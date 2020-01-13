from datetime import datetime, date
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import DeleteView
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum
from django.urls import reverse
from .models import Entry, Account, AccountBalance
from .forms import NewEntryForm, NewAccForm
from .utils import make_account_tree


def change_field(request):
    acc_pk = request.POST.get('acc_pk')
    acc_field = request.POST.get('acc_field')
    new_value = request.POST.get('value')
    update_params = {acc_field: new_value}
    Account.objects.filter(pk=acc_pk).update(**update_params)
    return HttpResponse('')


class MainView(CreateView):
    model = Entry
    template_name = 'financez/index.html'
    form_class = NewEntryForm
    success_url = 'main_book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now()
        context['current_month'] = today
        # entries per month
        context['entries'] = (
            Entry.objects
            .order_by('-date')
            .filter(date__year=today.year, date__month=today.month)
            .values('date', 'acc_dr__name', 'acc_cr__name', 'total', 'comment', 'currency__name')
        )
        # accounts
        context['account_list'] = make_account_tree()
        # results
        context['results_queryset'] = (
            AccountBalance.objects
            .filter(
                Q(acc__results=Account.RESULT_ASSETS) |
                Q(acc__results=Account.RESULT_PLANS) |
                Q(acc__results=Account.RESULT_DEBTS),
                acc__child=None)
            .values('acc__name', 'acc__results', 'total', 'acc__parent').order_by('acc__order')
        )
        # results by groups
        context['results_grouped_queryset'] = (
            AccountBalance.objects.filter(
                Q(acc__results=Account.RESULT_ASSETS) |
                Q(acc__results=Account.RESULT_PLANS) |
                Q(acc__results=Account.RESULT_DEBTS)
            ).exclude(acc__parent=None).values('acc__parent__name', 'acc__parent__results').annotate(total=Sum('total'))
        )
        # results by month
        incomes_sum = Entry.objects.filter(
            date__year=today.year, date__month=today.month, acc_cr__results=Account.RESULT_INCOMES
        ).values('total').aggregate(sum=Sum('total'))['sum'] or 0
        expenses_sum = Entry.objects.filter(
            date__year=today.year, date__month=today.month, acc_dr__results=Account.RESULT_EXPENSES
        ).values('total').aggregate(sum=Sum('total'))['sum'] or 0
        context['incomes_sum'] = incomes_sum
        context['expenses_sum'] = expenses_sum
        context['month_result'] = incomes_sum - expenses_sum
        context['result_types'] = {
            'assets': Account.RESULT_ASSETS,
            'debts': Account.RESULT_DEBTS,
            'plans': Account.RESULT_PLANS,
            'incomes': Account.RESULT_INCOMES,
            'expenses': Account.RESULT_EXPENSES
        }
        return context


class ReportsView(TemplateView):
    template_name = 'financez/reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        today = datetime.now()
        context['period_from'] = date(today.year, 1, 1).strftime("%Y-%m-%d")
        context['period_to'] = today.strftime("%Y-%m-%d")
        return context


class ReportDataView(View):

    def calculate_results(self, results, entries, group_by_parent):
        for entr in entries:
            group_date = f'{entr.date.year}.{entr.date.month}'
            if entr.acc_dr.results == Account.RESULT_EXPENSES:
                acc_name = (
                    f'exp:{entr.acc_dr.parent.name}'
                    if group_by_parent
                    else f'exp:{entr.acc_dr.parent.name}:{entr.acc_dr.name}'
                )
            else:
                acc_name = f'inc:{entr.acc_cr.name}'
            group_dict = next((item for item in results if item['group_date'] == group_date), None)
            if group_dict:
                group_dict[acc_name] = entr.total + group_dict.get(acc_name, 0)
            else:
                results.append({'group_date': group_date, acc_name: entr.total})

    def get(self, request, *args, **kwargs):
        today = datetime.now()
        group_by_parent = True
        period_from = request.GET.get('period-from', date(today.year, 1, 1))
        period_to = request.GET.get('period-to', today)
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        qs_exp = (
            Entry.objects
            .filter(date__gte=period_from, date__lte=period_to, acc_dr__results=Account.RESULT_EXPENSES)
            .select_related('acc_dr', 'acc_dr__parent')
            .order_by('date')
        )
        qs_inc = (
            Entry.objects
            .filter(date__gte=period_from, date__lte=period_to, acc_cr__results=Account.RESULT_INCOMES)
            .select_related('acc_cr', 'acc_cr__parent')
            .order_by('date')
        )
        results = []
        self.calculate_results(results, qs_exp, group_by_parent)
        self.calculate_results(results, qs_inc, group_by_parent)
        inc_accounts = [
            f'inc:{acc["name"]}' for acc in
            Account.objects.filter(results=Account.RESULT_INCOMES).values('name')
        ]
        if group_by_parent:
            exp_accounts = [
                f'exp:{acc["name"]}' for acc in
                Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None).order_by('order').values('name')
            ]
        else:
            exp_accounts = [
                f'exp:{acc["parent__name"]}:{acc["name"]}' for acc in
                Account.objects.filter(results=Account.RESULT_EXPENSES).values('name', 'parent__name').distinct()
            ]
        return JsonResponse(
            {
                'accounts_incomes': inc_accounts,
                'accounts_expenses': exp_accounts,
                'results': results,
            },
            safe=False
        )


class SettingsView(TemplateView):
    template_name = 'financez/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = kwargs.get('section')
        context['account_list'] = make_account_tree(section)
        context['available_parents'] = Account.objects.filter(results=section, parent=None).values('pk', 'name')
        context['new_acc_form'] = NewAccForm(section=section)
        context['sections'] = {
            'assets': Account.RESULT_ASSETS,
            'plans': Account.RESULT_PLANS,
            'debts': Account.RESULT_DEBTS,
            'incomes': Account.RESULT_INCOMES,
            'expenses': Account.RESULT_EXPENSES,
        }
        return context


class NewAccView(CreateView):
    model = Account
    form_class = NewAccForm

    def get_success_url(self, **kwargs):
        return reverse('settings', args=(self.request.POST.get('results'), ))


class DelAccView(DeleteView):
    model = Account

    def get_success_url(self, **kwargs):
        return reverse('settings', args=(self.request.POST.get('section'), ))

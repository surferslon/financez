from datetime import datetime, date, timedelta
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import DeleteView
from django.template.response import TemplateResponse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F, Sum
from django.urls import reverse
from .models import Entry, Account, AccountBalance, Currency
from .forms import NewEntryForm, NewAccForm, NewCurForm
from .utils import make_account_tree


def change_field(request):
    acc_pk = request.POST.get('acc_pk')
    acc_field = request.POST.get('acc_field')
    new_value = request.POST.get('value')
    update_params = {acc_field: new_value}
    Account.objects.filter(pk=acc_pk).update(**update_params)
    return HttpResponse('')


def change_currency(request):
    currency = Currency.objects.get(user=request.user, pk=request.POST.get('cur_pk'))
    currency.selected = True
    currency.save()
    return HttpResponse('')


class EntriesView(CreateView):
    model = Entry
    template_name = 'financez/index.html'
    form_class = NewEntryForm
    success_url = '/entries'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now()
        user = self.request.user
        context['result_types'] = {
            'assets': Account.RESULT_ASSETS,
            'debts': Account.RESULT_DEBTS,
            'plans': Account.RESULT_PLANS,
            'incomes': Account.RESULT_INCOMES,
            'expenses': Account.RESULT_EXPENSES
        }
        context['form'].fields['currency'].queryset = Currency.objects.filter(user=user)
        try:
            currency = Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            currency = None
        context['current_month'] = today
        # entries per month
        context['entries'] = (
            Entry.objects
            .order_by('-date')
            .filter(date__year=today.year, date__month=today.month, currency=currency, user=user)
            .values('date', 'acc_dr__name', 'acc_cr__name', 'total', 'comment', 'currency__name')
        )
        # accounts
        context['account_list'] = make_account_tree(user)
        return context


class MainView(TemplateView):
    template_name = 'financez/reports.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        today = datetime.now()
        context['period_from'] = date(today.year, 1, 1).strftime("%Y-%m-%d")
        context['period_to'] = today.strftime("%Y-%m-%d")
        context['current_month'] = today
        # results
        user = self.request.user
        try:
            currency = Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            currency = None
        context['results_queryset'] = (
            AccountBalance.objects
            .filter(
                Q(acc__results=Account.RESULT_ASSETS) |
                Q(acc__results=Account.RESULT_PLANS) |
                Q(acc__results=Account.RESULT_DEBTS),
                currency=currency, acc__user=user)
            .exclude(total=0)
            .values('acc__name', 'acc__results', 'total', 'acc__parent__name', 'acc__parent__order')
            .order_by('acc__order')
        )
        # results by month
        incomes_sum = Entry.objects.filter(
            date__year=today.year, date__month=today.month, user=user,
            acc_cr__results=Account.RESULT_INCOMES, currency=currency
        ).values('total').aggregate(sum=Sum('total'))['sum'] or 0
        expenses_sum = Entry.objects.filter(
            date__year=today.year, date__month=today.month, user=user,
            acc_dr__results=Account.RESULT_EXPENSES, currency=currency
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


class ReportDataView(View):

    def calculate_results(self, results, entries, group_by_parent, group_all):
        for entr in entries:
            if group_all:
                group_date = 'Total'
            else:
                group_date = f'{entr.date.year}.{entr.date.month}'
            if entr.acc_dr.results == Account.RESULT_EXPENSES:
                if group_by_parent:
                    acc_name = (
                        f'exp:{entr.acc_dr.parent.name}'
                        if entr.acc_dr.parent
                        else f'exp:{entr.acc_dr.name}'
                    )
                else:
                    acc_name = (
                        f'exp:{entr.acc_dr.parent.name}:{entr.acc_dr.name}'
                        if entr.acc_dr.parent
                        else f'exp:{entr.acc_dr.name}'
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
        group_all = True if request.GET.get('group_all') == "true" else False
        period_from = request.GET.get('period-from', date(today.year, 1, 1))
        period_to = request.GET.get('period-to', today)
        user = request.user
        try:
            currency = Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            currency = None
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        qs_exp = (
            Entry.objects
            .filter(date__gte=period_from, date__lte=period_to, user=user,
                    acc_dr__results=Account.RESULT_EXPENSES, currency=currency)
            .select_related('acc_dr', 'acc_dr__parent')
            .order_by('date')
        )
        qs_inc = (
            Entry.objects
            .filter(date__gte=period_from, date__lte=period_to, user=user,
                    acc_cr__results=Account.RESULT_INCOMES, currency=currency)
            .select_related('acc_cr', 'acc_cr__parent')
            .order_by('date')
        )
        results = []
        self.calculate_results(results, qs_exp, group_by_parent, group_all)
        self.calculate_results(results, qs_inc, group_by_parent, group_all)
        inc_accounts = [
            f'inc:{acc["name"]}' for acc in
            Account.objects.filter(results=Account.RESULT_INCOMES, user=user).values('name')
        ]
        if group_by_parent:
            exp_accounts = [
                f'exp:{acc["name"]}' for acc in
                Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None, user=user).order_by('order').values('name')
            ]
        else:
            exp_accounts = [
                f'exp:{acc["parent__name"]}:{acc["name"]}' for acc in
                Account.objects.filter(results=Account.RESULT_EXPENSES, user=user).values('name', 'parent__name').distinct()
            ]
        return JsonResponse(
            {
                'accounts_incomes': inc_accounts,
                'accounts_expenses': exp_accounts,
                'results': results,
            },
            safe=False
        )


class ReportDetailsView(View):

    def get(self, request, *args, **kwargs):
        category = request.GET.get('category')
        results, category = category.split(':')
        try:
            parent_acc = Account.objects.get(name=category, results=results)
        except Account.DoesNotExist:
            parent_acc = Account.objects.get(name__contains=category, results=results)
        today = datetime.now()
        period_from = request.GET.get('period-from', date(today.year, 1, 1))
        period_to = request.GET.get('period-to', today)
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        params = {
            'currency': Currency.objects.get(user=request.user, selected=True),
            'user': request.user,
            'date__gte': period_from,
            'date__lte': period_to
        }
        if results == 'exp':
            qs = Entry.objects.filter(
                Q(acc_dr__parent=parent_acc) | Q(acc_dr=parent_acc), **params
            ).annotate(acc_name=F('acc_dr__name'), acc_id=F('acc_dr__id'))
        else:
            qs = Entry.objects.filter(
                Q(acc_cr__parent=parent_acc) | Q(acc_cr=parent_acc), **params
            ).annotate(acc_name=F('acc_cr__name'), acc_id=F('acc_cr__id'))
        results = []
        accounts = []
        group = True if request.GET.get('group_details') == 'true' else False
        iter_date = period_from
        while iter_date < period_to:
            if group:
                group_date = 'Total'
            else:
                group_date = f'{iter_date.year}.{iter_date.month}'
            group_dict = next((item for item in results if item['group_date'] == group_date), None)
            if not group_dict:
                results.append({'group_date': group_date})
            if iter_date.month + 1 > 12:
                iter_date = iter_date.replace(year=iter_date.year + 1, month=1, day=1)
            else:
                iter_date = iter_date.replace(month=iter_date.month + 1, day=1)
        for entry in qs:
            if group:
                group_date = 'Total'
            else:
                group_date = f'{entry.date.year}.{entry.date.month}'
            group_dict = next((item for item in results if item['group_date'] == group_date), None)
            group_dict[entry.acc_id] = entry.total + group_dict.get(entry.acc_id, 0)
            if entry.acc_id not in accounts:
                accounts.append(entry.acc_id)
        accounts = [{'valueField': acc.id, 'name': acc.name} for acc in Account.objects.filter(id__in=accounts)]
        return JsonResponse({'title': parent_acc.name, 'results': results, 'accounts': accounts}, safe=False)


class ReportEntriesView(View):

    def get(self, request, *args, **kwargs):
        acc_id = request.GET.get('acc_id')
        acc = Account.objects.get(id=acc_id)
        today = datetime.now()
        month = request.GET.get('month', None)
        params = {
            'currency': Currency.objects.get(user=request.user, selected=True),
            'user': request.user,
        }
        if month:
            year, month = month.split('.')
            params['date__gte'] = date(year=int(year), month=int(month), day=1)
            if int(month) + 1 > 12:
                params['date__lte'] = date(year=int(year) + 1, month=1, day=1) - timedelta(days=1)
            else:
                params['date__lte'] = date(year=int(year), month=int(month) + 1, day=1) - timedelta(days=1)
        else:
            period_from = request.GET.get('period-from', date(today.year, 1, 1))
            period_to = request.GET.get('period-to', today)
            if isinstance(period_from, str):
                period_from = datetime.strptime(period_from, "%Y-%m-%d")
            if isinstance(period_to, str):
                period_to = datetime.strptime(period_to, "%Y-%m-%d")
            params['date__gte'] = period_from
            params['date__lte'] = period_to
        qs = Entry.objects.filter(Q(acc_cr=acc) | Q(acc_dr=acc), **params).order_by('-date')
        return TemplateResponse(
            request,
            'financez/report_entries.html',
            {
                'entries': qs,
                'total_sum': qs.aggregate(Sum('total'))['total__sum']
            }
        )


class SettingsView(TemplateView):
    template_name = 'financez/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = kwargs.get('section')
        user = self.request.user
        if section == 'general':
            context['currencies'] = Currency.objects.filter(user=user)
            context['new_cur_form'] = NewCurForm
        context['account_list'] = make_account_tree(user, section)
        context['available_parents'] = (
            Account.objects.filter(results=section, parent=None, user=user).values('pk', 'name')
        )
        context['new_acc_form'] = NewAccForm(section=section, user=user)
        context['sections'] = {
            'general': 'general',
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

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('settings', args=(self.request.POST.get('results'), ))


class NewCurView(CreateView):
    model = Currency
    form_class = NewCurForm

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        if not Currency.objects.filter(user=user).exists():
            form.instance.selected = True
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('settings', args=('general', ))


class DelAccView(DeleteView):
    model = Account

    def get_success_url(self, **kwargs):
        return reverse('settings', args=(self.request.POST.get('section'), ))

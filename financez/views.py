from datetime import datetime, date
from django.views.generic import CreateView, TemplateView
from django.http import JsonResponse
from django.db.models import Q, Sum
from .models import Entry, Account, AccountBalance
from .forms import NewEntryForm
from .utils import make_account_tree


def report_data(request):
    today = datetime.now()
    period_from = request.GET.get('period-from')
    period_to = request.GET.get('period-to')
    if not period_from or not period_to:
        period_from = date(today.year, 1, 1)
        period_to = today
    else:
        period_from = datetime.strptime(period_from, "%Y-%m-%d")
        period_to = datetime.strptime(period_to, "%Y-%m-%d")

    group_by_parent = True

    qs_exp = (
        Entry.objects
        .filter(date__gte=period_from, date__lte=period_to, acc_dr__results=Account.RESULT_EXPENSES)
        .select_related('acc_dr', 'acc_dr__parent')
        .order_by('date')
    )
    qs_inc = (
        Entry.objects
        .filter(date__gt=period_from, date__lt=period_to, acc_cr__results=Account.RESULT_INCOMES)
        .select_related('acc_cr', 'acc_cr__parent')
        .order_by('date')
    )
    results = []
    for entr in qs_exp:
        group_date = '{}.{}'.format(entr.date.year, entr.date.month)
        acc_name = 'exp:{}'.format(entr.acc_dr.parent.name) if group_by_parent else 'exp:{}:{}'.format(entr.acc_dr.parent.name, entr.acc_dr.name)
        group_dict = next((item for item in results if item['group_date'] == group_date), None)
        if group_dict:
            group_dict[acc_name] = entr.total + group_dict.get(acc_name, 0)
        else:
            results.append({'group_date': group_date, acc_name: entr.total})
    for entr in qs_inc:
        group_date = '{}.{}'.format(entr.date.year, entr.date.month)
        acc_name = 'inc:{}'.format(entr.acc_cr.name)
        group_dict = next((item for item in results if item['group_date'] == group_date), None)
        if group_dict:
            group_dict[acc_name] = entr.total + group_dict.get(acc_name, 0)
        else:
            results.append({'group_date': group_date, acc_name: entr.total})
    if group_by_parent:
        exp_accounts = [
            'exp:{}'.format(acc['parent__name']) for acc in
            Account.objects.filter(results=Account.RESULT_EXPENSES).order_by('parent__order').values('parent__name').distinct()
        ]
    else:
        exp_accounts = [
            'exp:{}:{}'.format(acc['parent__name'], acc['name']) for acc in
            Account.objects.filter(results=Account.RESULT_EXPENSES).values('name', 'parent__name').distinct()
        ]
    response = {
        'accounts_incomes': [
            'inc:{}'.format(acc['name']) for acc in
            Account.objects.filter(results=Account.RESULT_INCOMES).values('name')
        ],
        'accounts_expenses': exp_accounts,
        'results': results,
    }
    return JsonResponse(response, safe=False)


class MainView(CreateView):
    model = Entry
    template_name = 'financez/index.html'
    form_class = NewEntryForm
    success_url = '/'

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
                Q(acc__results=Account.RESULT_DEBTS))
            .values('acc__name', 'acc__results', 'total')
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
            'plans': Account.RESULT_PLANS
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


class SettingsView(TemplateView):
    template_name = 'financez/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_list'] = make_account_tree()
        return context

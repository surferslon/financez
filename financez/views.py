from datetime import datetime
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum
from django.db.models import Func
from django.db import models
from django.core.paginator import Paginator
from .models import Entry, Account, AccountBalance
from .forms import NewEntryForm
from itertools import groupby


def report_data(request):
    today = datetime.now()
    qs_exp = (
        Entry.objects
        .filter(date__year=today.year, acc_dr__results=Account.RESULT_EXPENSES)
        .select_related('acc_dr', 'acc_dr__parent')
        .order_by('date')
    )
    qs_inc = (
        Entry.objects
        .filter(date__year=today.year, acc_cr__results=Account.RESULT_INCOMES)
        .select_related('acc_cr', 'acc_cr__parent')
        .order_by('date')
    )
    results = []
    for entr in qs_exp:
        group_date = '{}.{}'.format(entr.date.year, entr.date.month)
        acc_name = '{}:{}'.format(entr.acc_dr.parent.name, entr.acc_dr.name)
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
    response = {
        'accounts_incomes': [
            acc['name'] for acc in
            Account.objects.filter(results=Account.RESULT_INCOMES).values('name')
        ],
        'accounts_expenses': [
            '{}:{}'.format(acc.parent.name, acc.name) for acc in
            Account.objects.filter(results=Account.RESULT_EXPENSES).select_related('parent')
        ],
        'results': results,
    }
    return JsonResponse(response, safe=False)


class MainView(CreateView):
    model = Entry
    template_name = 'financez/index.html'
    form_class = NewEntryForm
    success_url = '/'

    def add_subaccounts(self, acc_list, filtered_list):
        result_tree = []
        for acc in filtered_list:
            parent_id = acc['id']
            subaccounts = list(filter(lambda x: x['parent_id'] == parent_id, acc_list))
            if subaccounts:
                acc['subaccs'] = subaccounts
                for subacc in subaccounts:
                    subacc['subaccs'] = self.add_subaccounts(
                        acc_list,
                        filter(lambda x: x['parent_id'] == subacc['id'], acc_list)
                    )
            result_tree.append(acc)
        return result_tree

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now()
        context['current_month'] = today
        # entries per month
        context['entries'] = (
            Entry.objects
            .order_by('-date')
            .select_related('acc_dr', 'acc_cr', 'currency')
            .filter(date__year=today.year, date__month=today.month)
        )
        # accounts
        accounts = Account.objects.all().values('id', 'parent_id', 'name')
        acc_list = [acc for acc in accounts]
        context['account_list'] = self.add_subaccounts(acc_list, filter(lambda x: x['parent_id'] is None, acc_list))
        # results
        results_accounts = ['Main', 'Savings']
        results_data = AccountBalance.objects.filter(acc__name__in=results_accounts)
        debts_accounts = AccountBalance.objects.filter(acc__parent__code='01.03').aggregate(sum=Sum('total'))
        context['assets_sum'] = results_data.get(acc__name='Main').total
        context['savings_sum'] = results_data.get(acc__name='Savings').total
        context['debts_sum'] = debts_accounts['sum']
        # planning
        planning_data = AccountBalance.objects.filter(acc__parent__code='02')
        context['planning_food'] = planning_data.get(acc__name='Food').total
        context['planning_transport'] = planning_data.get(acc__name='Transport').total
        context['planning_payments'] = planning_data.get(acc__name='Payments').total
        context['planning_unscheduled'] = planning_data.get(acc__name='Unscheduled').total
        # debts
        context['debts_queryset'] = AccountBalance.objects.filter(total__lt=0.0, acc__parent__code__in=['03', '03.01'])
        # results by month
        incomes_sum = Entry.objects.filter(
            date__year=today.year, date__month=today.month,
            acc_cr__results=Account.RESULT_INCOMES
        ).aggregate(sum=Sum('total'))['sum']
        expenses_sum = Entry.objects.filter(
            date__year=today.year, date__month=today.month,
            acc_dr__results=Account.RESULT_EXPENSES
        ).aggregate(sum=Sum('total'))['sum']
        context['incomes_sum'] = incomes_sum
        context['expenses_sum'] = expenses_sum
        context['month_result'] = incomes_sum - expenses_sum
        return context


class ReportsView(TemplateView):
    template_name = 'financez/reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        return context


class SettingsView(TemplateView):
    template_name = 'financez/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

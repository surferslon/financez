from decimal import Decimal
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Entry, Account, AccountBalance, Currency


class EntryModelTests(TestCase):

    def test_balance_updating(self):
        currency = Currency.objects.create(name='rub')
        acc_ast = Account.objects.create(name='assets', results=Account.RESULT_ASSETS)
        acc_inc = Account.objects.create(name='incomes', results=Account.RESULT_INCOMES)
        first_sum = Decimal('12.321')
        second_sum = Decimal('11.456')
        Entry.objects.create(date=timezone.now(), acc_dr=acc_ast, acc_cr=acc_inc, total=first_sum, currency=currency)
        acc_ast_balance = AccountBalance.objects.get(acc=acc_ast)
        acc_inc_balance = AccountBalance.objects.get(acc=acc_inc)
        self.assertEqual(acc_ast_balance.total, first_sum)
        self.assertEqual(acc_inc_balance.total, -1 * first_sum)
        Entry.objects.create(date=timezone.now(), acc_dr=acc_ast, acc_cr=acc_inc, total=second_sum, currency=currency)
        acc_ast_balance = AccountBalance.objects.get(acc=acc_ast)
        acc_inc_balance = AccountBalance.objects.get(acc=acc_inc)
        self.assertEqual(acc_ast_balance.total, first_sum + second_sum)
        self.assertEqual(acc_inc_balance.total, -1 * (first_sum + second_sum))


class ReportViewTests(TestCase):

    def test_results_by_parent(self):
        currency = Currency.objects.create(name='rub')
        acc_ast = Account.objects.create(name='assets', results=Account.RESULT_ASSETS)
        acc_inc = Account.objects.create(name='incomes', results=Account.RESULT_INCOMES)
        acc_exp_parent = Account.objects.create(name='expenses_parent', results=Account.RESULT_EXPENSES)
        acc_exp_subacc1 = Account.objects.create(name='expenses_subacc1', results=Account.RESULT_EXPENSES, parent=acc_exp_parent)
        acc_exp_subacc2 = Account.objects.create(name='expenses_subacc2', results=Account.RESULT_EXPENSES, parent=acc_exp_parent)
        sum_inc = Decimal('52.321')
        sum_exp1 = Decimal('11.456')
        sum_exp2 = Decimal('5.123')
        entry_date = timezone.now()
        Entry.objects.create(date=entry_date, acc_dr=acc_ast, acc_cr=acc_inc, total=sum_inc, currency=currency)
        Entry.objects.create(date=entry_date, acc_dr=acc_exp_subacc1, acc_cr=acc_ast, total=sum_exp1, currency=currency)
        Entry.objects.create(date=entry_date, acc_dr=acc_exp_subacc2, acc_cr=acc_ast, total=sum_exp2, currency=currency)
        response = self.client.get(reverse('report_data'))
        results_by_parent = response.json()['results'][0]
        # expenses
        self.assertEqual(Decimal(str(results_by_parent['exp:expenses_parent'])), sum_exp1 + sum_exp2)
        # incomes
        self.assertEqual(Decimal(str(results_by_parent['inc:incomes'])), sum_inc)

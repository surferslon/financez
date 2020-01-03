from django.db import models
from django.db.models import Sum


class Currency(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Account(models.Model):
    TYPE_ACTIVE = 'a'
    TYPE_PASSIVE = 'p'
    RESULT_ASSETS = 'ast'
    RESULT_INCOMES = 'inc'
    RESULT_EXPENSES = 'exp'
    RESULT_DEBTS = 'dbt'
    RESULT_PLANS = 'pln'
    ACC_TYPES = (
        (TYPE_ACTIVE, 'active'),
        (TYPE_PASSIVE, 'passive'),
    )
    RESULT_TYPES = (
        (RESULT_ASSETS, 'assets'),
        (RESULT_INCOMES, 'incomes'),
        (RESULT_EXPENSES, 'expenses'),
        (RESULT_DEBTS, 'debts'),
        (RESULT_PLANS, 'planning'),
    )
    name = models.CharField(max_length=255)
    order = models.CharField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', related_name='child', on_delete=models.CASCADE, null=True, blank=True)
    acc_type = models.CharField(max_length=1, choices=ACC_TYPES, default=TYPE_ACTIVE)
    results = models.CharField(max_length=3, choices=RESULT_TYPES, null=True, blank=True)

    def __str__(self):
        return self.name
        # return '{}: {}'.format(self.parent.name, self.name) if self.parent else self.name

    @property
    def full_name(self):
        parents = []
        parent = self.parent
        while parent:
            parents.insert(0, parent.name)
            parent = parent.parent
        return '{}/{}'.format('/'.join(parents), self.name)


class Entry(models.Model):
    date = models.DateField()
    acc_dr = models.ForeignKey(Account, related_name='acc_dr', on_delete=models.CASCADE)
    acc_cr = models.ForeignKey(Account, related_name='acc_cr', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    comment = models.CharField(max_length=1024, default='', blank=True)

    class Meta:
        verbose_name_plural = 'Entries'

    def __str__(self):
        return '{} {} {} {}'.format(self.date, self.acc_dr.name, self.acc_cr.name, self.total)

    def update_turnovers_and_balance(self, acc):
        # turnovers
        turnover, new = AccountTurnover.objects.get_or_create(
            date=self.date, acc=acc, currency=self.currency, entry=self)
        if acc == self.acc_dr:
            turnover.total_dr = self.total
        else:
            turnover.total_cr = self.total
        turnover.save()
        # balance
        balance, new = AccountBalance.objects.get_or_create(acc=acc, currency=self.currency)
        incomes = Entry.objects.filter(acc_dr=acc).aggregate(sum=Sum('total'))
        expenses = Entry.objects.filter(acc_cr=acc).aggregate(sum=Sum('total'))
        balance.total = (incomes['sum'] or 0) - (expenses['sum'] or 0)
        balance.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_turnovers_and_balance(self.acc_dr)
        self.update_turnovers_and_balance(self.acc_cr)


class AccountBalance(models.Model):
    acc = models.ForeignKey(Account, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {}'.format(self.acc.name, self.total)


class AccountTurnover(models.Model):
    date = models.DateField()
    acc = models.ForeignKey(Account, on_delete=models.CASCADE)
    total_dr = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)
    total_cr = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

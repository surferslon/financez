from django.db import models


class Account(models.Model):
    ACC_TYPES = (
        ('a', 'active'),
        ('p', 'passive'),
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True)
    acc_type = models.CharField(max_length=1, default='a', choices=ACC_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        # return self.name
        return '{}: {}'.format(self.parent.name, self.name) if self.parent else self.name

    @property
    def full_name(self):
        parents = []
        parent = self.parent
        while parent:
            parents.insert(0, parent.name)
            parent = parent.parent
        return '{}/{}'.format('/'.join(parents), self.name)


class Currency(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Entry(models.Model):
    date = models.DateField()
    acc_dr = models.ForeignKey(Account, related_name='acc_dr', on_delete=models.CASCADE)
    acc_cr = models.ForeignKey(Account, related_name='acc_cr', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    comment = models.CharField(max_length=1024)

    class Meta:
        verbose_name_plural = 'Entries'

    def __str__(self):
        return '{} {} {} {}'.format(self.date, self.acc_dr.name, self.acc_cr.name, self.total)

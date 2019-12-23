from django.db import models


class Account(models.Model):
    ACC_TYPES = (
        ('a', 'active'),
        ('p', 'passive'),
    )
    name = models.CharField(max_length=255)
    code = models.IntegerField(blank=True, null=True)
    acc_type = models.CharField(max_length=1, default='a', choices=ACC_TYPES)

    def __str__(self):
        return self.name


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

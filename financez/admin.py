from django.contrib import admin
from .models import Entry, Account, Currency, AccountBalance, AccountTurnover

admin.site.register(Entry)
admin.site.register(Account)
admin.site.register(Currency)
admin.site.register(AccountBalance)
admin.site.register(AccountTurnover)

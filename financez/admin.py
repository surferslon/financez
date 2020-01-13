from django.contrib import admin
from .models import Entry, Account, Currency, AccountBalance

admin.site.register(Entry)
admin.site.register(Account)
admin.site.register(Currency)
admin.site.register(AccountBalance)

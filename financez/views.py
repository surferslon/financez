from django.views.generic import CreateView
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from .models import Entry, Account
from .forms import NewEntryForm


class MainView(CreateView):
    model = Entry
    template_name = 'financez/index.html'
    form_class = NewEntryForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        paginator = Paginator(Entry.objects.all().order_by('-date'), 500)

        context['entries'] = paginator.get_page(page)
        context['pages'] = paginator.page_range
        context['accounts_assets'] = Account.objects.filter(parent__name='Assets')
        context['accounts_planning'] = Account.objects.filter(parent__name='Planning')
        context['accounts_incomes'] = Account.objects.filter(parent__name='Incomes')
        context['accounts_expenses'] = Account.objects.filter(parent__name='Expenses')
        assets_account = Account.objects.get(code='01.01')
        savings_account = Account.objects.get(code='01.02')
        assets_sum_dr = Entry.objects.filter(acc_dr=assets_account).aggregate(sum=Sum('total'))
        assets_sum_cr = Entry.objects.filter(acc_cr=assets_account).aggregate(sum=Sum('total'))
        assets_sum = assets_sum_dr['sum'] - assets_sum_cr['sum']
        savings_sum_dr = Entry.objects.filter(acc_dr=savings_account).aggregate(sum=Sum('total'))
        savings_sum_cr = Entry.objects.filter(acc_cr=savings_account).aggregate(sum=Sum('total'))
        savings_sum = savings_sum_dr['sum'] - savings_sum_cr['sum']
        context['assets_sum'] = assets_sum
        context['savings_sum'] = savings_sum

        return context

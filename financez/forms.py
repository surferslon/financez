from django import forms
from django.utils import timezone
from .models import Entry, Account, Currency


class DateInput(forms.DateInput):
    input_type = 'date'


class NewEntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ['date', 'acc_dr', 'acc_cr', 'total', 'currency', 'comment']
        widgets = {
            'date': DateInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['acc_dr'].widget.attrs.update({'hidden': ''})
        self.fields['acc_cr'].widget.attrs.update({'hidden': ''})
        self.fields['date'].initial = timezone.now()


class NewCurForm(forms.ModelForm):

    class Meta:
        model = Currency
        fields = ['name']


class NewAccForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'acc_type', 'results', 'order', 'parent']

    def __init__(self, *args, **kwargs):
        section = kwargs.pop('section', None)
        super().__init__(*args, **kwargs)
        if not section:
            return
        self.fields['parent'].queryset = Account.objects.filter(results=section, parent=None)
        self.fields['results'].initial = section
        if section in (Account.RESULT_ASSETS, Account.RESULT_PLANS, Account.RESULT_EXPENSES):
            self.fields['acc_type'].initial = Account.TYPE_ACTIVE
        else:
            self.fields['acc_type'].initial = Account.TYPE_PASSIVE

from datetime import datetime
from django import forms
from .models import Entry, Account


class DateInput(forms.DateInput):
    input_type = 'date'


class NewEntryForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), initial=datetime.now())

    class Meta:
        model = Entry
        fields = ['date', 'acc_dr', 'acc_cr', 'total', 'currency', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['acc_dr'].widget.attrs.update({'hidden': ''})
        self.fields['acc_cr'].widget.attrs.update({'hidden': ''})


class NewAccForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'acc_type', 'results', 'order', 'parent']

    def __init__(self, *args, **kwargs):
        try:
            section = kwargs.pop('section')
        except KeyError:
            section = None
        super().__init__(*args, **kwargs)
        if not section:
            return
        self.fields['parent'].queryset = Account.objects.filter(results=section, parent=None)
        self.fields['results'].initial = section
        self.fields['acc_type'].initial = (
            Account.TYPE_ACTIVE if section in (Account.RESULT_ASSETS, Account.RESULT_PLANS, Account.RESULT_EXPENSES)
            else Account.TYPE_PASSIVE
        )

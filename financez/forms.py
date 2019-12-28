from datetime import datetime
from django import forms
from .models import Entry


class DateInput(forms.DateInput):
    input_type = 'date'


class NewEntryForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), initial=datetime.now())

    class Meta:
        model = Entry
        fields = ['date', 'acc_dr', 'acc_cr', 'total', 'currency', 'comment']

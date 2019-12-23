from django.views.generic import CreateView
from .models import Entry
from .forms import NewEntryForm


class MainView(CreateView):
    model = Entry
    template_name = 'financez/index.html'
    form_class = NewEntryForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['entries'] = Entry.objects.all()
        return context

from django.views.generic.edit import CreateView
from django.contrib.auth import login
from .forms import RegistrationForm


class RegistrationView(CreateView):
    template_name = 'registration/signup.html'
    form_class = RegistrationForm
    success_url = '/'

    def get_success_url(self, **kwargs):
        url = super(RegistrationView, self).get_success_url(**kwargs)
        login(self.request, self.object)
        return url

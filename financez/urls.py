from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(views.MainView.as_view()), name='main'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reg/', include('registration.urls')),

    path('entries/', login_required(views.EntriesView.as_view()), name='entries'),
    path('report_data/', login_required(views.ReportDataView.as_view()), name='report_data'),
    path('report_details/', login_required(views.ReportDetailsView.as_view()), name='report_details'),
    path('report_entries/', login_required(views.ReportEntriesView.as_view()), name='report_entries'),
    path('settings/<str:section>', login_required(views.SettingsView.as_view()), name='settings'),
    path('change_field', login_required(views.change_field), name='change_field'),
    path('newacc/', login_required(views.NewAccView.as_view()), name='new_acc'),
    path('newcur/', login_required(views.NewCurView.as_view()), name='new_cur'),
    path('changecur/', login_required(views.change_currency), name='change_cur'),
    path('delacc/<int:pk>', login_required(views.DelAccView.as_view()), name='del_acc'),
]

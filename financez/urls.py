from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(views.MainView.as_view()), name='main_book'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reg/', include('registration.urls')),

    path('reports/', login_required(views.ReportsView.as_view()), name='reports'),
    path('report_data/', login_required(views.ReportDataView.as_view()), name='report_data'),
    path('settings/<str:section>', login_required(views.SettingsView.as_view()), name='settings'),
    path('change_field', login_required(views.change_field), name='change_field'),
    path('newacc/', login_required(views.NewAccView.as_view()), name='new_acc'),
    path('newcur/', login_required(views.NewCurView.as_view()), name='new_cur'),
    path('changecur/', login_required(views.change_currency), name='change_cur'),
    path('delacc/<int:pk>', login_required(views.DelAccView.as_view()), name='del_acc'),
]

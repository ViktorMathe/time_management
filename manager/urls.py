from django.urls import include, path
from . import views

urlpatterns = [
    path('reg_business/', views.business_register, name='business_reg'),
    path('manager/', views.manager_site, name='manager'),
    path('loggedin/', views.loggedin),
    path('mgnt_clocking/', views.mgnt_clocking),
]
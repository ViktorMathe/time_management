from django.urls import include, path
from . import views

urlpatterns = [
    path('reg_business/', views.business_register, name='business_reg'),
    path('manager/', views.manager_site, name='manager'),
    path('loggedin/', views.loggedin),
    path('mgnt_clocking/', views.mgnt_clocking),
    path('approval/<employee_id>', views.approve_employee, name='approve'),
    path('send-manager-invitation/', views.send_manager_invitation, name='send_manager_invitation'),
    path('manager-registration/<int:company_id>', views.manager_registration, name='manager_registration'),
    path('delete-manager/<int:id>', views.delete_manager, name='delete_manager'),
    path('invitations/', views.invitations, name='invitations'),
    path('send-employee-invitation/', views.send_employee_invitation, name='send_employee_invitation'),
    path('employee-registration/<int:company_id>', views.employee_registration, name='employee_registration'),
    path('delete-employee/<int:id>', views.delete_employee, name='delete_employee'),
    path('invitations/accept-invite/<str:key>', views.AcceptInviteView.as_view(), name='custom_accept_invite'),
    path('delete-invitation/<int:invitation_id>/', views.delete_invitation, name='delete_invitation'),
]
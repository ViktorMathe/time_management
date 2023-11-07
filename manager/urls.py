from django.urls import include, path
from . import views

urlpatterns = [
    path('reg_business/', views.business_register, name='business_reg'),
    path('manager/', views.manager_site, name='manager'),
    path('loggedin/', views.loggedin),
    path('mgnt_clocking/', views.mgnt_clocking),
    path('approval/<employee_id>', views.approve_employee, name='approve'),
    path('send-invitation/', views.send_manager_invitation, name='send_manager_invitation'),
    path('manager-registration/<int:company_id>', views.custom_manager_registration, name='manager_registration'),
    path('invitations/', views.invitations, name='invitations'),
    path('invitations/accept-invite/<str:key>', views.AcceptInviteView.as_view(), name='custom_accept_invite'),
    path('delete-pending-invitation/<int:invitation_id>/', views.delete_pending_invitation, name='delete_pending_invitation'),
]
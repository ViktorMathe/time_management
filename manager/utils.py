from django.utils import timezone
from invitations.models import Invitation
from django.conf import settings

def is_invitation_expired(invitation):
    expiration_date = invitation.sent + timezone.timedelta(
        days=settings.INVITATIONS_INVITE_EXPIRE
    )
    return timezone.now() > expiration_date
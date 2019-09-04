from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _

from pretix.base.signals import logentry_display
from pretix.control.signals import nav_event


@receiver(nav_event, dispatch_uid="send_vouchers_nav")
def control_nav_import(sender, request=None, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(request.organizer, request.event, 'can_view_vouchers', request=request):
        return []
    return [
        {
            'label': _('Send out vouchers'),
            'url': reverse('plugins:pretix_send_vouchers:send', kwargs={
                'event': request.event.slug,
                'organizer': request.event.organizer.slug,
            }),
            'active': (url.namespace == 'plugins:send_vouchers' and url.url_name == 'send'),
            'icon': 'envelope',
            'children': []
        },
    ]


@receiver(signal=logentry_display)
def pretixcontrol_logentry_display(sender, logentry, **kwargs):
    plains = {
        'pretix.plugins.send_vouchers.sent': _('Email was sent'),
    }
    if logentry.action_type in plains:
        return plains[logentry.action_type]

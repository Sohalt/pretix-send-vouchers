from i18nfield.strings import LazyI18nString

from pretix.base.i18n import language
from pretix.base.models import Event, User
from pretix.base.services.mail import SendMailException, mail
from pretix.base.services.tasks import ProfiledEventTask
from pretix.celery_app import app

from .util import normalize_voucher_template, build_voucher_template_dict


@app.task(base=ProfiledEventTask)
def send_mails(event: Event, user: int, recipients: list, subject: dict, message: dict) -> None:
    failures = []
    user = User.objects.get(pk=user) if user else None
    subject = LazyI18nString(subject)
    message = LazyI18nString(message)

    for r in recipients:
        if isinstance(r,tuple):
            locale,email_address = r
        else:
            locale = None
            email_address = r
        try:
            with language(locale):
                #TODO less hacky
                subject = normalize_voucher_template(str(subject))
                message = normalize_voucher_template(str(message))
                vouchers = build_voucher_template_dict(event, subject+message, how_shared=email_address)
                subject = LazyI18nString(subject)
                message = LazyI18nString(message)
                email_context = {
                    'event': event,
                    'voucher': vouchers
                }
                mail(
                    email_address,
                    subject,
                    message,
                    email_context,
                    event,
                    locale=locale
                )
                event.log_action(
                    'pretix.plugins.pretix_send_vouchers.sent',
                    user=user,
                    data={
                        'subject': str(subject).format_map(email_context),
                        'message': str(message).format_map(email_context),
                        'recipient': email_address
                    }
                )
        except SendMailException:
            failures.append(email_address)

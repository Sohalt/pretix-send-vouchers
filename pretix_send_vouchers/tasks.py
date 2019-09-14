from i18nfield.strings import LazyI18nString

from pretix.base.i18n import language
from pretix.base.models import Event, User
from pretix.base.services.mail import SendMailException, mail
from pretix.base.services.tasks import ProfiledEventTask
from pretix.celery_app import app

from .util import normalize_voucher_template, build_voucher_template_dict


@app.task(base=ProfiledEventTask)
def send_mails(event: Event, user: int, recipients: list, vouchers: dict, subject: dict, message: dict) -> None:
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
                email_context = {
                    'event': event,
                    'voucher': vouchers[locale].pop()
                }
                mail(
                    email_address,
                    subject,
                    message,
                    email_context,
                    event,
                    locale=locale
                )
        except SendMailException:
            failures.append(email_address)

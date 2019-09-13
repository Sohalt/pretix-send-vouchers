import logging
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from pretix.base.i18n import language
from pretix.base.templatetags.rich_text import markdown_compile_email
from pretix.control.permissions import EventPermissionRequiredMixin
from pretix.multidomain.urlreverse import build_absolute_uri

from i18nfield.strings import LazyI18nString

from .forms import MailForm
from .tasks import send_mails
from .util import normalize_voucher_template, build_voucher_template_dict, NoMatchingVoucher

logger = logging.getLogger('pretix.plugins.send-vouchers')


class SenderView(EventPermissionRequiredMixin, FormView):
    template_name = 'pretix_send_vouchers/send_form.html'
    form_class = MailForm
    permission = 'can_view_vouchers'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.request.event
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, _('We could not send the email. See below for details.'))
        return super().form_invalid(form)

    def form_valid(self, form):
        self.output = {}

        recipients = form.cleaned_data.get('recipients')

        if not recipients:
            messages.error(self.request, _('You have not provided any recipients.'))
            return self.get(self.request, *self.args, **self.kwargs)

        # normalize voucher templates in subject and message
        i18n_subject = {}
        i18n_message = {}
        for l in self.request.event.settings.locales:
            with language(l):
                i18n_subject[l] = normalize_voucher_template(str(form.cleaned_data['subject']))
                i18n_message[l] = normalize_voucher_template(str(form.cleaned_data['message']))
        subject = LazyI18nString(i18n_subject)
        message = LazyI18nString(i18n_message)

        # generate preview
        if self.request.POST.get("action") == "preview":
            for l in self.request.event.settings.locales:
                with language(l):
                    try:
                        vouchers = build_voucher_template_dict(self.request.event, str(subject)+str(message))
                    except NoMatchingVoucher:
                        messages.error(self.request, _('There are not enough vouchers to fill the template.'))
                        return self.get(self.request, *self.args, **self.kwargs)

                    context_dict = {
                        'event': self.request.event.name,
                        'voucher': vouchers
                    }
                    preview_subject = str(subject).format_map(context_dict)
                    preview_text = markdown_compile_email(str(message).format_map(context_dict))

                    self.output[l] = {
                        'subject': _('Subject: {subject}').format(subject=preview_subject),
                        'html': preview_text,
                    }

            return self.get(self.request, *self.args, **self.kwargs)

        # collect vouchers
        vouchers = {l:[] for l in self.request.event.settings.locales}
        vouchers.update({None:[]})
        try:
            with transaction.atomic():
                for r in recipients:
                    if isinstance(r,tuple):
                        locale, email_address = r
                    else:
                        locale = None
                        email_address = r
                    with language(locale):
                        v = build_voucher_template_dict(self.request.event, str(subject)+str(message), how_shared=email_address)
                        vouchers[locale].append(v)
        except NoMatchingVoucher:
            messages.error(self.request, _('There are not enough vouchers to fill the template.'))
            return self.get(self.request, *self.args, **self.kwargs)

        # send e-mails
        send_mails.apply_async(
            kwargs={
                'recipients': recipients,
                'vouchers': vouchers,
                'event': self.request.event.pk,
                'user': self.request.user.pk,
                'subject': subject.data,
                'message': message.data,
            }
        )
        self.request.event.log_action('pretix.plugins.pretix_send_vouchers.sent',
                                      user=self.request.user,
                                      data=dict(form.cleaned_data))
        messages.success(self.request, _('Your message has been queued and will be sent to the provided addresses in the next minutes.'))

        return redirect(
            'plugins:pretix_send_vouchers:send',
            event=self.request.event.slug,
            organizer=self.request.event.organizer.slug
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['output'] = getattr(self, 'output', None)
        return ctx

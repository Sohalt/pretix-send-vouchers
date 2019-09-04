import logging
from datetime import timedelta

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from pretix.base.i18n import language
from pretix.base.templatetags.rich_text import markdown_compile_email
from pretix.control.permissions import EventPermissionRequiredMixin
from pretix.multidomain.urlreverse import build_absolute_uri

from .forms import MailForm
from .tasks import send_mails
from .util import normalize_voucher_template, build_voucher_template_dict

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

        if self.request.POST.get("action") == "preview":
            for l in self.request.event.settings.locales:

                with language(l):

                    subject = form.cleaned_data['subject'].localize(l)
                    subject = normalize_voucher_template(subject)
                    message = form.cleaned_data['message'].localize(l)
                    message = normalize_voucher_template(message)
                    vouchers = build_voucher_template_dict(self.request.event, subject+message)
                    context_dict = {
                        'event': self.request.event.name,
                        'voucher': vouchers
                    }
                    preview_subject = subject.format_map(context_dict)
                    preview_text = markdown_compile_email(message.format_map(context_dict))

                    self.output[l] = {
                        'subject': _('Subject: {subject}').format(subject=preview_subject),
                        'html': preview_text,
                    }

            return self.get(self.request, *self.args, **self.kwargs)

        send_mails.apply_async(
            kwargs={
                'recipients': form.cleaned_data['recipients'],
                'event': self.request.event.pk,
                'user': self.request.user.pk,
                'subject': form.cleaned_data['subject'].data,
                'message': form.cleaned_data['message'].data,
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

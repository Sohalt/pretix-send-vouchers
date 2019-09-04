import re

from django import forms
from django.core.validators import BaseValidator, validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from i18nfield.forms import I18nFormField, I18nTextarea, I18nTextInput
from i18nfield.strings import LazyI18nString

from .util import normalize_voucher_template


class RegexPlaceholderValidator(BaseValidator):
    """
    Takes list of regular expressinos for allowed placeholders,
    validates form field by checking for placeholders,
    which are not presented in taken list.
    """

    def __init__(self, limit_value):
        super().__init__(limit_value)
        self.limit_value = limit_value

    def __call__(self, value):
        if isinstance(value, LazyI18nString):
            for l, v in value.data.items():
                self.__call__(v)
            return

        if value.count('{') != value.count('}'):
            raise ValidationError(
                _('Invalid placeholder syntax: You used a different number of "{" than of "}".'),
                code='invalid',
            )

        data_placeholders = list(re.findall(r'({[^}]*})', value, re.X))
        invalid_placeholders = []
        for placeholder in data_placeholders:
            if not any([re.match(r,placeholder) for r in self.limit_value]):
                invalid_placeholders.append(placeholder)
        if invalid_placeholders:
            raise ValidationError(
                _('Invalid placeholder(s): %(value)s'),
                code='invalid',
                params={'value': ", ".join(invalid_placeholders,)})

    def clean(self, x):
        return x

class EmailsField(forms.CharField):
    widget = forms.Textarea

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(self.validate_emails)
        self.help_text=_("Add one E-mail per line.")

    def to_python(self, value):
        return value.split()

    def validate_emails(self, emails):
        for email in emails:
            validate_email(email)


class MailForm(forms.Form):
    recipients = EmailsField(
        label=_('Recipients'),
        required=True
    )
    subject = forms.CharField(
        label=_('Subject'),
        required=True
    )
    message = forms.CharField(
        label=_('Message'),
        required=True
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super().__init__(*args, **kwargs)

        self.fields['subject'] = I18nFormField(
            label=_('Subject'),
            widget=I18nTextInput, required=True,
            locales=event.settings.get('locales'),
            help_text=_("Available placeholders: {event}, {voucher.&lt;tag&gt;.&lt;n&gt;} where &lt;tag&gt; is a voucher tag and &lt;n&gt; is a number"),
            validators=[RegexPlaceholderValidator(['{event}','{voucher(\.[^}.]+(\.\d+)?)?}'])]
        )
        self.fields['message'] = I18nFormField(
            label=_('Message'),
            widget=I18nTextarea, required=True,
            locales=event.settings.get('locales'),
            help_text=_("Available placeholders: {event}, {voucher.&lt;tag&gt;.&lt;n&gt;} where &lt;tag&gt; is a voucher tag and &lt;n&gt; is a number"),
            validators=[RegexPlaceholderValidator(['{event}','{voucher(\.[^}.]+(\.\d+)?)?}'])]
        )

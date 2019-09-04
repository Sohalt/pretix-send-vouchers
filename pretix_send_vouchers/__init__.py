from django.utils.translation import ugettext_lazy
try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    name = 'pretix_send_vouchers'
    verbose_name = 'Pretix Send Vouchers'

    class PretixPluginMeta:
        name = ugettext_lazy('Pretix Send Vouchers')
        author = 'sohalt'
        description = ugettext_lazy('A plugin to send vouchers to a list of e-mail addresses')
        visible = True
        version = '1.0.0'
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_send_vouchers.PluginApp'

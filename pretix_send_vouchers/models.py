from django.db import models

from pretix.base.models.vouchers import Voucher

class VoucherMarking(models.Model):
    voucher = models.OneToOneField(
        Voucher,
        on_delete=models.CASCADE,
        related_name="marking"
    )
    shared = models.CharField(max_length=255)

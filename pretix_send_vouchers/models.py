from django.db import models

from pretix.base.models.vouchers import Voucher

class VoucherMarking(models.Model):
    voucher = models.OneToOneField(
        Voucher,
        on_delete=models.CASCADE,
        related_name="marking"
    )
    shared = models.CharField(max_length=255)

    @classmethod
    def create(cls, voucher, how_shared):
        vm = cls(voucher=voucher, shared=how_shared)
        voucher.comment = "Shared by pretix_send_vouchers with: {}\n{}".format(how_shared, voucher.comment)
        voucher.save()
        return vm

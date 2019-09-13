import re

from django.db.models import F, Q
from django.utils.timezone import now

from .models import VoucherMarking


def normalize_voucher_template(template):
    """
    Turns template placeholders of form
    '{voucher}' into '{voucher.*.0}'
    and
    '{voucher.foo}' into '{voucher.foo.0}'
    """
    template = re.sub(r'{voucher}','{voucher.*.0}',template)
    template = re.sub(r'{voucher\.([^\.}]+)}',r'{voucher.\1.0}',template)
    return template


class DictHelper(dict):

    def __getattr__(self, k):
        return getattr(super(), k, self.get(k))


class NoMatchingVoucher(Exception):
    pass


def build_voucher_template_dict(event, template, how_shared=None):
    """
    Looks for template placeholders of form '{voucher.tag.idx}' and builds a
    nested data structure with vouchers to be used with `str.format_map`.
    '{voucher.foo.0}' gets expanded to an unused voucher with tag 'foo'.
    '{voucher.*.0}' gets expanded to an unused voucher with an arbitrary tag.
    The last part (idx) allows to refer to the same voucher in multiple places.
    """
    d = DictHelper()
    wildcard = set(re.findall(r'{voucher\.\*\.(\d+)}', template, re.X))
    tagged = set(re.findall(r'{voucher\.([^}\.\*]+).(\d+)}', template, re.X))
    vouchers = event.vouchers.filter(Q(redeemed=0) &
                                     (Q(valid_until__isnull=True) | Q(valid_until__gt=now())) &
                                     Q(marking__isnull=True))

    exclude = []

    for tag,n in tagged:
        d.setdefault(tag,DictHelper()).update({n:None})

    for tag in d:
        vs = vouchers.filter(tag=tag)[:len(d[tag])]
        for i,idx in enumerate(d[tag].keys()):
            try:
                v = vs[i]
                exclude.append(v.pk)
            except IndexError:
                raise NoMatchingVoucher('Could not find a valid voucher for tag "{}" and index "{}"'.format(tag,idx))
            d[tag][idx] = str(v)
            if how_shared:
                VoucherMarking(v,how_shared).save()

    d['*'] = DictHelper()
    vs = vouchers.exclude(pk__in=exclude).iterator()
    for n in wildcard:
        try:
            v = next(vs)
        except StopIteration:
            raise NoMatchingVoucher('Could not find a valid voucher for tag "*" and index "{}"'.format(n))
        d['*'][n] = str(v)
        if how_shared:
            VoucherMarking(v,how_shared).save()

    return d

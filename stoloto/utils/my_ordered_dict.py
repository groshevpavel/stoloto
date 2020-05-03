from collections import OrderedDict


class MyOrderedDict(OrderedDict):
    """When adding value into existing key,
    value transforms into list() with old value
    and new values will adds into that list"""

    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        if key in self:
            vval = super(__class__, self).__getitem__(key)

            if not isinstance(vval, list):
                v = [vval, val]
                super(__class__, self).__setitem__(key, v)
            else:
                vval.append(val)
                super(__class__, self).__setitem__(key, vval)

        else:
            super(__class__, self).__setitem__(key, val)

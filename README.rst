Pretix Send Vouchers
==========================

This is a plugin for `pretix`_ to allow sending vouchers to a list of e-mail addresses.

Usage
-----

Install and enable the plugin, then navigate to the ``Send out vouchers`` menu item.

Here you can provide a list of e-mail addresses, separated by newlines.

In the ``Subject`` and ``Message`` fields you can compose your e-mail and use special placeholders to embed vouchers in your e-mail.

``{voucher}`` and ``{voucher.*}`` gets expanded to an arbitrary voucher, which has never been redeemed and is still valid.
``{voucher.foo}`` gets expanded to an arbitrary voucher with tag ``foo``, which has never been redeemed and is still valid.

Repeated use of the placeholder will result in the same expansion. To get multiple, different vouchers within the same email, you can use an unique index:

``{voucher.foo.1}`` and ``{voucher.foo.2}`` expand to two different vouchers with tag ``foo``, which have never been redeemed and are still valid.


Development setup
-----------------

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository, eg to ``local/pretix-send-vouchers``.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------


Copyright 2019 sohalt

Released under the terms of the Apache License 2.0



.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html

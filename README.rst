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


Design decisions
----------------

1. Substituting existing vouchers vs generating new vouchers

The plugin does not create any vouchers itself, instead it looks up already existing vouchers and substitutes them in templates. This has the advantage, that you have more direct control over how many vouchers you are handing out and can easily set an upper limit. Additionally it solves the problem of having to specify, what properties a newly generated voucher should have (e.g. max usages, valid until, etc.). 

2. Eager vs lazy evaluation of voucher placeholders

We are eagerly building the object holding the vouchers for substitution using ``build_voucher_template_dict`` before passing the result to ``format_map``. An alternative approach would be to pass a special ``voucher object`` to ``format_map``, which would then lazily look up vouchers and cache them, when the placeholder gets actually substituted. This has the disadvantage though, that you cannot tell beforehand, if there are enough vouchers of a certain type available. Only when expanding the template, which is done in the ``mail`` function from pretix, do you find out. This is too late to notify the user who initiated the action.


License
-------


Copyright 2019 sohalt

Released under the terms of the Apache License 2.0



.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html

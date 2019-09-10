import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-send-vouchers',
    version='1.0.0',
    description='A plugin to send vouchers to a list of e-mail addresses',
    long_description=long_description,
    url='https://github.com/sohalt/pretix-send-vouchers',
    author='sohalt',
    author_email='sohalt@sohalt.net',
    license='Apache Software License',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_send_vouchers=pretix_send_vouchers:PretixPluginMeta
""",
)

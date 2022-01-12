# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_basic_auth import __version__

REQUIREMENTS = [
    # dependency for constance database backend
    'django-picklefield>=0.3.2',
    # dependency for managing settings via admin
    'django-constance',
    'aldryn-addons',
    'six',
]


setup(
    name='aldryn-basic-auth',
    version=__version__,
    description=open('README.rst').read(),
    author='Divio AG',
    author_email='info@divio.com',
    packages=find_packages(),
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    zip_safe=False,
)

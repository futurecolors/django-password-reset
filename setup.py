# coding: utf-8
from distutils.core import setup
from setuptools import find_packages


setup(
    name='django-password-reset-fc',
    version=__import__('password_reset').__version__,
    author='Ilya Baryshev',
    author_email='baryshev@futurecolors.ru',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/brutasse/django-password-reset',
    license='BSD licence, see LICENSE file',
    description='Class-based views for password reset.',
    long_description=open('README.rst').read(),
    install_requires=[
        'django-templated-email==0.4.7',
    ],
    tests_require=[
        'django>=1.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    test_suite='runtests.runtests',
    zip_safe=False,
)

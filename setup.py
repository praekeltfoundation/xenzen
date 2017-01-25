import codecs
import os

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


# Stolen from txacme
def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


setup(
    name='xenzen',
    version='1.0.0.dev0',
    license='MIT',
    url='https://github.com/praekeltfoundation/xenzen',
    description=(
        'A Django UI for managing XenServer in the simplest possible way.'),
    long_description=read('README.md'),
    author='Colin Alston',
    maintainer='Praekelt.org SRE team',
    maintainer_email='sre@praekelt.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'celery < 4',
        'Django >= 1.8, < 1.9',
        'django-celery',
        'django-celery-email',
        'django-crispy-forms',
        'django-haystack',
        'django-social-auth == 0.7.28',
        'lxml',
        'psycopg2',
        'pyyaml',
        'raven',
        'redis',
    ],
)

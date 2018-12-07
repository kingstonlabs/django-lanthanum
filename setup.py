import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


tests_require = [
    'pytest>=4.0.1',
    'pytest-cov>=2.6.0',
    'pytest-django>=3.4.4'
]

install_requires = [
    'django>=2.0',
    'django-admin-json-editor>=0.1.5',
    'jsonschema>=2.6.0',
    'psycopg2==2.7.5'
]


setup(
    name='django-lanthanum',
    version='0.1.2',
    description='Dynamic JSON Schema Fields for Django Postgres Models',
    long_description=README,
    author='Kingston Labs',
    author_email='tom@kingstonlabs.co.uk',
    license='BSD',
    url='https://github.com/kingstonlabs/lanthanum',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
)

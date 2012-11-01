# -*- coding: utf-8 -*-
"""
This module contains the tool of ftw.shop
"""
import os
from setuptools import setup, find_packages

version = '1.1.3.dev0'

tests_require = ['zope.testing',
                 'Products.PloneTestCase',
                 'pyquery<=0.6.1',
                ]

setup(name='ftw.shop',
      version=version,
      description="A web shop solution for Plone",
      long_description=open("README.rst").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),

      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],

      keywords='ftw shop plone',
      author='4teamwork GmbH',
      author_email='mailto:@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.shop',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'plone.app.z3cform',
        'collective.z3cform.wizard',
        'plone.app.registry',
        'simplejson',
        'collective.js.jqueryui',
#        'Products.ATCountryWidget',
      ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'ftw.shop.tests.test_docs.test_suite',

      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

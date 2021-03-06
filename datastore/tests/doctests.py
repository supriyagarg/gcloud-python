# Copyright 2014 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pkgutil
import tempfile
import unittest

import six

from google.cloud import datastore


SPHINX_CONF = """\
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
]
"""

SPHINX_SECTION_TEMPLATE = """\
Section %02d
===========

.. automodule:: google.cloud.%s
  :members:

"""


@unittest.skipIf(six.PY2, 'Doctests run against Python 3 only.')
class TestDoctest(unittest.TestCase):

    def _submodules(self):
        pkg_iter = pkgutil.iter_modules(datastore.__path__)
        result = []
        for _, mod_name, ispkg in pkg_iter:
            self.assertFalse(ispkg)
            result.append(mod_name)

        self.assertNotIn('__init__', result)
        return result

    @staticmethod
    def _add_section(index, mod_name, file_obj):
        mod_part = 'datastore'
        if mod_name != '__init__':
            mod_part += '.' + mod_name
        content = SPHINX_SECTION_TEMPLATE % (index, mod_part)
        file_obj.write(content)

    def _make_temp_docs(self):
        docs_dir = tempfile.mkdtemp(prefix='datastore-')

        conf_file = os.path.join(docs_dir, 'conf.py')

        with open(conf_file, 'w') as file_obj:
            file_obj.write(SPHINX_CONF)

        index_file = os.path.join(docs_dir, 'contents.rst')
        datastore_modules = self._submodules()
        with open(index_file, 'w') as file_obj:
            self._add_section(0, '__init__', file_obj)
            for index, datastore_module in enumerate(datastore_modules):
                self._add_section(index + 1, datastore_module, file_obj)

        return docs_dir

    def test_it(self):
        from sphinx import application

        docs_dir = self._make_temp_docs()
        outdir = os.path.join(docs_dir, 'doctest', 'out')
        doctreedir = os.path.join(docs_dir, 'doctest', 'doctrees')

        app = application.Sphinx(
            srcdir=docs_dir, confdir=docs_dir,
            outdir=outdir, doctreedir=doctreedir,
            buildername='doctest', warningiserror=True, parallel=1)

        app.build()
        self.assertEqual(app.statuscode, 0)

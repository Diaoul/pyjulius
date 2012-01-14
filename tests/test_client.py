# -*- coding: utf-8 -*-
# Copyright 2011-2012 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of pyjulius.
#
# pyjulius is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyjulius is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyjulius.  If not, see <http://www.gnu.org/licenses/>.
from pyjulius.core import Client
from xml.etree.ElementTree import Element
import unittest


class ClientTestCase(unittest.TestCase):
    tests = ['test_data_received', 'test_modelize_off', 'test_command']

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.connect()
        cls.client.start()

    @classmethod
    def tearDownClass(cls):
        cls.client.stop()
        cls.client.join()
        cls.client.disconnect()

    def setUp(self):
        self.client.modelize = True

    def test_data_received(self):
        result = self.client.results.get()
        self.assertTrue(result is not None)

    def test_command(self):
        self.client.send('STATUS')
        while 1:
            result = self.client.results.get()
            if isinstance(result, Element) and result.tag == 'INPUT' and result.get('STATUS') == 'LISTEN':
                break

    def test_modelize_off(self):
        self.client.modelize = False
        while 1:
            result = self.client.results.get()
            if isinstance(result, Element) and result.tag == 'RECOGOUT':
                break


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(map(ClientTestCase, ClientTestCase.tests))
    unittest.TextTestRunner(verbosity=2).run(suite)

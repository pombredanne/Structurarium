import os
import shutil
from unittest import TestCase

from structurarium.elements.base import Base

from mocks import Transaction


class TestBaseElement(TestCase):

    # FIXME load from cache
    # FIXME load from transaction

    def setUp(self):
        self.txn = Transaction()
        os.makedirs('/tmp/graphiti-tests/Base')

    def tearDown(self):
        shutil.rmtree('/tmp/graphiti-tests/')

    def test_get(self):
        element = Base(self.txn, 'test', 'test value')
        self.assertEqual(element.get(), 'test value')

    def test_set(self):
        element = Base(self.txn, 'test', 'test value')
        element.set('another test')
        self.assertEqual(element.get(), 'another test')

    def test_load_save(self):
        element = Base(self.txn, 'test', 'test value')
        element.save()
        element = Base.load(self.txn, 'test')
        self.assertEqual(element.get(), 'test value')

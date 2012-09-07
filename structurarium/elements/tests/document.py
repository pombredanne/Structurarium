import os
import shutil
from unittest import TestCase

from structurarium.elements.base import Base
from structurarium.elements.document import Document

from mocks import Transaction


class TestDocumentElement(TestCase):

    # FIXME load from cache
    # FIXME load from transaction
    # FIXME iterdata

    def setUp(self):
        self.txn = Transaction()
        os.makedirs('/tmp/graphiti-tests/Document')

    def tearDown(self):
        shutil.rmtree('/tmp/graphiti-tests/')

    def test_inheritance(self):
        self.assertTrue(issubclass(Document, Base))

    def test_get(self):
        element = Document(self.txn, 'test', {'key': 'value'})
        self.assertEqual(element.get('key'), 'value')

    def test_set(self):
        element = Document(self.txn, 'test', {'key': 'value'})
        element.set('key', 'another value')
        self.assertEqual(element.get('key'), 'another value')

    def test_load_save(self):
        element = Document(self.txn, 'test', {'key': 'value'})
        element.save()
        element = Document.load(self.txn, 'test')
        self.assertEqual(element.get('key'), 'value')

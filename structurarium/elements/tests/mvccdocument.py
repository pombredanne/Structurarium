import os
import shutil
from unittest import TestCase

from structurarium.elements.mvccdocument import Document
from structurarium.elements.mvccdocument import MVCCDocument
from structurarium.exceptions import ElementNotFound

from mocks import Transaction


class TestMVCCDocument(TestCase):

    # FIXME load from cache
    # FIXME load from transaction
    # FIXME iterdata

    def setUp(self):
        self.txn = Transaction()
        os.makedirs('/tmp/graphiti-tests/MVCCDocument')

    def tearDown(self):
        shutil.rmtree('/tmp/graphiti-tests/')

    def test_inheritance(self):
        self.assertTrue(issubclass(MVCCDocument, Document))

    def test_get(self):
        element = MVCCDocument(
            self.txn,
            'identifier',
            'version',
            {'key': 'value'}
        )
        self.assertEqual(element.get('key'), 'value')

    def test_set(self):
        element = MVCCDocument(
            self.txn,
            'identifier',
            'version',
            {'key': 'value'}
        )
        element.set('key', 'another value')
        self.assertEqual(element.get('key'), 'another value')

    def test_save(self):
        element = MVCCDocument.create(
            self.txn,
            {'key': 'value'}
        )
        element.save()
        self.assertTrue(os.path.exists(element.path()))
        path = os.path.join(element.path(), element.version)
        self.assertTrue(os.path.exists(path))

    def test_load_save(self):
        element = MVCCDocument.create(
            self.txn,
            {'key': 'value'}
        )
        element.save()
        element = MVCCDocument.load(self.txn, element.identifier)
        self.assertEqual(element.get('key'), 'value')

    def test_delete_version(self):
        element = MVCCDocument.create(
            self.txn,
            {'key': 'value'}
        )
        element.save()
        element.delete()
        path = os.path.join(element.path(), element.version)
        self.assertFalse(os.path.exists(path))

    def test_load_latest_version(self):
        element = MVCCDocument.create(
            self.txn,
            {'key': 'value'}
        )
        element.save()
        for x in range(10):
            element.set('key', x)
        element = MVCCDocument.load(self.txn, element.identifier)
        self.assertEqual(element.get('key'), 9)

    def test_delete_element(self):
        element = MVCCDocument.create(
            self.txn,
            {'key': 'value'}
        )
        element.save()
        txn = Transaction(ts=2)
        element = MVCCDocument.load(txn, element.identifier)
        element.expire_ts(True)
        element.save()
        txn = Transaction(ts=3)
        txn.commited_ts = [1, 2]
        self.assertRaises(
            ElementNotFound,
            MVCCDocument.load,
            txn,
            element.identifier
        )

    def test_deleted_element_by_an_uncommited_transaction(self):
        element = MVCCDocument.create(
            self.txn,
            {'key': 'value'}
        )
        element.save()
        
        element.expire_ts(True)
        txn = Transaction(ts=2)
        element = MVCCDocument.load(txn, element.identifier)
        element.expire_ts(True)
        element.save()
        txn = Transaction(ts=3)
        self.assertTrue(MVCCDocument.load(txn, element.identifier))

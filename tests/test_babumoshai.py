import unittest

import pylaagu.babumoshai
from pylaagu.babumoshai import NSExportSpec


class TestBabumoshai(unittest.TestCase):


    def test_basic_ns_export(self):
        module = "pylaagu.meta"
        nsspec = NSExportSpec(module_name=module)
        self.assertEqual("pylaagu.meta", nsspec.ns_name)

    def test_ns_export_with_ns_name(self):
        module = "pylaagu.meta"
        ns_name = "py.meta"
        nsspec = NSExportSpec(module_name=module, ns_name=ns_name)
        self.assertEqual(ns_name, nsspec.ns_name)


    def test_ns_load_with_meta(self):
        module = "pylaagu.meta"
        nsspec = NSExportSpec(module_name=module, ns_name='py.meta', export_meta=True)
        ns = pylaagu.babumoshai.load_as_namespace(nsspec)
        foo = ns.get("function-signatures")
        self.assertTrue(foo is not None)
        self.assertEqual(foo['name'], "function-signatures")
        self.assertEqual("py.meta", ns.name)
        self.assertTrue(ns.get('ClassSignature') is None) # Classes should not be exported

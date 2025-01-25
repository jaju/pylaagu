import os
import sys
import unittest

import pylaagu.meta as meta
import pylaagu.utils as utils
from pylaagu.meta import ClassSignature

class TestMeta(unittest.TestCase):

    @staticmethod
    def module_to_file_path(module_name: str):
        file = sys.modules["pylaagu.meta"].__file__
        return os.path.abspath(file)


    def test_function_signatures(self):
        """This test verifies that function signatures are encoded correctly"""
        file = self.module_to_file_path("pylaagu.meta")
        signatures = meta.function_signatures(file, utils.is_public)
        signatures = dict(map(lambda s: [s.name, s], signatures))
        self.assertTrue(signatures["function_signatures"] is not None, msg="Method function_signatures not found in signatures")
        self.assertTrue(signatures["class_signatures"] is not None, msg="Method class_signatures not found in signatures")
        self.assertTrue(signatures["example_function"] is not None, msg="Method class_signatures not found in signatures")


    def test_example_function_details(self):
        file = self.module_to_file_path("pylaagu.meta")
        signatures = meta.function_signatures(file, utils.is_public)
        signatures = dict(map(lambda s: [s.name, s], signatures))
        example_function = signatures["example_function"]
        self.assertTrue(example_function is not None, msg="Method class_signatures not found in signatures")
        self.assertEqual([{"name": "arg1"}, {"name": "arg2"}], example_function.args)
        self.assertEqual({"name": "args"}, example_function.vararg)
        self.assertEqual({"name": "kwargs"}, example_function.kwarg)
        self.assertEqual('int', example_function.returns)

    def test_class_signatures(self):
        file = self.module_to_file_path("pylaagu.meta")
        signatures: list[ClassSignature] = meta.class_signatures(file, utils.is_public)
        signatures: dict[str, ClassSignature] = dict(map(lambda s: [s.name, s], signatures))
        self.assertTrue(signatures["FunctionSignature"] is not None, msg="Class FunctionSignature not found")
        self.assertEqual("FunctionSignature", signatures["FunctionSignature"].name)
        self.assertTrue(signatures["ClassSignature"] is not None, msg="Class ClassSignature not found")
        self.assertEqual("ClassSignature", signatures["ClassSignature"].name)

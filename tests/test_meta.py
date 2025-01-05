import os
import sys
import unittest

import pylaagu.meta as meta
import pylaagu.utils as utils
from pylaagu.meta import ClassSignature


class TestMeta(unittest.TestCase):

    def test_function_signatures(self):
        """This test verifies that function signatures are encoded correctly"""
        file = sys.modules["pylaagu.meta"].__file__
        file = os.path.abspath(file)
        signatures = meta.function_signatures(file, utils.is_public)
        signatures = dict(map(lambda s: [s.name, s], signatures))
        self.assertTrue(signatures["function_signatures"] is not None, msg="Method function_signatures not found in signatures")
        self.assertTrue(signatures["class_signatures"] is not None, msg="Method class_signatures not found in signatures")


    def test_class_signatures(self):
        file = sys.modules["pylaagu.meta"].__file__
        file = os.path.abspath(file)
        signatures: list[ClassSignature] = meta.class_signatures(file, utils.is_public)
        signatures: dict[str, ClassSignature] = dict(map(lambda s: [s.name, s], signatures))
        self.assertTrue(signatures["FunctionSignature"] is not None, msg="Class FunctionSignature not found")
        self.assertEqual(signatures["FunctionSignature"].name, "FunctionSignature")
        self.assertTrue(signatures["ClassSignature"] is not None, msg="Class ClassSignature not found")
        self.assertEqual(signatures["ClassSignature"].name, "ClassSignature")

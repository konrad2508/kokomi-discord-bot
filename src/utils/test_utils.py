import unittest
from typing import Callable
from unittest.mock import patch


def tested_module(source_module: str) -> Callable:
    def inner(test_case: TestCase) -> TestCase:
        test_case._source = source_module

        return test_case
    
    return inner


class TestCase(unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        patch.stopall()
    
    def patch(self, target: str):
        return patch(f'{self._source}.{target}').start()

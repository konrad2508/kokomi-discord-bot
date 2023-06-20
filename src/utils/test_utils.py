import unittest
from typing import Callable
from unittest.mock import AsyncMock, MagicMock, patch, call


class TestCase(unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        patch.stopall()
    
    def patch(self, target: str):
        return patch(f'{self._source}.{target}').start()
    
    def patch_dict(self, target: dict, substitute: dict) -> None:
        patch.dict(target, substitute).start()
    
    def assertNotRaises(self, expected_exception: Exception, callable: Callable, *args, **kwargs) -> None:
        try:
            callable(*args, **kwargs)
        except expected_exception:
            self.fail(f'{expected_exception.__name__} raised by {callable.__name__}')
    
    def assertHasCalls(self, mock: MagicMock | AsyncMock, call_args: list[tuple[object]]) -> None:
        mock.assert_has_calls([call(*args) for args in call_args])


def tested_module(source_module: str) -> Callable:
    def inner(test_case: TestCase) -> TestCase:
        test_case._source = source_module

        return test_case
    
    return inner

import collections.abc
import random
from functools import reduce

from model.exception.bad_operand import BadOperand
from model.exception.input_not_present import InputNotPresent


class MarkovGrammar:
    def __init__(self) -> None:
        self.occ_matrix: dict[str, dict[str, int]] = {}
        self.freq_matrix: dict[str, dict[str, float]] = {}
        self.utd_matrix: dict[str, bool] = {}

    def __iadd__(self, other: list[str]) -> None:
        if not isinstance(other, collections.abc.Sequence) or len(other) != 2:
            raise BadOperand

        input, output = other
        
        if input not in self.occ_matrix:
            self.occ_matrix[input] = {}

        if output not in self.occ_matrix[input]:
            self.occ_matrix[input][output] = 1
        
        else:
            self.occ_matrix[input][output] += 1
        
        self.utd_matrix[input] = False

        return self

    def __getitem__(self, input: str) -> str:
        if input not in self.occ_matrix:
            raise InputNotPresent
        
        if not self.utd_matrix[input]:
            total_occ = reduce((lambda acc, x: acc + x), [*self.occ_matrix[input].values()])
            self.freq_matrix[input] = { k: v / total_occ for k, v in self.occ_matrix[input].items() }

            self.utd_matrix[input] = True

        return random.choices(
            population=[*self.freq_matrix[input].keys()],
            weights=[*self.freq_matrix[input].values()]
        )[0]

    def print_matrixes(self):
        print(self.occ_matrix)
        print(self.freq_matrix)
        print(self.utd_matrix)

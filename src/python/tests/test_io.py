import pytest
from dimod import generators, BinaryQuadraticModel, ExactSolver
import dimod
from zquantum.qubo.io import (
    bqm_to_serializable,
    bqm_from_serializable,
    save_qubo,
    load_qubo,
)
from zquantum.qubo.utils import (
    save_dimod_sample_set,
)
from io import StringIO
import os


class TestConvertingBQMToSerializable:
    def test_all_linear_coefficients_are_stored(self):
        bqm = dimod.BinaryQuadraticModel(
            {0: 1, 1: 2, 2: 3},
            {(1, 2): 0.5, (1, 0): 0.7, (0, 2): 0.9},
            -10,
            vartype=dimod.BINARY,
        )

        serializable = bqm_to_serializable(bqm)

        assert set(serializable["linear"]) == {(0, 1), (1, 2), (2, 3)}

    def test_all_quadratic_coefficients_are_stored(self):
        bqm = dimod.BinaryQuadraticModel(
            {0: 0.5, 2: -2.0, 3: 3},
            {(2, 1): 0.5, (1, 0): 0.4, (0, 3): -0.1},
            -5,
            vartype=dimod.BINARY,
        )

        serializable = bqm_to_serializable(bqm)

        assert set(serializable["quadratic"]) == {
            (1, 2, 0.5),
            (0, 1, 0.4),
            (0, 3, -0.1),
        }

    @pytest.mark.parametrize("offset", [-5, 10, 0])
    def test_offset_is_stored(self, offset):
        bqm = dimod.BinaryQuadraticModel(
            {0: 0.5, 2: -2.0, 3: 3},
            {(2, 1): 0.5, (1, 0): 0.4, (0, 3): -0.1},
            offset,
            vartype=dimod.BINARY,
        )

        serializable = bqm_to_serializable(bqm)

        assert serializable["offset"] == offset

    @pytest.mark.parametrize(
        "vartype, expected_output_vartype",
        [
            ("SPIN", "SPIN"),
            ("BINARY", "BINARY"),
            (dimod.BINARY, "BINARY"),
            (dimod.SPIN, "SPIN"),
        ],
    )
    def test_vartype_is_stored(self, vartype, expected_output_vartype):
        bqm = dimod.BinaryQuadraticModel(
            {0: 0.5, 2: -2.0, 3: 3},
            {(2, 1): 0.5, (1, 0): 0.4, (0, 3): -0.1},
            vartype=vartype,
        )

        serializable = bqm_to_serializable(bqm)

        assert serializable["vartype"] == expected_output_vartype


class TestConstructingBQMFromSerializable:
    def test_all_linear_coefficients_are_loaded(self):
        bqm_dict = {
            "linear": [(0, 2.0), (2, 0.5), (1, -1.0)],
            "quadratic": [(0, 1, 1.2), (1, 2, 4.0)],
            "offset": 0.5,
            "vartype": "SPIN",
        }

        bqm = bqm_from_serializable(bqm_dict)
        assert bqm.linear == {0: 2.0, 2: 0.5, 1: -1.0}

    def test_all_quadratic_coefficients_are_loaded(self):
        bqm_dict = {
            "linear": [(0, 1.0), (1, 2.0), (2, 0.5)],
            "quadratic": [(0, 1, 2.1), (1, 2, 4.0), (1, 3, -1.0)],
            "offset": 0.1,
            "vartype": "BINARY",
        }

        bqm = bqm_from_serializable(bqm_dict)

        assert bqm.quadratic == {(0, 1): 2.1, (1, 2): 4.0, (1, 3): -1.0}

    @pytest.mark.parametrize("offset", [0.1, 2, -3.5])
    def test_offset_is_loaded(self, offset):
        bqm_dict = {
            "linear": [(0, 1.0), (1, 2.0), (2, 0.5)],
            "quadratic": [(0, 1, 2.1), (1, 2, 4.0), (1, 3, -1.0)],
            "offset": offset,
            "vartype": "BINARY",
        }

        bqm = bqm_from_serializable(bqm_dict)

        assert bqm.offset == offset

    @pytest.mark.parametrize(
        "vartype, expected_bqm_vartype",
        [("SPIN", dimod.SPIN), ("BINARY", dimod.BINARY)],
    )
    def test_vartype_is_set_correctly(self, vartype, expected_bqm_vartype):
        bqm_dict = {
            "linear": [(0, 1.0), (2, 2.0), (1, 0.5)],
            "quadratic": [(0, 1, 1), (1, 2, 4.0), (1, 3, 1e-2)],
            "offset": 0.5,
            "vartype": vartype,
        }

        bqm = bqm_from_serializable(bqm_dict)

        assert bqm.vartype == expected_bqm_vartype


def test_loading_saved_qubo_gives_the_same_qubo():
    qubo = dimod.BinaryQuadraticModel(
        {0: 0.5, 2: -2.0, 3: 3},
        {(2, 1): 0.5, (1, 0): 0.4, (0, 3): -0.1},
        -5,
        vartype="BINARY",
    )

    output_file = StringIO()

    save_qubo(qubo, output_file)
    # Move to the beginning of the file
    output_file.seek(0)
    new_qubo = load_qubo(output_file)

    assert qubo == new_qubo


def test_sample_set_saving():

    nbits = 4
    qubo = generators.uniform(nbits, "BINARY", low=-1, high=1, seed=42)
    num_sweeps = 500

    sampleset = ExactSolver().sample(qubo)

    save_dimod_sample_set(sampleset, "output.json")
    os.remove("output.json")
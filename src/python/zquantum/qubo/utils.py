import numpy as np
import json
from typing import Union, Tuple
from dimod import BinaryQuadraticModel, SampleSet
from zquantum.core.utils import SCHEMA_VERSION


def evaluate_bitstring_for_qubo(
    bitstring: Union[str, np.ndarray, Tuple[int, ...]], qubo: BinaryQuadraticModel
):
    """Returns the energy associated with given bitstring for a specific qubo.

    Args:
        bitstring: string/array of zeros and ones representing solution to a qubo .
        qubo: qubo that we want to evaluate for.

    Returns:
        float: energy associated with a bistring
    """
    return qubo.energy({i: bit for i, bit in enumerate(map(int, bitstring))})


def save_dimod_sample_set(dimod_sample_set: SampleSet, filename: str):

    optimal_sample_set = dimod_sample_set.lowest()
    optimized_energy = optimal_sample_set.record.energy[0]
    optimized_bit_string = optimal_sample_set.record.sample[0]

    dictionary = {
        "optimized_energy": optimized_energy,
        "optimized_bitstring": optimized_bit_string.real.tolist(),
    }
    dictionary["schema"] = SCHEMA_VERSION + "-sample_set"

    with open(filename, "w") as outfile:
        json.dump(dictionary, outfile)

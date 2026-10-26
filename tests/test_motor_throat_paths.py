"""Cover every route from the Throat to the first motor along that route."""

from itertools import pairwise, product

import pytest

from humandesign.features.mechanics import get_typ
from humandesign.hd_constants import GATES_CHAKRA_DICT

MOTORS = {"SL", "HT", "SP", "RT"}


def motor_paths():
    """Enumerate simple paths from the channel map, independently of get_typ.

    Once a motor is reached, longer paths cannot change the motor-to-Throat
    predicate. Head/Ajna branches cannot reach a motor without revisiting TT.
    """
    graph = {}
    for first, second in GATES_CHAKRA_DICT.values():
        graph.setdefault(first, set()).add(second)
        graph.setdefault(second, set()).add(first)

    paths = []

    def walk(path):
        if path[-1] in MOTORS:
            paths.append(path)
            return
        for neighbor in sorted(graph[path[-1]] - set(path)):
            walk((*path, neighbor))

    walk(("TT",))
    return paths


def active_channels(gates, reverse=False):
    """Include every complete channel implied by the active gates.

    Closing over all channels avoids testing impossible charts where a shared
    gate would create an additional connection omitted from the fixture.
    """
    pairs = [
        (pair, centers)
        for pair, centers in GATES_CHAKRA_DICT.items()
        if set(pair) <= gates
    ]
    if reverse:
        pairs = [(pair[::-1], centers[::-1]) for pair, centers in reversed(pairs)]
    channels = {
        "gate": [pair[0] for pair, _ in pairs],
        "ch_gate": [pair[1] for pair, _ in pairs],
        "gate_chakra": [centers[0] for _, centers in pairs],
        "ch_gate_chakra": [centers[1] for _, centers in pairs],
    }
    defined = {center for _, centers in pairs for center in centers}
    return channels, defined


PATHS = motor_paths()


@pytest.mark.parametrize("path", PATHS, ids=lambda path: "-".join(path))
@pytest.mark.parametrize("reverse", [False, True], ids=["forward", "reversed"])
def test_every_motor_path(path, reverse):
    # Exercise all concrete channels for every center-to-center edge, rather
    # than choosing one representative of e.g. the four Throat/G channels.
    choices = [
        [
            pair
            for pair, centers in GATES_CHAKRA_DICT.items()
            if set(centers) == {first, second}
        ]
        for first, second in pairwise(path)
    ]
    for realization in product(*choices):
        gates = {gate for pair in realization for gate in pair}
        channels, defined = active_channels(gates, reverse)
        expected = "Manifesting Generator" if "SL" in defined else "Manifestor"
        assert get_typ(channels, defined) == expected, (path, realization, reverse)


@pytest.mark.parametrize(
    "gates, expected",
    [
        # An indirect Sacral/Spleen/Throat connection with no direct motor link.
        ({27, 50, 20, 57}, "Manifesting Generator"),
        # A Sacral in another component still belongs to the Generator family.
        ({21, 45, 3, 60}, "Manifesting Generator"),
        # A defined Throat alone does not supply manifesting potential.
        ({27, 50, 7, 31}, "Generator"),
        # A non-motor cycle must not bridge to an isolated Sacral/Root island.
        ({7, 31, 10, 57, 20, 3, 60}, "Generator"),
        ({20, 57}, "Projector"),
        ({64, 47}, "Projector"),
        ({3, 60}, "Generator"),
        ({1}, "Reflector"),
        (set(), "Reflector"),
    ],
)
def test_type_boundaries(gates, expected):
    channels, defined = active_channels(gates)
    assert get_typ(channels, defined) == expected

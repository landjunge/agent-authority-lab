"""False-positive panel must ALLOW under B0. Does not score catalog attacks."""

from lab.validator import Lab
from tests.convergence.fp_panel import (
    BOUNDARY,
    interior_steps,
    run_p2_public_egress,
    run_p2_public_internal,
)


def test_interior_panel_allows():
    for seed in range(20):
        lab = Lab()
        for req in interior_steps(seed):
            d = lab.submit(req)
            assert d.allow is True, (seed, req.action, req.resource, d)


def test_boundary_panel_allows():
    for name, builder in BOUNDARY.items():
        lab = Lab()
        for req in builder():
            d = lab.submit(req)
            assert d.allow is True, (name, req.action, req.resource, d)


def test_phase2_public_egress_copy_allows():
    exp = run_p2_public_egress()
    assert "H1" in exp.external


def test_phase2_public_internal_copy_allows():
    exp = run_p2_public_internal()
    assert exp.external == []

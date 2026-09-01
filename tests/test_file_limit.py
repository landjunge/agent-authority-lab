"""11th distinct file write is denied (I2), even split across agents."""

from lab.attacks import file_limit_split
from lab.models import I2_FILE_LIMIT
from lab.validator import Lab


def test_file_limit_denies_eleventh_unique_file():
    lab = Lab()
    wid = "wf-files"
    reqs = file_limit_split(wid)
    assert len(reqs) == 11
    for req in reqs[:10]:
        d = lab.submit(req)
        assert d.allow, d
    denied = lab.submit(reqs[10])
    assert denied.allow is False
    assert denied.deny_reason == I2_FILE_LIMIT
    assert lab.state(wid).files_changed == 10
    assert len(lab.state(wid).touched_paths) == 10

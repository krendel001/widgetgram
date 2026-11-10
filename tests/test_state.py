import json

import pytest

from widgetgram import StateTooLargeError
from widgetgram.utils.state import assert_state_fits


def test_small_state_passes():
    payload = json.dumps({"a": 1, "b": [2, 3]}, separators=(",", ":"))
    assert_state_fits(payload)


def test_overflow_raises():
    big = json.dumps({"x": "a" * 1200})
    with pytest.raises(StateTooLargeError):
        assert_state_fits(big)


def test_unicode_counted_as_bytes():
    payload = json.dumps({"t": "я" * 600}, ensure_ascii=False)
    with pytest.raises(StateTooLargeError):
        assert_state_fits(payload)


def test_edge_at_1024():
    payload = "x" * 1024
    assert_state_fits(payload)
    with pytest.raises(StateTooLargeError):
        assert_state_fits("x" * 1025)

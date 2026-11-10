import time

from widgetgram import NonceStore


def test_issue_and_consume():
    s = NonceStore(ttl=5)
    n = s.issue(1)
    assert s.consume(1, n) is True
    assert s.consume(1, n) is False


def test_wrong_nonce():
    s = NonceStore(ttl=5)
    s.issue(1)
    assert s.consume(1, "wrong") is False
    assert s.peek(1) is not None


def test_expired():
    s = NonceStore(ttl=0.01)
    n = s.issue(1)
    time.sleep(0.05)
    assert s.consume(1, n) is False
    assert s.peek(1) is None


def test_isolated_by_chat():
    s = NonceStore(ttl=5)
    a = s.issue(1)
    s.issue(2)
    assert s.consume(2, a) is False
    assert s.peek(1) == a


def test_purge():
    s = NonceStore(ttl=0.01)
    s.issue(1)
    s.issue(2)
    time.sleep(0.05)
    s.issue(3)
    assert s.purge() == 2
    assert s.peek(3) is not None

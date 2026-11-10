import asyncio

import pytest

from widgetgram import EditQueue


@pytest.mark.asyncio
async def test_single_push_fires():
    q = EditQueue(min_interval=0.01, idle_ttl=0.1)
    fired = []

    async def send():
        fired.append(1)

    q.push("k", send)
    await asyncio.sleep(0.05)
    assert fired == [1]


@pytest.mark.asyncio
async def test_coalesces_bursts():
    q = EditQueue(min_interval=0.05, idle_ttl=1)
    counter = {"n": 0}

    async def send():
        counter["n"] += 1

    for _ in range(50):
        q.push("k", send)
    await q.flush()
    assert counter["n"] == 1


@pytest.mark.asyncio
async def test_latest_sender_wins():
    q = EditQueue(min_interval=0.02, idle_ttl=1)
    seen = []

    def make(label):
        async def send():
            seen.append(label)
        return send

    q.push("k", make("old"))
    q.push("k", make("new"))
    await q.flush()
    assert seen == ["new"]


@pytest.mark.asyncio
async def test_two_keys_independent():
    q = EditQueue(min_interval=0.01, idle_ttl=1)
    seen = []

    def make(x):
        async def send():
            seen.append(x)
        return send

    q.push("a", make("a"))
    q.push("b", make("b"))
    await q.flush()
    assert sorted(seen) == ["a", "b"]


@pytest.mark.asyncio
async def test_rate_limit_enforced():
    q = EditQueue(min_interval=0.1, idle_ttl=5)
    fires = []

    async def send():
        fires.append(asyncio.get_running_loop().time())

    q.push("k", send)
    await asyncio.sleep(0.02)
    q.push("k", send)
    await asyncio.sleep(0.02)
    q.push("k", send)
    await asyncio.sleep(0.5)
    assert len(fires) == 2
    assert fires[1] - fires[0] >= 0.09

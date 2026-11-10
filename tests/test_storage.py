import pytest

from widgetgram.state import MemoryStateStorage


@pytest.mark.asyncio
async def test_storage_roundtrip():
    s = MemoryStateStorage()
    assert await s.get(1, 100) is None
    await s.put(1, 100, {"a": 1})
    got = await s.get(1, 100)
    assert got == {"a": 1}
    await s.drop(1, 100)
    assert await s.get(1, 100) is None


@pytest.mark.asyncio
async def test_storage_isolation():
    s = MemoryStateStorage()
    await s.put(1, 100, {"x": 1})
    await s.put(1, 101, {"x": 2})
    await s.put(2, 100, {"x": 3})
    assert (await s.get(1, 100))["x"] == 1
    assert (await s.get(1, 101))["x"] == 2
    assert (await s.get(2, 100))["x"] == 3


@pytest.mark.asyncio
async def test_storage_copies_on_read():
    s = MemoryStateStorage()
    await s.put(1, 1, {"w": [1, 2]})
    got = await s.get(1, 1)
    got["w"].append(999)
    fresh = await s.get(1, 1)
    assert fresh["w"] == [1, 2]

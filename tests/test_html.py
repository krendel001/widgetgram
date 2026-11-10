import pytest

from widgetgram import pack_html, assert_html_fits, html_fits, HtmlTooLargeError


def test_small_html_passes():
    html = "<!doctype html><body>hi</body>"
    ok, raw, comp = html_fits(html)
    assert ok
    assert raw < 100
    assert comp > 0
    assert pack_html(html) == html


def test_raw_overflow():
    html = "x" * 40000
    with pytest.raises(HtmlTooLargeError):
        assert_html_fits(html)


def test_zlib_overflow():
    html = "".join(chr(0x4e00 + i % 20000) for i in range(2500))
    with pytest.raises(HtmlTooLargeError):
        assert_html_fits(html)


def test_repetitive_html_compresses_well():
    html = "<div>" * 2000 + "</div>" * 2000
    assert_html_fits(html)

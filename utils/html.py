import zlib

HTML_RAW_MAX = 32768
HTML_ZLIB_MAX = 4096

_COMPRESSOR_LEVEL = 6


class HtmlTooLargeError(ValueError):
    def __init__(self, raw: int, compressed: int) -> None:
        super().__init__(
            f"widget html too large: raw={raw}B (max {HTML_RAW_MAX}), "
            f"zlib={compressed}B (max {HTML_ZLIB_MAX})"
        )
        self.raw = raw
        self.compressed = compressed


def html_fits(html: str) -> tuple[bool, int, int]:
    raw = html.encode("utf-8")
    raw_len = len(raw)
    if raw_len > HTML_RAW_MAX:
        return (False, raw_len, -1)
    comp_len = len(zlib.compress(raw, _COMPRESSOR_LEVEL))
    return (comp_len <= HTML_ZLIB_MAX, raw_len, comp_len)


def assert_html_fits(html: str) -> None:
    ok, raw, comp = html_fits(html)
    if not ok:
        raise HtmlTooLargeError(raw, comp)


def pack_html(html: str) -> str:
    assert_html_fits(html)
    return html

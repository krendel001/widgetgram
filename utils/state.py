STATE_FIELD_MAX = 1024


class StateTooLargeError(ValueError):
    def __init__(self, size: int) -> None:
        super().__init__(f"widget state too large: {size}B (max {STATE_FIELD_MAX})")
        self.size = size


def assert_state_fits(payload: str) -> None:
    size = len(payload.encode("utf-8"))
    if size > STATE_FIELD_MAX:
        raise StateTooLargeError(size)


__all__ = ["STATE_FIELD_MAX", "StateTooLargeError", "assert_state_fits"]

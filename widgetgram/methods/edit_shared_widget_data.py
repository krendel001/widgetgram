from typing import Any, ClassVar

from aiogram.methods.base import TelegramMethod

from ..utils.state import assert_state_fits


class EditSharedWidgetData(TelegramMethod[bool]):
    __returning__ = bool
    __api_method__: ClassVar[str] = "editSharedWidgetData"

    widget_id: str
    public_data: str
    cache_time: int | None = None

    def model_post_init(self, _: Any) -> None:
        assert_state_fits(self.public_data)

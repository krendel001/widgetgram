from typing import Any, ClassVar

from aiogram.methods.base import TelegramMethod

from ..utils.state import assert_state_fits


class EditMessageWidgetData(TelegramMethod[bool]):
    __returning__ = bool
    __api_method__: ClassVar[str] = "editMessageWidgetData"

    chat_id: int | str | None = None
    message_id: int | None = None
    inline_message_id: str | None = None
    public_data: str | None = None
    chat_data: str | None = None

    def model_post_init(self, _: Any) -> None:
        if self.chat_data is not None:
            assert_state_fits(self.chat_data)
        if self.public_data is not None:
            assert_state_fits(self.public_data)

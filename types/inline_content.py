from typing import Any

from aiogram.types import TelegramObject, MessageEntity

from ..utils.html import assert_html_fits
from ..utils.state import assert_state_fits


class InputWidgetMessageContent(TelegramObject):
    html: str
    width: int | None = None
    height: int | None = None
    public_data: str | None = None
    chat_data: str | None = None
    caption: str | None = None
    parse_mode: str | None = None
    caption_entities: list[MessageEntity] | None = None
    show_caption_above_media: bool | None = None
    allow_queries: bool | None = None
    is_shared: bool | None = None

    def model_post_init(self, _: Any) -> None:
        assert_html_fits(self.html)
        if self.chat_data is not None:
            assert_state_fits(self.chat_data)
        if self.public_data is not None:
            assert_state_fits(self.public_data)


class InputSharedWidgetMessageContent(TelegramObject):
    widget_id: str
    chat_data: str | None = None
    caption: str | None = None
    parse_mode: str | None = None
    caption_entities: list[MessageEntity] | None = None
    show_caption_above_media: bool | None = None

    def model_post_init(self, _: Any) -> None:
        if self.chat_data is not None:
            assert_state_fits(self.chat_data)

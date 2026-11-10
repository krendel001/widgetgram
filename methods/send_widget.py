from typing import Any, ClassVar, Union

from aiogram.methods.base import TelegramMethod
from aiogram.types import (
    Message,
    MessageEntity,
    ReplyParameters,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
)

from ..utils.html import assert_html_fits
from ..utils.state import assert_state_fits


class SendWidget(TelegramMethod[Message]):
    __returning__ = Message
    __api_method__: ClassVar[str] = "sendWidget"

    chat_id: int | str
    html: str
    message_thread_id: int | None = None
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
    disable_notification: bool | None = None
    protect_content: bool | None = None
    allow_paid_broadcast: bool | None = None
    message_effect_id: str | None = None
    reply_parameters: ReplyParameters | None = None
    reply_markup: Union[
        InlineKeyboardMarkup,
        ReplyKeyboardMarkup,
        ReplyKeyboardRemove,
        ForceReply,
        None,
    ] = None

    def model_post_init(self, _: Any) -> None:
        assert_html_fits(self.html)
        if self.chat_data is not None:
            assert_state_fits(self.chat_data)
        if self.public_data is not None:
            assert_state_fits(self.public_data)

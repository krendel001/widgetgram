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

from ..utils.state import assert_state_fits


class SendSharedWidget(TelegramMethod[Message]):
    __returning__ = Message
    __api_method__: ClassVar[str] = "sendSharedWidget"

    chat_id: int | str
    widget_id: str
    message_thread_id: int | None = None
    chat_data: str | None = None
    caption: str | None = None
    parse_mode: str | None = None
    caption_entities: list[MessageEntity] | None = None
    show_caption_above_media: bool | None = None
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
        if self.chat_data is not None:
            assert_state_fits(self.chat_data)

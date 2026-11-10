from typing import ClassVar

from aiogram.methods.base import TelegramMethod


class AnswerWidgetQuery(TelegramMethod[bool]):
    __returning__ = bool
    __api_method__: ClassVar[str] = "answerWidgetQuery"

    widget_query_id: str
    data: str | None = None

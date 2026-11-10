from typing import TYPE_CHECKING

from aiogram.types import TelegramObject, User, Chat
from pydantic import Field

from .query_type import WidgetQueryType

if TYPE_CHECKING:
    from ..methods.answer_widget_query import AnswerWidgetQuery


class WidgetQuery(TelegramObject):
    id: str
    from_user: User = Field(..., alias="from")
    chat: Chat | None = None
    message_id: int | None = None
    inline_message_id: str | None = None
    chat_instance: str
    chat_type: str | None = None
    type: WidgetQueryType
    data: str
    widget_id: str | None = None

    def answer(self, data: str | None = None) -> "AnswerWidgetQuery":
        from ..methods.answer_widget_query import AnswerWidgetQuery
        method = AnswerWidgetQuery(widget_query_id=self.id, data=data)
        return method.as_(self.bot) if self.bot else method

    async def ack(self, data: str | None = None) -> bool:
        if self.bot is None:
            raise RuntimeError("WidgetQuery is not bound to a Bot")
        return await self.bot(self.answer(data))

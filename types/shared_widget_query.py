from typing import TYPE_CHECKING

from aiogram.types import TelegramObject, User
from pydantic import Field

from .query_type import WidgetQueryType

if TYPE_CHECKING:
    from ..methods.answer_widget_query import AnswerWidgetQuery


class SharedWidgetQuery(TelegramObject):
    id: str
    from_user: User = Field(..., alias="from")
    type: WidgetQueryType
    data: str
    widget_id: str

    def answer(self, data: str | None = None) -> "AnswerWidgetQuery":
        from ..methods.answer_widget_query import AnswerWidgetQuery
        method = AnswerWidgetQuery(widget_query_id=self.id, data=data)
        return method.as_(self.bot) if self.bot else method

    async def ack(self, data: str | None = None) -> bool:
        if self.bot is None:
            raise RuntimeError("SharedWidgetQuery is not bound to a Bot")
        return await self.bot(self.answer(data))

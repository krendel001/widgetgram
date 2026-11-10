import json
from typing import Any

from aiogram import Bot
from aiogram.types import Message

from .methods import SendWidget
from .state import StateStorage
from .types import Widget


async def send_widget(
    bot: Bot,
    chat_id: int,
    html: str,
    state: dict[str, Any] | None = None,
    *,
    storage: StateStorage | None = None,
    public_data: str | None = None,
    allow_queries: bool = True,
    is_shared: bool = False,
    **extra: Any,
) -> Message:
    chat_data = None
    if state is not None:
        chat_data = json.dumps(state, separators=(",", ":"), ensure_ascii=False)
    msg = await bot(SendWidget(
        chat_id=chat_id,
        html=html,
        chat_data=chat_data,
        public_data=public_data,
        allow_queries=allow_queries,
        is_shared=is_shared,
        **extra,
    ))
    if storage is not None and state is not None:
        await storage.put(chat_id, msg.message_id, state)
    return msg


def get_widget(msg: Message) -> Widget | None:
    data = None
    extra = getattr(msg, "model_extra", None)
    if extra is not None:
        data = extra.get("widget")
    if data is None:
        data = getattr(msg, "widget", None)
    if data is None:
        return None
    if isinstance(data, Widget):
        return data
    return Widget.model_validate(data)


__all__ = ["send_widget", "get_widget"]

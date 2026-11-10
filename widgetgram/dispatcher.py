import copy
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot, Dispatcher as _AiogramDispatcher

from .methods import AnswerWidgetQuery
from .router import WIDGET_QUERY, SHARED_WIDGET_QUERY, Router
from .state import MemoryStateStorage, StateStorage, push_state
from .types import SharedWidgetQuery, WidgetQuery

log = logging.getLogger("widgetgram")


class _StateMiddleware(BaseMiddleware):
    def __init__(self, storage: StateStorage) -> None:
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: WidgetQuery,
        data: dict[str, Any],
    ) -> Any:
        if event.chat is None or event.message_id is None:
            data["state"] = {}
            return await handler(event, data)
        chat_id, message_id = event.chat.id, event.message_id
        before = await self.storage.get(chat_id, message_id) or {}
        state = copy.deepcopy(before)
        data["state"] = state
        result = await handler(event, data)
        if state != before:
            bot: Bot | None = data.get("bot")
            if bot is not None:
                await push_state(bot, chat_id, message_id, state)
            await self.storage.put(chat_id, message_id, state)
        return result


class _AutoAckMiddleware(BaseMiddleware):
    def __init__(self, data: str | None = None) -> None:
        self.data = data

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: WidgetQuery | SharedWidgetQuery,
        data: dict[str, Any],
    ) -> Any:
        bot: Bot | None = data.get("bot")
        if bot is not None:
            try:
                await bot(AnswerWidgetQuery(widget_query_id=event.id, data=self.data))
            except Exception as e:  # noqa: BLE001
                log.warning("answerWidgetQuery failed for %s: %s", event.id, e)
        return await handler(event, data)


class Dispatcher(_AiogramDispatcher):
    def __init__(
        self,
        *,
        state_storage: StateStorage | None = None,
        auto_ack: bool = True,
        auto_ack_data: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.state_storage = state_storage or MemoryStateStorage()
        self._own_router = Router(name="widgetgram")
        self.observers[WIDGET_QUERY] = self._own_router.widget_query
        self.observers[SHARED_WIDGET_QUERY] = self._own_router.shared_widget_query
        self._own_router.widget_query.outer_middleware(_StateMiddleware(self.state_storage))
        if auto_ack:
            mw = _AutoAckMiddleware(auto_ack_data)
            self._own_router.widget_query.outer_middleware(mw)
            self._own_router.shared_widget_query.outer_middleware(mw)

    @property
    def widget_query(self):
        return self._own_router.widget_query

    @property
    def shared_widget_query(self):
        return self._own_router.shared_widget_query

    async def feed_raw_update(self, bot: Bot, update: dict[str, Any], **kwargs: Any) -> Any:
        if isinstance(update, dict):
            if WIDGET_QUERY in update:
                return await self._dispatch_widget(
                    bot, update, WIDGET_QUERY, WidgetQuery, **kwargs
                )
            if SHARED_WIDGET_QUERY in update:
                return await self._dispatch_widget(
                    bot, update, SHARED_WIDGET_QUERY, SharedWidgetQuery, **kwargs
                )
        return await super().feed_raw_update(bot, update, **kwargs)

    async def _dispatch_widget(
        self,
        bot: Bot,
        raw: dict[str, Any],
        update_type: str,
        cls: type,
        **kwargs: Any,
    ) -> Any:
        event = cls.model_validate(raw[update_type], context={"bot": bot})
        return await self.propagate_event(
            update_type=update_type,
            event=event,
            dispatcher=self,
            bot=bot,
            **self.workflow_data,
            **kwargs,
        )


__all__ = ["Dispatcher"]

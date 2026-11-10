from aiogram import Router as _AiogramRouter
from aiogram.dispatcher.event.telegram import TelegramEventObserver

WIDGET_QUERY = "widget_query"
SHARED_WIDGET_QUERY = "shared_widget_query"


class Router(_AiogramRouter):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name=name)
        self.widget_query = TelegramEventObserver(router=self, event_name=WIDGET_QUERY)
        self.shared_widget_query = TelegramEventObserver(
            router=self, event_name=SHARED_WIDGET_QUERY
        )
        self.observers[WIDGET_QUERY] = self.widget_query
        self.observers[SHARED_WIDGET_QUERY] = self.shared_widget_query


__all__ = ["Router", "WIDGET_QUERY", "SHARED_WIDGET_QUERY"]

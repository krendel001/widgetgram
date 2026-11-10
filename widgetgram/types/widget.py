from aiogram.types import TelegramObject


class Widget(TelegramObject):
    id: str | None = None
    width: int | None = None
    height: int | None = None
    html: str
    public_data: str | None = None
    chat_data: str | None = None

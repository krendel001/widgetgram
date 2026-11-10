from aiogram.types import TelegramObject, UniqueGift


class TonNftAttribute(TelegramObject):
    trait_type: str
    value: str


class TonNft(TelegramObject):
    address: str
    index: str
    name: str
    description: str
    collection_address: str | None = None
    attributes: list[TonNftAttribute] | None = None
    gift: UniqueGift | None = None

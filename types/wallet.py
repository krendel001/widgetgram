from aiogram.types import TelegramObject

from .area_position import AreaPosition
from .ton_nft import TonNft


class WidgetQueryWallet(TelegramObject):
    address: str
    amount: str
    public_key: str | None = None
    state_init: str | None = None


class TonWalletCardSticker(TelegramObject):
    position: AreaPosition
    nft: TonNft


class TonWalletCard(TelegramObject):
    address: str
    amount: str
    stickers: list[TonWalletCardSticker]
    background_nft_address: str | None = None

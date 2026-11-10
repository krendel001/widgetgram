from typing import Annotated, Literal, Union

from aiogram.types import TelegramObject
from pydantic import Field

from .wallet import TonWalletCard, WidgetQueryWallet


class WidgetQueryTypeData(TelegramObject):
    type: Literal["data"] = "data"
    wallet_card: TonWalletCard | None = None


class WidgetQueryTypeSignData(TelegramObject):
    type: Literal["sign_data"]
    wallet: WidgetQueryWallet
    sign_data: str


class WidgetQueryTypeSentTransaction(TelegramObject):
    type: Literal["sent_transaction"]
    wallet: WidgetQueryWallet
    msg_hash: str


WidgetQueryType = Annotated[
    Union[
        WidgetQueryTypeData,
        WidgetQueryTypeSignData,
        WidgetQueryTypeSentTransaction,
    ],
    Field(discriminator="type"),
]

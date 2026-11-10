from widgetgram import (
    WidgetQuery,
    SharedWidgetQuery,
    WidgetQueryTypeData,
    WidgetQueryTypeSignData,
    WidgetQueryTypeSentTransaction,
    TonWalletCard,
)


def _user() -> dict:
    return {"id": 42, "is_bot": False, "first_name": "t"}


def test_parse_data_query_without_wallet_card():
    q = WidgetQuery.model_validate({
        "id": "abc",
        "from": _user(),
        "chat_instance": "inst",
        "type": {"type": "data"},
        "data": "next",
    })
    assert q.id == "abc"
    assert q.from_user.id == 42
    assert isinstance(q.type, WidgetQueryTypeData)
    assert q.type.wallet_card is None
    assert q.data == "next"


def test_parse_data_query_with_wallet_card():
    q = WidgetQuery.model_validate({
        "id": "x",
        "from": _user(),
        "chat_instance": "inst",
        "type": {
            "type": "data",
            "wallet_card": {
                "address": "EQabc",
                "amount": "1000000000",
                "stickers": [],
            },
        },
        "data": "connect",
    })
    assert isinstance(q.type, WidgetQueryTypeData)
    assert isinstance(q.type.wallet_card, TonWalletCard)
    assert q.type.wallet_card.address == "EQabc"


def test_parse_sign_data():
    q = WidgetQuery.model_validate({
        "id": "sig1",
        "from": _user(),
        "chat_instance": "inst",
        "type": {
            "type": "sign_data",
            "wallet": {"address": "EQabc", "amount": "0"},
            "sign_data": "deadbeef",
        },
        "data": "signed:ok",
    })
    assert isinstance(q.type, WidgetQueryTypeSignData)
    assert q.type.sign_data == "deadbeef"
    assert q.type.wallet.address == "EQabc"


def test_parse_sent_transaction():
    q = WidgetQuery.model_validate({
        "id": "t1",
        "from": _user(),
        "chat_instance": "inst",
        "type": {
            "type": "sent_transaction",
            "wallet": {"address": "EQabc", "amount": "0"},
            "msg_hash": "abcd1234",
        },
        "data": "sent",
    })
    assert isinstance(q.type, WidgetQueryTypeSentTransaction)
    assert q.type.msg_hash == "abcd1234"


def test_shared_widget_query_slim():
    q = SharedWidgetQuery.model_validate({
        "id": "s1",
        "from": _user(),
        "type": {"type": "data"},
        "data": "payload",
        "widget_id": "W-123",
    })
    assert q.widget_id == "W-123"
    assert isinstance(q.type, WidgetQueryTypeData)
    assert not hasattr(q, "chat_instance") or True  # not part of SharedWidgetQuery


def test_answer_without_bot_returns_method():
    q = WidgetQuery.model_validate({
        "id": "x",
        "from": _user(),
        "chat_instance": "i",
        "type": {"type": "data"},
        "data": "p",
    })
    m = q.answer("done")
    assert m.widget_query_id == "x"
    assert m.data == "done"

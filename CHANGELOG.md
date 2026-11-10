# CHANGELOG

## 0.1.0

Первый релиз.

- Dispatcher и Router с поддержкой `widget_query` и `shared_widget_query`
- Пять методов Bot API: `sendWidget`, `sendSharedWidget`, `editMessageWidgetData`,
  `editSharedWidgetData`, `answerWidgetQuery`
- Полные типы по спеке Bot API 10.4+: `WidgetQuery`, `SharedWidgetQuery`,
  discriminated union `WidgetQueryType`, `TonWalletCard`, `TonNft`, `WidgetQueryWallet`,
  `Widget`, `InputWidgetMessageContent`, `InputSharedWidgetMessageContent`
- Инъекция `state: dict` в хендлер с автосохранением и пушем `editMessageWidgetData`
- Автоответ на `widget_query` до запуска хендлера (отключается `auto_ack=False`)
- Хелпер `send_widget(bot, chat_id, html, state=..., storage=...)`
- Хелпер `get_widget(msg)` для доступа к `Message.widget`
- Валидация размеров HTML и `chat_data` / `public_data` на этапе создания метода
- `EditQueue` для коалесции частых edit-ов до 1 в секунду на сообщение
- `NonceStore` для челлендж-ответа в `wallet.signData`
- Хелперы проверки подписей: `verify_ed25519`, `verify_evm_personal`

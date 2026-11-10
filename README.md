# widgetgram

Виджеты Telegram (Bot API 10.4+) для aiogram 3.

Это тот же стиль, что у aiogram: `Dispatcher`, `Router`, декораторы на фильтрах.
Добавляется приём `widget_query`, типы `WidgetQuery` / `SharedWidgetQuery`, пять
методов Bot API (`sendWidget`, `editMessageWidgetData` и прочие), и несколько
удобств: автоответ на запрос, инъекция состояния в хендлер, валидация размеров.

## Установка

```
pip install widgetgram
```

Опциональные зависимости:

```
pip install widgetgram[ed25519]   # проверка подписей TON / Solana
pip install widgetgram[evm]       # проверка подписей EVM через eth-account
```

## Минимальный пример

```python
import asyncio
from aiogram import Bot, F
from aiogram.filters import Command
import widgetgram as wg

HTML = """<!doctype html>
<button id=b>tap</button>
<script>
var W = window.TelegramWidget;
document.getElementById('b').onclick = () => W.request('hello');
W.ready && W.ready();
</script>"""

dp = wg.Dispatcher()

@dp.message(Command("start"))
async def start(msg, bot):
    await wg.send_widget(bot, msg.chat.id, HTML)

@dp.widget_query(F.data == "hello")
async def on_hello(q):
    await q.bot.send_message(q.chat.id, f"привет, {q.from_user.first_name}")

async def main():
    bot = Bot("TOKEN")
    await dp.start_polling(bot)

asyncio.run(main())
```

Запускаешь бота, пишешь `/start`, тапаешь кнопку в виджете. Готово.

## Состояние

Виджет держит кусок JSON в поле `chat_data` на стороне Telegram. Когда
приходит `widget_query`, Telegram не присылает это поле обратно, поэтому
библиотека хранит состояние у себя и кладёт его в хендлер как `state`.

```python
@dp.message(Command("start"))
async def start(msg, bot):
    await wg.send_widget(
        bot, msg.chat.id, HTML,
        state={"counter": 0},
        storage=dp.state_storage,
    )

@dp.widget_query(F.data == "inc")
async def on_inc(q, state):
    state["counter"] += 1
```

Что происходит внутри:

1. До хендлера middleware подтягивает состояние из хранилища по
   `(chat_id, message_id)`.
2. Хендлер меняет словарь как обычно.
3. После хендлера библиотека сравнивает словарь со снимком до вызова, и если
   он поменялся, вызывает `editMessageWidgetData` и обновляет хранилище.

По умолчанию хранилище in-memory. Для продакшена напишешь свой, реализовав
протокол `wg.StateStorage` (get/put/drop).

## Автоответ на widget_query

У бота есть 15 секунд, чтобы вызвать `answerWidgetQuery`, иначе промис
`W.request()` на клиенте зависнет. Библиотека отвечает за тебя автоматически
перед хендлером. Отключить можно так:

```python
dp = wg.Dispatcher(auto_ack=False)
```

Тогда пиши сам:

```python
await q.answer("done")   # вернёт данные обратно в W.request().then(...)
```

## Фильтры

Используй стандартный `aiogram.F`, как с обычными сообщениями:

```python
@dp.widget_query(F.data == "next")
@dp.widget_query(F.data.startswith("w:"))
@dp.widget_query(F.data.regexp(r"^len:(12|24)$"))
@dp.widget_query(F.from_user.id == 12345)
@dp.widget_query(F.chat.type == "private")
```

## Платёжные запросы

Telegram кладёт три разных типа виджет-запросов в поле `q.type`:

- `WidgetQueryTypeData` = обычный `W.request(str)` от юзера
- `WidgetQueryTypeSignData` = результат `wallet.signData(message)`
- `WidgetQueryTypeSentTransaction` = результат `wallet.sendTransaction(...)`

Удобно разбирать через match:

```python
from widgetgram import (
    WidgetQueryTypeData,
    WidgetQueryTypeSignData,
    WidgetQueryTypeSentTransaction,
)

@dp.widget_query()
async def router(q):
    match q.type:
        case WidgetQueryTypeData(wallet_card=card) if card:
            await q.bot.send_message(q.chat.id, f"кошелёк: {card.address}")
        case WidgetQueryTypeSignData(wallet=w, sign_data=sig):
            await verify_and_login(q, w, sig)
        case WidgetQueryTypeSentTransaction(wallet=w, msg_hash=h):
            await q.bot.send_message(q.chat.id, f"tx {h}")
```

## Shared widget (один виджет на несколько чатов)

```python
msg = await wg.send_widget(bot, chat_id, HTML, is_shared=True)
widget_id = wg.get_widget(msg).id

# пересылаешь копии в другие чаты
await bot(wg.SendSharedWidget(chat_id=other, widget_id=widget_id))

# обновляешь public_data во всех копиях сразу
await bot(wg.EditSharedWidgetData(
    widget_id=widget_id,
    public_data='{"price": 5000}',
    cache_time=30,
))

# запрос из shared-виджета придёт как shared_widget_query
@dp.shared_widget_query()
async def on_shared(q):
    print(q.widget_id, q.data)
```

## Методы Bot API

Все пять методов есть как типизированные классы, вызываются стандартно через `await bot(...)`:

```python
from widgetgram import (
    SendWidget, SendSharedWidget,
    EditMessageWidgetData, EditSharedWidgetData,
    AnswerWidgetQuery,
)
```

Параметры совпадают с Bot API один в один, включая `width`, `height`,
`caption`, `reply_markup`, `message_effect_id` и так далее. Размер HTML и
размеры `chat_data` / `public_data` валидируются в момент создания объекта,
поэтому `HtmlTooLargeError` / `StateTooLargeError` ты получишь ещё до
похода в API.

## Проверка подписей

Внутри `widgetgram.utils.signatures`:

```python
from widgetgram.utils import signatures

# TON / Solana = ed25519
ok = signatures.verify_ed25519(
    public_key=wallet.public_key,
    message=challenge,
    signature=q.type.sign_data,
)

# EVM = EIP-191 personal_sign
ok = signatures.verify_evm_personal(
    address=wallet.address,
    message=challenge,
    signature=q.type.sign_data,
)
```

Какой именно префикс кладёт Telegram под подпись в проде, в официальных
доках сейчас не описано. Хелперы `ton_safe_message`, `solana_offchain_message`,
`evm_personal_hash` лежат в этом же модуле на случай ручной сверки.

## Nonce для signData

Если делаешь челлендж-ответ (бот выдаёт случайную строку, виджет её подписывает):

```python
nonces = wg.NonceStore(ttl=300)

@dp.widget_query(F.data == "connect")
async def on_connect(q):
    await q.answer(f"challenge:{nonces.issue(q.chat.id)}")
    # виджет подписывает challenge через wallet.signData

@dp.widget_query()
async def on_sign(q):
    if isinstance(q.type, wg.WidgetQueryTypeSignData):
        if nonces.consume(q.chat.id, q.data):
            await complete_login(q)
```

## Rate limit на edit-ы

`editMessageWidgetData` можно звать примерно раз в секунду на сообщение.
Если есть риск спамить (например пушишь живой курс), используй `EditQueue`:

```python
eq = wg.EditQueue(min_interval=1.1)

def on_tick(chat_id, message_id, state):
    eq.push(
        key=("msg", chat_id, message_id),
        sender=lambda: wg.push_state(bot, chat_id, message_id, state),
    )
```

Последний пуш выигрывает, промежуточные отбрасываются. При завершении бота:

```python
await eq.flush()
eq.close()
```

## Лимиты (автоматически проверяются где можно)

| Что | Лимит |
|---|---|
| HTML виджета | 32768 байт сырого, 4096 после zlib |
| chat_data / public_data | 1024 байта на поле |
| W.request payload | 1 до 64 байт |
| widget_query с юзера | 5 за 5 секунд |
| editMessageWidgetData | около 1 в секунду на сообщение |
| editSharedWidgetData | около 1 в секунду на widget_id |
| answerWidgetQuery deadline | 15 секунд |

## Message.widget

`aiogram` пока не знает про поле `widget` в `Message`, оно остаётся в
`model_extra`. Есть хелпер:

```python
w = wg.get_widget(msg)   # Widget | None
if w:
    print(w.id, len(w.html))
```

## Разработка

```
git clone https://github.com/yourname/widgetgram
cd widgetgram
pip install -e .[dev,ed25519,evm]
pytest widgetgram/tests
```

## Лицензия

MIT.

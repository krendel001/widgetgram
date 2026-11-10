"""
Простой пример счётчика. Нажимаешь кнопку - число растёт.

Запуск:
    pip install widgetgram
    BOT_TOKEN=... python -m widgetgram.examples.counter
"""
import asyncio
import os

from aiogram import Bot, F
from aiogram.filters import Command
from aiogram.types import Message

import widgetgram as wg

HTML = """<!doctype html>
<style>
  body { font: 24px -apple-system, sans-serif; text-align: center; padding: 40px 10px; }
  button { font: 20px inherit; padding: 12px 24px; border-radius: 10px;
           border: 0; background: #b5a0ff; color: #171220; cursor: pointer; }
  #n { font-size: 56px; font-weight: 700; margin: 20px 0; }
</style>
<div id=n>0</div>
<button id=plus>+1</button>
<button id=reset>reset</button>
<script>
var W = window.TelegramWidget;
function render() {
  var s = {}; try { s = JSON.parse(W.chatData || '{}'); } catch(e) {}
  document.getElementById('n').textContent = s.counter || 0;
}
document.getElementById('plus').onclick = () => W.request('inc');
document.getElementById('reset').onclick = () => W.request('reset');
W.onEvent && W.onEvent('chatDataChanged', render);
render();
W.ready && W.ready();
</script>
"""

dp = wg.Dispatcher()


@dp.message(Command("start"))
async def start(msg: Message, bot: Bot) -> None:
    await wg.send_widget(
        bot, msg.chat.id, HTML,
        state={"counter": 0},
        storage=dp.state_storage,
    )


@dp.widget_query(F.data == "inc")
async def on_inc(q: wg.WidgetQuery, state: dict) -> None:
    state["counter"] = state.get("counter", 0) + 1


@dp.widget_query(F.data == "reset")
async def on_reset(q: wg.WidgetQuery, state: dict) -> None:
    state["counter"] = 0


async def main() -> None:
    bot = Bot(token=os.environ["BOT_TOKEN"])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

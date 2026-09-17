import os
import asyncio
import aiohttp

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


TOKEN = os.getenv("BOT_TOKEN")
WB_ARTICLE = "550374906"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот мониторинга RTX 50 работает!\n\n"
        "/check — проверить цену RTX 50\n"
        "/status — статус бота"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Бот работает.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Получаю цену Wildberries...")

    url = (
        "https://card.wb.ru/cards/v4/detail"
        "?appType=1&curr=rub&dest=-1257786"
        f"&nm={WB_ARTICLE}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:

                if response.status != 200:
                    await update.message.reply_text(
                        f"❌ WB вернул HTTP {response.status}"
                    )
                    return

                data = await response.json()

        products = data.get("products", [])

        if not products:
            await update.message.reply_text(
                "❌ Товар не найден в ответе WB."
            )
            return

        product = products[0]
        name = product.get("name", "Без названия")

        prices = []

        for size in product.get("sizes", []):
            price = size.get("price", {})

            if isinstance(price, dict):
                value = price.get("total") or price.get("product")

                if value:
                    prices.append(value)

        if not prices:
            await update.message.reply_text(
                f"📦 {name}\n\n"
                "⚠️ Цена не найдена в ответе WB."
            )
            return

        price = min(prices) / 100

        await update.message.reply_text(
            f"📦 {name}\n\n"
            f"💰 Цена WB: {price:,.0f} ₽\n"
            f"🔢 Артикул: {WB_ARTICLE}\n"
            f"🔗 https://www.wildberries.ru/catalog/{WB_ARTICLE}/detail.aspx"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при получении цены:\n{e}"
        )


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

from telegram import Update, InputFile, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from io import BytesIO
import os
import re
from dotenv import load_dotenv
import logging
from enkacard import encbanner
import aiohttp
import asyncio

logging.getLogger().setLevel(logging.CRITICAL)
load_dotenv()

token = os.getenv("TOKEN")
BOT_USERNAME = "@ManukaAI_Bot"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Support me on :  \nhttps://www.paypal.me/ardha27\nhttps://saweria.co/ardha27"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type something so i can respond")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is custom command")


def is_numeric(text):
    # Use a regular expression to check if the text consists only of digits
    return bool(re.match(r"^\d+$", text))


async def card():
    try:
        async with encbanner.ENC(lang="en") as encard:
            ENCpy = await encard.enc(uids="800098474")
            return await encard.creat(ENCpy, 2)
    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        print(f"An error occurred: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
        else:
            return
    elif message_type == "private":
        if is_numeric(text):
            result = await card()
            if result:
                photo_list = []  # Create a list to store the images

                # Iterate through the received data and add images to the list
                for uid, character_data in result.items():
                    for character_name, character_info in character_data.items():
                        img = character_info["img"]

                        # Convert the PIL image to bytes
                        img_bytes = BytesIO()
                        img.save(img_bytes, format="PNG")
                        img_bytes.seek(0)

                        photo_list.append(InputMediaPhoto(media=img_bytes))
                try:
                    await update.message.reply_media_group(media=photo_list)
                except Exception as e:
                    await update.message.reply_text(f"An error occurred: {e}")

            else:
                await update.message.reply_text("An error occurred. Please try again.")
        else:
            await update.message.reply_text("Please send your Genshin UID")
            return


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=3)

from ssl import SSLError
from typing import NoReturn
from pyrogram import filters
from pyrogram.methods.utilities.idle import idle
from pyrogram.client import Client
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pytube.exceptions import RegexMatchError
from bot.youtube import (
    AudioQuality,
    VideoQuality,
    YouTubeDownloader
)

from config.config import (
    TELEGRAM_BOT_API_HASH,
    TELEGRAM_BOT_API_ID,
    TELEGRAM_BOT_NAME,
    TELEGRAM_BOT_TOKEN
)
from constants.strings import (
    HELP_MESSAGE,
    INVALID_URL_WARNING,
    SOMETHING_WENT_WRONG_MESSAGE,
    START_MESSAGE,
    USAGE_MESSAGE,
)

# Main

app = Client(
    TELEGRAM_BOT_NAME,
    api_id=TELEGRAM_BOT_API_ID,
    api_hash=TELEGRAM_BOT_API_HASH,
    bot_token=TELEGRAM_BOT_TOKEN,

)

# ? --------------------------- Start Command ---------------------------


@app.on_message(filters.text & filters.command("start") & filters.private)
async def start_command(client: Client, message: Message) -> NoReturn:
    await message.reply(START_MESSAGE, disable_web_page_preview=True)


# ? --------------------------- Help Command ---------------------------
@app.on_message(filters.text & filters.command("help") & filters.private)
async def help_command(client: Client, message: Message) -> NoReturn:
    await message.reply(HELP_MESSAGE, disable_web_page_preview=True)


@app.on_message(filters.text & filters.private)
async def handel_message(client: Client, message: Message):
    print(f"New message received from @{message.chat.username}")

    url: str = message.text.strip()
    try:
        video_id = YouTubeDownloader.extract_video_id(url)
    except RegexMatchError:
        await message.reply(
            INVALID_URL_WARNING + "\n\n" + USAGE_MESSAGE,
            disable_web_page_preview=True
        )
        return

    # Send inline buttons asking for audio or video
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Audio", callback_data=f"audio_{video_id}"),
        InlineKeyboardButton("Video", callback_data=f"video_{video_id}")
    ]])

    await message.reply("Do you want to download audio or video?", reply_markup=keyboard)


@app.on_callback_query()
async def on_callback_query(client: Client, callback_query: CallbackQuery) -> NoReturn:
    # Split into at most 3 parts
    choice, *parts = str(callback_query.data).split("_")

    print(f"From user @{callback_query.from_user.username} {parts}")

    if len(parts) == 1 and choice in ("audio", "video"):
        # If there are only 2 parts, it means the format is "choice_videoId"
        video_id = parts[0]
        # Send inline buttons for audio quality selection
        keyboard = _get_quality_keyboard(choice, video_id)

        await callback_query.message.edit_text(f"Select {choice} quality:", reply_markup=keyboard)

    elif len(parts) == 2 and choice in ("audio", "video"):
        # If there are 3 parts, it means the format is "choice_quality_videoId"
        quality, video_id = parts[0], parts[1]
        url = YouTubeDownloader.get_url_from_id(video_id)

        new_message = await callback_query.message.reply_text(f"Downloading {choice} at {quality} quality...")

        print(f"Processing - \"{url}\"")

        try:
            ytd = YouTubeDownloader(url)
            file = await download(callback_query.message, new_message, choice, quality, ytd)
            await send_file(callback_query.message, new_message, choice, file)

        except RegexMatchError as e:
            print("Invalid URL")
            await callback_query.message.reply(INVALID_URL_WARNING)

        finally:
            print(f"Deleting {choice} file...")
            ytd.close()

    else:
        # Handle unexpected format
        await callback_query.message.reply_text("Invalid request format.\n\n" + USAGE_MESSAGE)


def _get_quality_keyboard(choice, video_id):
    quality_buttons = [
        InlineKeyboardButton(
            quality.name, callback_data=f"{choice}_{quality.value}_{video_id}")
        for quality in (AudioQuality if choice == "audio" else VideoQuality)
    ]
    return InlineKeyboardMarkup([quality_buttons])


async def send_file(message: Message, new_message: Message, choice: str, file: str | None) -> str | None:
    if file:
        print(f"Sending {choice} file...")
        await new_message.edit_text(f"Uploading {choice}")
        await (message.reply_audio(file) if choice == "audio" else message.reply_video(file))
        await new_message.delete()
    else:
        print(f"{choice} not downloaded")
        await new_message.edit_text("Coudn't download the video")


async def download(message: Message, new_message: Message, choice: str, quality: str, ytd: YouTubeDownloader) -> str | None:
    try:
        print(f"Downloading {choice} file...")

        if choice == "audio":
            return ytd.download_audio(
                quality=AudioQuality[quality.upper()])
        else:
            return ytd.download_video(quality=VideoQuality[f"_{quality}"])

    except SSLError as e:
        print(f"There was a SSL error:\n{e.strerror}")
        await new_message.edit_text(SOMETHING_WENT_WRONG_MESSAGE)

    except Exception as e:
        print(f"There was an error:\n{e}")
        await new_message.edit_text(SOMETHING_WENT_WRONG_MESSAGE)


async def run_bot() -> NoReturn:
    print("Starting bot...")
    await app.start()
    print("Bot started...")

    print("Bot is running...")
    await idle()

    print("\nStopping bot...")
    await app.stop()
    print("Bot stopped...")

def start_bot():
    app.run(run_bot())
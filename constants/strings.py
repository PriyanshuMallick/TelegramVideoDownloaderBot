from typing import Final

USAGE_MESSAGE: Final = """*Usage:* YouTube_Link

Example: https://youtu.be/dQw4w9WgXcQ
"""

HELP_MESSAGE: Final = USAGE_MESSAGE + """\n
Commands:
⚪ /start - Start the bot
⚪ /help - Show help
"""

START_MESSAGE: Final = "Hello! I'm a YouTube Downloader Bot\n\n" + HELP_MESSAGE

INVALID_URL_WARNING: Final = """**_INVALID URL_**

Please provide a valid YouTube link.
"""

SOMETHING_WENT_WRONG_MESSAGE: Final = "Something went wrong while processing your request.\nPlease try again later."

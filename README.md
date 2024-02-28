# Telegram Youtube Downloader Bot

This repository contains a Telegram bot that allows users to download videos and audio from YouTube directly through Telegram messages.

## Features:

- Download videos in various resolutions (240p, 360p, 480p, 720p, 1080p)
- Download audio in various qualities (Best, Medium, Low)
- Automatic quality selection if the requested one is unavailable
<!-- - Progress bar during the download -->

## Requirements:

- Python 3.x
- Pyrogram library
- pyTube library
- python-dotenv library
- TgCrypto library

## Installation:

1. Clone this repository.
2. Install the required libraries: `pip install -r requirements.txt`
3. Create a Telegram bot using the BotFather and obtain your bot token.
4. Make a `.env` file using the `example.env` as an example.

## Usage:

1. Send the bot a message containing the URL of the YouTube video you want to download.
2. Choose the desired video quality from the provided options.
3. The bot will download the video and send you a notification when it's complete.

## Disclaimer:

This bot is intended for educational and personal use only. Downloading copyrighted content without permission is illegal. Please respect intellectual property rights.

## Contributions:

Feel free to contribute to this project by creating pull requests with improvements, bug fixes, or new features.

## License:

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

## Additional Notes:

- You can customize the bot's messages and behavior by editing the code in the `bot/telegram.py` file.
- Remember to run the bot using `python ./bot.py` after making any changes.
- This is a basic example, and you can add more features and functionalities to the bot as needed.

I hope this README file provides all the necessary information for you to use and contribute to this Telegram video downloader bot!

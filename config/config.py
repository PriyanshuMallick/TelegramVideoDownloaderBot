import os
from dotenv import load_dotenv
from typing import Final


def get_env_value(env_name: str, default: str | None = None) -> str:
    env_value = os.getenv(env_name, default)
    if env_value is None:
        print(f"Environment variable {env_name} not found")
        exit()

    return env_value


load_dotenv()


TELEGRAM_BOT_USERNAME: Final = get_env_value('TELEGRAM_BOT_USERNAME')
TELEGRAM_BOT_NAME: Final = get_env_value('TELEGRAM_BOT_NAME')
TELEGRAM_BOT_TOKEN: Final = get_env_value('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_API_ID: Final = int(get_env_value('TELEGRAM_BOT_API_ID'))
TELEGRAM_BOT_API_HASH: Final = get_env_value('TELEGRAM_BOT_API_HASH')

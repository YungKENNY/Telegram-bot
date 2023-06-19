from environs import Env
from dataclasses import dataclass

@dataclass
class Settings:
    bot_token: str
    admin_ids: list
    schedule_folser_url: str

def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bot_token=env.str('TOKEN'),
        admin_ids=env.list('ADMIN_IDS'),
        schedule_folser_url=env.str('SCHEDULE_FOLDER_LINK')
    )

settings = get_settings('data')
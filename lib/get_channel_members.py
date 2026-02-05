import hashlib
import os

from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TERMIN_RADAR_TELEGRAM_SESSION = os.getenv("TERMIN_RADAR_TELEGRAM_SESSION")
ENCRYPTION_SALT = os.getenv("ENCRYPTION_SALT")


def get_channel_members(channel_id):
    with TelegramClient(StringSession(TERMIN_RADAR_TELEGRAM_SESSION),
                        TELEGRAM_API_ID,
                        TELEGRAM_API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN) as client:
        participants = []
        offset = 0
        limit = 100
        while True:
            users = client(GetParticipantsRequest(channel=channel_id,
                                                  filter=ChannelParticipantsSearch(''),
                                                  offset=offset,
                                                  limit=limit,
                                                  hash=0)).users
            if not users:
                break
            participants.extend(users)
            offset += len(users)
        return [hashlib.md5(f"{ENCRYPTION_SALT}-{participant.id}".encode()).hexdigest() for participant in participants]

import os
import hashlib

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_channel_members(channel_id):
    with TelegramClient('termin_radar', TELEGRAM_API_ID, TELEGRAM_API_HASH).start(
            bot_token=TELEGRAM_BOT_TOKEN) as client:
        participants = client(
            GetParticipantsRequest(channel=channel_id, filter=ChannelParticipantsSearch(''), offset=0, limit=100,
                hash=0)).users
        return [hashlib.md5(str(user.id).encode()).hexdigest() for user in participants]

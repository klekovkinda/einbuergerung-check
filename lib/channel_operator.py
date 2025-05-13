import hashlib
import os

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, DeleteMessagesRequest
from telethon.tl.types import ChannelParticipantsSearch

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")


def get_channel_members(channel_id):
    with TelegramClient('termin_radar', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        participants = client(
            GetParticipantsRequest(channel=channel_id, filter=ChannelParticipantsSearch(''), offset=0, limit=100,
                                   hash=0)).users
        return [hashlib.md5(str(user.id).encode()).hexdigest() for user in participants]


def delete_unpinned_messages(channel_id):
    with TelegramClient('termin_radar', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        offset_id = 0
        while True:
            history = client(
                GetHistoryRequest(peer=channel_id, offset_id=offset_id, offset_date=None, add_offset=0, limit=100,
                                  max_id=0, min_id=0, hash=0))
            messages = history.messages
            if not messages:
                break

            unpinned_message_ids = [msg.id for msg in messages if not msg.pinned]
            if unpinned_message_ids:
                client(DeleteMessagesRequest(id=unpinned_message_ids))

            offset_id = messages[-1].id if messages else 0

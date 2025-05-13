import hashlib
import json
import os

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, DeleteMessagesRequest
from telethon.tl.types import ChannelParticipantsSearch

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")


def get_channel_members(channel_id):
    with TelegramClient('user_bot_termin_radar', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        participants = client(
            GetParticipantsRequest(channel=channel_id, filter=ChannelParticipantsSearch(''), offset=0, limit=100,
                                   hash=0)).users
        return [hashlib.md5(str(user.id).encode()).hexdigest() for user in participants]


def send_message_to_channel(channel_id, message):
    with TelegramClient('user_bot_termin_radar', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        client.start()
        client.send_message(channel_id, message)


def get_channel_unpinned_messages(channel_id, client):
    messages_to_delete = []
    offset_id = 0
    while True:
        history = client(
            GetHistoryRequest(peer=channel_id, offset_id=offset_id, offset_date=None, add_offset=0, limit=100, max_id=0,
                              min_id=0, hash=0))
        messages = history.messages
        if not messages:
            break
        offset_id = messages[-1].id if messages else 0

        print(f"client_id: {client.get_me().id}")
        for msg in messages:
            print(json.dumps(msg.to_dict(), indent=4, default=str))

        messages_to_delete += [msg.id for msg in messages if not msg.pinned]

    return messages_to_delete


def delete_unpinned_messages(channel_id):
    with TelegramClient('user_bot_termin_radar', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        client.start()
        messages_to_delete = get_channel_unpinned_messages(channel_id, client)
        if messages_to_delete:
            print(client(DeleteMessagesRequest(id=messages_to_delete, revoke=True)))

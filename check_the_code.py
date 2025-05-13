from time import sleep

from lib.channel_operator import send_message_to_channel, delete_unpinned_messages

#send_message_to_channel("@klekovkindatest", "15:45 MESSAGE TO DELETE")

delete_unpinned_messages("@klekovkindatest")

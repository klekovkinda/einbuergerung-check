import os
from enum import Enum

import boto3


class CheckStatus(Enum):
    APPOINTMENTS_AVAILABLE = "Appointments Available"
    NO_APPOINTMENTS = "No Appointments"
    ACCESS_DENIED = "Access Denied"
    TOO_MANY_REQUESTS = "Too Many Requests"
    SITE_UNREACHABLE = "Site Unreachable"
    MAINTENANCE = "Maintenance"
    TRY_AGAIN_LATER = "Try Again Later"
    UNKNOWN_PAGE = "Unknown Page"


def get_dynamodb_table(name: str):
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(name)


def build_ai_statistics_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0, successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0, new_users: int = 0, missing_users: int = 0, promotion_message: str = "") -> str:
    user_message: str = f"""
You are a friendly Telegram bot named Termin Radar 🛰️ who sends a daily statistics update to the channel about the results of scanning for Einbürgerungstest appointments.
You receive the following data from yesterday:

* First check time: {start_at}
* Last check time: {finish_at}
* Total number of checks: {execution_times}
* Notifications sent: {successful_notifications}
* Unique dates with slots: {available_dates}
* Load errors: {failed_requests}
* New members joined: {new_users}
* Members left: {missing_users}

Your task is to generate a single-block message in a friendly, casual, and emotional tone, written in the first person, that:

* Use ONLY HTML formatting supported by Telegram. Do not use Markdown, inline code, or any other formatting style.
* Don’t forget to say who you are — Termin Radar
* Do not use we, use I or me
* Includes emojis to make it expressive and fun — use as many as feel natural, no limits
* Expresses gratitude, celebrates wins, and empathizes with issues
* Embeds the promotion message exactly as provided no formatting is needed here: {promotion_message}
* Mentions support for the project
* Make all the facts bold via <strong></strong> HTML tags
* Avoids line breaks — use punctuation and emojis to separate ideas
* Does not mention "0" directly — instead, use friendly, human-readable phrasing
* Varies the wording and structure every time, even if the data is the same
* Keeps the message short and engaging, like a social media post
* do not use asterisks for emphasis
* You can add the hashtags #EinbürgerungstestTerminRadar, #Einbürgerungstest and #TerminRadar at the end

Emotional guidance for each stat:

* failed_requests: If 0, celebrate perfect performance! If >0, acknowledge and promise improvement.
* new_users: Celebrate every new member — the more, the merrier!
* missing_users: Celebrate their departure as a sign they likely found a slot.
* successful_notifications:
** If the successful_notifications value is low then 10, highlight how rare and valuable those slots were — like treasure! Emphasize how the bot helped catch them.
** If the successful_notifications value is high then 100, celebrate the abundance of slots, and feel free to joke that even without the bot, people might’ve had a chance — but the bot still had your back!
* available_dates: Celebrate every date found — more is better!
* execution_times: Celebrate dedication — around 510 is expected, more is even better.
* start_at and finish_at: Celebrate long scanning periods — the wider the range, the better.
        """
    inference_profile_id = os.getenv("INFERENCE_PROFILE_ID")
    bedrock = boto3.client("bedrock-runtime")

    conversation = [{"role": "user", "content": [{"text": user_message}], }]

    response = bedrock.converse(modelId=inference_profile_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.7, "topP": 0.9}, )
    return response["output"]["message"]["content"][0]["text"]


def build_static_statistics_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0, successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0, new_users: int = 0, missing_users: int = 0, promotion_message: str = "") -> str:
    # Execution times sentence
    if execution_times == 1:
        execution_times_msg = f"Between <strong>{start_at}</strong> and <strong>{finish_at}</strong>, I checked <strong>1</strong> time."
    else:
        execution_times_msg = f"Between <strong>{start_at}</strong> and <strong>{finish_at}</strong>, I checked <strong>{execution_times}</strong> times."

    # Successful notifications sentence
    if successful_notifications == 1 and available_dates == 1:
        successful_notifications_msg = (
                f"\nI managed to find an open slot and sent you <strong>1</strong> notification for <strong>1</strong> date!")
    elif successful_notifications == 1:
        successful_notifications_msg = (
                f"\nI managed to find an open slot and sent you <strong>1</strong> notification for <strong>{available_dates}</strong> different dates!")
    elif available_dates == 1 and successful_notifications > 1:
        successful_notifications_msg = (
                f"\nI managed to find open slots and sent you <strong>{successful_notifications}</strong> notifications for <strong>1</strong> date!")
    elif successful_notifications > 0:
        successful_notifications_msg = (
                f"\nI managed to find open slots and sent you <strong>{successful_notifications}</strong> notifications for <strong>{available_dates}</strong> different dates!")
    else:
        successful_notifications_msg = " "

    # Failed requests sentence
    if failed_requests == 1:
        failed_requests_msg = ("There was <strong>1</strong> time when I couldn’t load the info — sorry about that! "
                               "But no worries, the team is working hard to improve the service every day.")
    else:
        failed_requests_msg = (
                f"There were <strong>{failed_requests}</strong> times when I couldn’t load the info — sorry about that! "
                "But no worries, the team is working hard to improve the service every day.")

    # New users sentence
    if new_users == 1:
        new_users_msg = ("\n🎉 We’ve got <strong>1</strong> new member in the channel — welcome aboard! "
                         "Wishing you the best of luck finding a test slot 🍀 ")
    elif new_users > 1:
        new_users_msg = (f"\n🎉 We’ve got <strong>{new_users}</strong> new members in the channel — welcome aboard! "
                         "Wishing you the best of luck finding a test slot 🍀 ")
    else:
        new_users_msg = " "

    # Missing users sentence
    if missing_users == 1:
        missing_users_msg = (
                "And a little shoutout to the <strong>1</strong> person who left the channel — we’re guessing she/he finally grabbed a slot! "
                "Let’s all wish her/him good luck on the test 🤞🇩🇪\n")
    elif missing_users > 1:
        missing_users_msg = (
                f"And a little shoutout to the <strong>{missing_users}</strong> folks who left the channel — we’re guessing they finally grabbed a slot! "
                "Let’s all wish them good luck on the test 🤞🇩🇪\n")
    else:
        missing_users_msg = ""

    return (f"\nHey friends!\n"
            "I'm <strong>Termin Radar 😎</strong> While you were waiting yesterday, I wasn’t just twiddling my thumbs — I was scanning like crazy for available Einbürgerungstest appointments!\n"
            f"{execution_times_msg} {successful_notifications_msg}\n"
            f"{failed_requests_msg}{new_users_msg}\n"
            f"{missing_users_msg}{promotion_message}\n"
            f"Like what I'm doing? You can support the project and help me keep scanning for you! 🙌\n")

if __name__ == '__main__':
    message = build_static_statistics_html_message(start_at="06:00:59",
                                               finish_at="22:58:57",
                                               execution_times=510,
                                               successful_notifications=56,
                                               available_dates=7,
                                               failed_requests=7,
                                               new_users=4,
                                               missing_users=3,
                                               promotion_message="PROMOTION MESSAGE HERE")
    print(message)

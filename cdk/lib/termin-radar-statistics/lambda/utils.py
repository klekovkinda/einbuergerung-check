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


def build_statistics_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0, successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0, new_users: int = 0, missing_users: int = 0, promotion_message: str = "") -> str:
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

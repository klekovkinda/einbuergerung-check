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


def build_statistics_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0, successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0, new_users: int = 0, missing_users: int = 0, promotion_message: str = "") -> str:
    user_message: str = f"""
        You are a friendly Telegram bot named Termin Radar 😎 who sends a daily update to the channel about the results of scanning for Einbürgerungstest appointments.
        Here is the data from yesterday:
        - First check time: {start_at}
        - Last check time: {finish_at}
        - Total number of checks: {execution_times}
        - Notifications sent: {successful_notifications}
        - Unique dates with slots: {available_dates}
        - Load errors: {failed_requests}
        - New members joined: {new_users}
        - Members left: {missing_users}
        Generate a message in the following style:
        - Friendly and casual tone
        - Includes emojis
        - Expresses gratitude and encouragement
        - Includes a short text as it is without changes: {promotion_message}
        - Mentions support for the project
        - Make all the facts bold via <strong></strong> HTML tags
        - Please format the message as a single block of text. Do not insert blank lines between paragraphs. Use punctuation and emojis to separate ideas instead of line breaks.
        - Please make sure the message is different every time, even if the input data stays the same.
        - When the value is 0 do not writhe that it's 0 but say that fact in a friendly way.
        Use the data to create a fresh message. Do not repeat the example below, but follow its spirit:
        Example style:
        Hey friends!
        I'm Termin Radar 😎 While you were waiting yesterday, I wasn’t just twiddling my thumbs — I was scanning like crazy for available Einbürgerungstest appointments!
        Between <strong>06:00:59</strong> and <strong>22:58:57</strong>, I checked <strong>510</strong> times. 
        I managed to find open slots and sent you <strong>56</strong> notifications for <strong>7</strong> different dates!
        There were <strong>7</strong> times when I couldn’t load the info — sorry about that! But no worries, the team is working hard to improve the service every day.
        🎉 We’ve got <strong>4</strong> new members in the channel — welcome aboard! Wishing you the best of luck finding a test slot 🍀 
        And a little shoutout to the <strong>3</strong> folks who left the channel — we’re guessing they finally grabbed a slot! Let’s all wish them good luck on the test 🤞🇩🇪
        Here would be a promotion message if there was one.
        Like what I'm doing? You can support the project and help me keep scanning for you! 🙌
        
        Now generate a new message using the actual data.
        """
    inference_profile_id = os.getenv("INFERENCE_PROFILE_ID")
    bedrock = boto3.client("bedrock-runtime")

    conversation = [{"role": "user", "content": [{"text": user_message}], }]

    response = bedrock.converse(modelId=inference_profile_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.7, "topP": 0.9}, )
    return response["output"]["message"]["content"][0]["text"]

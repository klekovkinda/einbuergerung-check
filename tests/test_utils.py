import unittest
from lib.utils import build_statistics_html_message

class TestBuildStatisticsHtmlMessage(unittest.TestCase):
    def test_statistics_html_message_all_zeros(self):
        msg = build_statistics_html_message()
        self.assertIn("Between <strong>00:00:00</strong> and <strong>00:00:00</strong>, I checked <strong>0</strong> times.", msg)
        self.assertIsNot("I managed to find open slots and sent you", msg)
        self.assertIn("<strong>0</strong> times when I couldn’t load the info", msg)

    def test_statistics_html_message_with_successful_notifications(self):
        msg = build_statistics_html_message(
            start_at="08:00:00",
            finish_at="09:00:00",
            execution_times=5,
            successful_notifications=2,
            available_dates=2,
            failed_requests=1
        )
        self.assertIn("Between <strong>08:00:00</strong> and <strong>09:00:00</strong>, I checked <strong>5</strong> times.", msg)
        self.assertIsNot("I managed to find open slots and sent you <strong>2</strong> notifications for <strong>2</strong> different dates!", msg)
        self.assertIn("<strong>1</strong> times when I couldn’t load the info", msg)
        print(msg)

    def test_statistics_html_message_no_successful_notifications(self):
        msg = build_statistics_html_message(
            start_at="10:00:00",
            finish_at="11:00:00",
            execution_times=3,
            successful_notifications=0,
            available_dates=0,
            failed_requests=2
        )

        self.assertIn("Between <strong>10:00:00</strong> and <strong>11:00:00</strong>, I checked <strong>3</strong> times.", msg)
        self.assertIsNot("I managed to find open slots", msg)
        self.assertIn("<strong>2</strong> times when I couldn’t load the info", msg)
        print(msg)

    def test_full_statistics_html_messages(self):
        msg = build_statistics_html_message(
            start_at="08:00:00",
            finish_at="09:00:00",
            execution_times=5,
            successful_notifications=2,
            available_dates=2,
            failed_requests=1,
            new_users=3,
            missing_users=2
        )
        expected_msg ="""
Hey friends!
I'm <strong>Termin Radar 😎</strong> While you were waiting yesterday, I wasn’t just twiddling my thumbs — I was scanning like crazy for available Einbürgerungstest appointments!
Between <strong>08:00:00</strong> and <strong>09:00:00</strong>, I checked <strong>5</strong> times. 
I managed to find open slots and sent you <strong>2</strong> notifications for <strong>2</strong> different dates!
There were <strong>1</strong> times when I couldn’t load the info — sorry about that! But no worries, the team is working hard to improve the service every day.
🎉 We’ve got <strong>3</strong> new members in the channel — welcome aboard! Wishing you the best of luck finding a test slot 🍀 
And a little shoutout to the <strong>2</strong> folks who left the channel — we’re guessing they finally grabbed a slot! Let’s all wish them good luck on the test 🤞🇩🇪
Like what I'm doing? You can support the project and help me keep scanning for you! 🙌
"""
        self.assertEqual(expected_msg, msg)
        print(msg)


if __name__ == "__main__":
    unittest.main()

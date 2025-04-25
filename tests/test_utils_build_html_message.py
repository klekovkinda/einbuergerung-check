import unittest

from lib.utils import build_html_message

URL = "example.com"


class TestBuildMarkdownMessage(unittest.TestCase):
    def test_empty_available_dates(self):
        available_dates = []
        expected_output = ("<b>Go and book your appointment now!</b>\n"
                           "<a href='example.com'>Click here to book the appointment</a>\n"
                           "Available dates:\n")
        self.assertEqual(build_html_message(URL, available_dates), expected_output)

    def test_single_available_date(self):
        available_dates = ["12.06.2025"]
        expected_output = ("<b>Go and book your appointment now!</b>\n"
                           "<a href='example.com'>Click here to book the appointment</a>\n"
                           "Available dates:\n"
                           "• 12.06.2025")
        self.assertEqual(build_html_message(URL, available_dates), expected_output)

    def test_multiple_available_dates(self):
        available_dates = ["12.06.2025", "15.06.2025"]
        expected_output = ("<b>Go and book your appointment now!</b>\n"
                           "<a href='example.com'>Click here to book the appointment</a>\n"
                           "Available dates:\n"
                           "• 12.06.2025\n"
                           "• 15.06.2025")
        self.assertEqual(build_html_message(URL, available_dates), expected_output)


if __name__ == "__main__":
    unittest.main()

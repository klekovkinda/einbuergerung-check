import unittest

from lib.extract_dates import AvailableDate
from lib.utils import build_markdown_message


class TestBuildMarkdownMessage(unittest.TestCase):
    def test_empty_available_dates(self):
        available_dates = []
        expected_output = "Go and book your appointment now! Available dates:\n"
        self.assertEqual(build_markdown_message(available_dates), expected_output)

    def test_single_available_date(self):
        available_dates = [AvailableDate("Date 1", "termin1")]
        expected_output = ("Go and book your appointment now! Available dates:\n"
                           "- [Date 1](https://service.berlin.de/termin1)\n")
        self.assertEqual(build_markdown_message(available_dates), expected_output)

    def test_multiple_available_dates(self):
        available_dates = [AvailableDate("Date 1", "termin1"), AvailableDate("Date 2", "termin2")]
        expected_output = ("Go and book your appointment now! Available dates:\n"
                           "- [Date 1](https://service.berlin.de/termin1)\n"
                           "- [Date 2](https://service.berlin.de/termin2)\n")
        self.assertEqual(build_markdown_message(available_dates), expected_output)


if __name__ == "__main__":
    unittest.main()

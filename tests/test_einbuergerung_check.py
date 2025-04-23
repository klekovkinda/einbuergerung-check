import unittest
from unittest.mock import patch, MagicMock
from einbuergerung_check import check_for_appointment, bot, URL


class TestEinbuergerungCheck(unittest.TestCase):
    @patch("einbuergerung-check.check_for_appointment")
    @patch("einbuergerung-check.bot.send_message")
    def test_appointment_notification_sent(self, mock_send_message, mock_check_for_appointment):
        mock_check_for_appointment.return_value = True

        with patch("builtins.print"):
            exec(open("einbuergerung-check.py").read())

        mock_send_message.assert_called_once_with(
            bot.chat_id, f"Go and book your appointment now! \n {URL}"
        )

    @patch("einbuergerung-check.check_for_appointment")
    @patch("einbuergerung-check.bot.send_message")
    def test_no_appointment_no_notification(self, mock_send_message, mock_check_for_appointment):
        mock_check_for_appointment.return_value = False

        with patch("builtins.print"):
            exec(open("einbuergerung-check.py").read())

        mock_send_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()

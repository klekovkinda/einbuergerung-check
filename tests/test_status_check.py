import unittest
from unittest.mock import patch, MagicMock
from lib.status_check import check_for_appointment, check_appointment


class TestStatusCheck(unittest.TestCase):
    @patch("lib.status_check.webdriver.Chrome")
    def test_check_for_appointment_no_appointments(self, mock_chrome):
        mock_driver = MagicMock()
        mock_driver.page_source = "Leider sind aktuell keine Termine für ihre Auswahl verfügbar."
        mock_chrome.return_value = mock_driver

        result = check_for_appointment("http://example.com")
        self.assertFalse(result)

    @patch("lib.status_check.webdriver.Chrome")
    def test_check_for_appointment_appointments_available(self, mock_chrome):
        mock_driver = MagicMock()
        mock_driver.page_source = "<html>Appointments available!</html>"
        mock_chrome.return_value = mock_driver

        with patch("lib.status_check.os.makedirs"), patch("lib.status_check.open", create=True):
            result = check_for_appointment("http://example.com")
        self.assertTrue(result)

    @patch("lib.status_check.webdriver.Chrome")
    def test_check_for_appointment_access_denied(self, mock_chrome):
        mock_driver = MagicMock()
        mock_driver.page_source = "Forbidden access"
        mock_chrome.return_value = mock_driver

        result = check_for_appointment("http://example.com")
        self.assertFalse(result)

    @patch("lib.status_check.webdriver.Chrome")
    def test_check_for_appointment_too_many_requests(self, mock_chrome):
        mock_driver = MagicMock()
        mock_driver.page_source = "Zu viele Zugriffe"
        mock_chrome.return_value = mock_driver

        result = check_for_appointment("http://example.com")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

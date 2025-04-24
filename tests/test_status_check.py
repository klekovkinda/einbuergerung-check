import os
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

from lib.status_check import check_for_appointment


class TestStatusCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class MockServerHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                base_path = os.path.dirname(__file__)
                file_path = os.path.join(base_path, "html", self.path.lstrip("/"))
                if os.path.exists(file_path) and self.path.endswith(".html"):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    with open(file_path, "rb") as file:
                        self.wfile.write(file.read())
                else:
                    self.send_response(404)
                    self.end_headers()

        cls.mock_server = HTTPServer(("localhost", 0), MockServerHandler)
        cls.server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        cls.mock_server_url = f"http://localhost:{cls.mock_server.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.mock_server.shutdown()
        cls.mock_server.server_close()  # Ensure the server's socket is closed
        cls.server_thread.join()

    def test_check_for_appointment__zu_viele_zugriffe(self):
        file_name = "zu_viele_zugriffe.html"
        url = f"{self.mock_server_url}{file_name}"
        result = check_for_appointment(url)
        self.assertFalse(result)

    def test_check_for_appointment__wartung(self):
        file_name = "wartung.html"
        url = f"{self.mock_server_url}{file_name}"
        result = check_for_appointment(url)
        self.assertFalse(result)

    def test_check_for_appointment__keine_termine(self):
        file_name = "keine_termine.html"
        url = f"{self.mock_server_url}{file_name}"
        result = check_for_appointment(url)
        self.assertFalse(result)

    def test_check_for_appointment__forbidden_access(self):
        file_name = "forbidden_access.html"
        url = f"{self.mock_server_url}{file_name}"
        result = check_for_appointment(url)
        self.assertFalse(result)

    def test_this_site_can_not_be_reached(self):
        file_name = "this_site_can_not_be_reached.html"
        url = f"{self.mock_server_url}{file_name}"
        result = check_for_appointment(url)
        self.assertFalse(result)

    def test_check_for_appointment__terminvereinbarung(self):
        file_name = "terminvereinbarung.html"
        url = f"{self.mock_server_url}{file_name}"
        result = check_for_appointment(url)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()


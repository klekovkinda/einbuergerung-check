from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    APPOINTMENTS_AVAILABLE = "Appointments Available"
    NO_APPOINTMENTS = "No Appointments"
    ACCESS_DENIED = "Access Denied"
    TOO_MANY_REQUESTS = "Too Many Requests"
    SITE_UNREACHABLE = "Site Unreachable"
    MAINTENANCE = "Maintenance"
    TRY_AGAIN_LATER = "Try Again Later"
    UNKNOWN_PAGE = "Unknown Page"


@dataclass
class AlgorithmParseResult:
    appointment_status: CheckStatus
    available_dates: list[str]
    telegram_html_message: str

    def to_dict(self):
        return {
                'appointment_status': f"{self.appointment_status.value}",
                'available_dates': self.available_dates,
                'telegram_html_message': self.telegram_html_message}

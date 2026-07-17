"""SMS provider abstraction.

`SmsProvider` is the interface a production backend (Twilio, etc.) would
implement. `ConsoleSmsProvider` is the local/test adapter used in this
academic project — it never makes a network call, so it requires no paid
credentials and works identically in development and automated tests.
"""
from abc import ABC, abstractmethod


class SmsProvider(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> bool:
        """Return True if the message was accepted for delivery."""
        raise NotImplementedError


class ConsoleSmsProvider(SmsProvider):
    def send(self, to: str, message: str) -> bool:
        print(f'[SMS] to={to or "(no phone on file)"}: {message}')
        return True


def get_sms_provider() -> SmsProvider:
    return ConsoleSmsProvider()

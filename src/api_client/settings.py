from dataclasses import dataclass


@dataclass
class APISettings:
    base_url: str
    timeout: float = 10.0

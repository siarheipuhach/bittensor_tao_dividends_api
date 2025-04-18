from pydantic import BaseModel


class StakeHistory(BaseModel):
    netuid: int
    hotkey: str
    amount: float
    direction: str
    timestamp: str

from pydantic import BaseModel, Field


class TaoDividendResponse(BaseModel):
    netuid: int = Field(..., description="Subnet netuid identifier.")
    hotkey: str = Field(..., description="SS58 address of the hotkey.")
    dividend: int = Field(
        ..., description="Amount of Tao dividends received (in raw units)."
    )
    cached: bool = Field(
        ..., description="Indicates if the result was fetched from cache."
    )
    stake_tx_triggered: bool = Field(
        ..., description="Whether a stake/unstake transaction was triggered."
    )

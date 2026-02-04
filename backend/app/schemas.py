from pydantic import BaseModel
from typing import List


class PredictResult(BaseModel):
    id: int
    filename: str
    label: str
    confidence: float
    created_at: str


class ErrorResponse(BaseModel):
    message: str
    detail: str | None = None
    code: str


class HistoryResponse(BaseModel):
    data: List[PredictResult]

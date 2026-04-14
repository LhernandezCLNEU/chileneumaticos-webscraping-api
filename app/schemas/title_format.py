from pydantic import BaseModel
from typing import Optional, Dict, Any


class TitleFormatBase(BaseModel):
    name: str
    pattern: str
    example: Optional[str] = None
    priority: int = 0
    enabled: bool = True
    version: Optional[str] = "1.0"


class TitleFormatCreate(TitleFormatBase):
    pass


class TitleFormatUpdate(BaseModel):
    name: Optional[str] = None
    pattern: Optional[str] = None
    example: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None
    version: Optional[str] = None


class TitleFormatRead(TitleFormatBase):
    id: int
    created_by_id: Optional[int] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class ParseResult(BaseModel):
    format_id: Optional[int]
    format_name: Optional[str]
    result: Dict[str, Any]

    model_config = {"from_attributes": True}

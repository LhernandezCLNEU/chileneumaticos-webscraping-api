from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ParsedResultRead(BaseModel):
    id: int
    product_id: int
    title_format_id: Optional[int] = None
    result: Dict[str, Any]
    parsed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

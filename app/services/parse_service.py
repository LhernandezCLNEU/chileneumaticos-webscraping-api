import re
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.title_format import TitleFormat
from app.models.parsed_result import ParsedResult
from app.models.product import Product


async def parse_title_with_formats(title: str, db: AsyncSession) -> Dict[str, Any]:
    q = await db.execute(select(TitleFormat).where(TitleFormat.enabled == True).order_by(TitleFormat.priority.desc()))
    formats = q.scalars().all()

    for fmt in formats:
        try:
            regex = re.compile(fmt.pattern, re.IGNORECASE)
        except re.error:
            continue
        m = regex.search(title)
        if not m:
            continue
        # prefer named groups
        if m.groupdict():
            result = m.groupdict()
        else:
            groups = m.groups()
            result = {str(i): v for i, v in enumerate(groups)}

        return {"format_id": fmt.id, "format_name": fmt.name, "result": result}

    return {"format_id": None, "format_name": None, "result": {}}


async def apply_format_to_product(product_id: int, db: AsyncSession) -> Optional[ParsedResult]:
    q = await db.execute(select(Product).where(Product.id == product_id))
    product = q.scalars().first()
    if not product:
        return None

    parsed = await parse_title_with_formats(product.title_raw, db)

    pr = ParsedResult(product_id=product.id, title_format_id=parsed.get("format_id"), result=parsed.get("result"))
    db.add(pr)
    await db.commit()
    await db.refresh(pr)

    # update product normalized title when possible
    if parsed.get("result"):
        product.title_normalized = product.title_raw
        db.add(product)
        await db.commit()
        await db.refresh(product)

    return pr

import pytest
from sqlalchemy import select

from app.models.title_format import TitleFormat
from app.models.product import Product
from app.services.parse_service import parse_title_with_formats, apply_format_to_product


@pytest.mark.asyncio
async def test_parse_title_with_formats(db_session):
    # create a simple title format
    tf = TitleFormat(name="simple", pattern=r"(?P<brand>\w+)\s+(?P<width>\d{3})/(?P<profile>\d{2})\sR(?P<diameter>\d{2})", example="Pirelli 205/55 R16", priority=10)
    db_session.add(tf)
    await db_session.commit()
    await db_session.refresh(tf)

    # create a product
    p = Product(title_raw="Pirelli 205/55 R16 91V Cinturato P7")
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    parsed = await parse_title_with_formats(p.title_raw, db_session)
    assert parsed["format_id"] == tf.id
    assert parsed["result"]["brand"] == "Pirelli"
    assert parsed["result"]["width"] == "205"

    # test apply_format_to_product creates a ParsedResult record
    pr = await apply_format_to_product(p.id, db_session)
    assert pr is not None
    assert pr.product_id == p.id
    assert isinstance(pr.result, dict)

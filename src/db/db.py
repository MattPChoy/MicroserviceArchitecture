from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship

mapper_registry = registry()
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
engine = create_engine("sqlite+pysqlite:///test2.db", echo=True)


@mapper_registry.mapped
class User:
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    fullname: Mapped[Optional[str]]
    nickname: Mapped[Optional[str]] = mapped_column(String(64))
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

    addresses: Mapped[list["Address"]] = relationship(back_populates="user")


@mapper_registry.mapped
class Address:
    __tablename__ = "address"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("user.id"))
    email_address: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="addresses")


from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String

metadata_obj = MetaData()
user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True, unique=True),
    Column("name", String(30)),
    Column("fullname", String),
)

# Create the tables.
metadata_obj.create_all(engine)

from sqlalchemy import insert

stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")
stmt2 = select(user_table).where(user_table.c.name == "spongebob")
print(stmt)

with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()

    r = conn.execute(stmt2)
    print(r.all())

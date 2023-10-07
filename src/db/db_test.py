from sqlalchemy import create_engine, text
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

# with engine.connect() as conn:
#     res = conn.execute(text("select 'hello world'"))
#     print(res.all())
#
# with engine.connect() as conn:
#     conn.execute(text("CREATE TABLE some_table (x int, y int)"))
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
#     )
#     # Changes are implicitly written?
#
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT x, y FROM some_table"))
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")

from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()
user_table = Table(
    "user_account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)
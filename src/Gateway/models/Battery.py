from typing import Optional

from pydantic import BaseModel
import psycopg2
import logging


class Battery(BaseModel):
    name: str
    capacity: int
    charge: int
    owner: int
    id: Optional[str] = None


class BatteryTable:
    def __init__(self, db=None):
        self.db = db or psycopg2.connect(
            database='batteries_db',
            user='docker',
            password='docker',
            host='batteries_db',
        )
        self.cursor = self.db.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "public".BATTERIES ( \
                                "id" SERIAL PRIMARY KEY, \
                                "owner" integer NOT NULL, \
                                "capacity" integer NOT NULL, \
                                "charge" integer NOT NULL, \
                                "name" text NOT NULL \
                            )')
        self.db.commit()
        self.column_names = ["id", "owner", "capacity", "charge", "name"]

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")

    def add(self, owner: int, name: str, capacity: int, charge: int):
        assert type(owner) == int, f"Owner should be type string but is instead {type(name)}"
        assert type(name) == str, f"Battery name should be type string but is instead {type(name)}"
        assert type(capacity) == int, f"Battery capacity should be type int but is instead {type(capacity)}"
        assert type(charge) == int, f"Battery charge should be type int but is instead {type(charge)}"

        self.cursor.execute(
            'INSERT INTO "public".BATTERIES (owner, name, capacity, charge) VALUES (%s, %s, %s, %s) RETURNING id',
            (str(owner), name, str(capacity), str(charge)))
        batt_id = self.cursor.fetchone()[0]
        self.db.commit()
        return batt_id

    def get(self, battery_id: int):
        try:
            self.cursor.execute('SELECT * FROM "public".BATTERIES WHERE id = %s', (battery_id,))
        except psycopg2.ProgrammingError as e:
            self.logger.error(f"Postgres Programming Error {e}")
            return False
        return self.cursor.fetchone()

    def get_all_owned_by(self, uid: int):
        self.cursor.execute('SELECT * FROM "public".BATTERIES WHERE owner=%s', (uid,))
        return self.cursor.fetchall()

    def update(self, owner: str, id: int, name: str, capacity: int, charge: int):
        self.cursor.execute(
            'UPDATE "public".BATTERIES SET owner = %s, name  = %s, capacity = %s, charge = %s WHERE id = %s',
            (owner, name, capacity, charge, id))
        self.db.commit()

    def delete(self, battery_id: int):
        self.cursor.execute('DELETE FROM "public".BATTERIES WHERE id=%s', (battery_id,))
        self.db.commit()

from typing import Optional

import psycopg2
import logging

from pydantic import BaseModel


class Station(BaseModel):
    lat: float
    lon: float
    name: str
    id: Optional[str] = None


class StationsTable:
    def __init__(self, db=None):
        self.db = db or psycopg2.connect(
            database='batteries_db',
            user='docker',
            password='docker',
            host='batteries_db',
        )
        self.cursor = self.db.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "public".STATIONS ( \
                                "id" SERIAL PRIMARY KEY, \
                                "lat" float8 NOT NULL, \
                                "lon" float8 NOT NULL, \
                                "name" text NOT NULL, \
                                "active" boolean NOT NULL \
                            )')
        self.db.commit()
        self.column_names = ["id", "lat", "lon", "name", "active"]

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")

    def add(self, lat: float, lon: float, name: str):
        assert type(lat) == float, f"Latitude should be type float but is instead {type(lat)}"
        assert type(lon) == float, f"Longitude should be type float but is instead {type(lon)}"
        assert type(name) == str, f"Station name should be type string but is instead {type(name)}"

        self.cursor.execute(
            'INSERT INTO "public".STATIONS (lat, lon, name, active) VALUES (%s, %s, %s, true) RETURNING id',
            (str(lat), str(lon), name))
        station_id = self.cursor.fetchone()[0]
        self.db.commit()
        return station_id

    def get(self, station_id: int):
        try:
            self.cursor.execute('SELECT * FROM "public".STATIONS WHERE id = %s AND active=true', (station_id,))
        except psycopg2.ProgrammingError as e:
            self.logger.error(f"Postgres Programming Error {e}")
            return False
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute('SELECT * FROM "public".STATIONS WHERE active=true')
        return self.cursor.fetchall()

    def get_closest(self, lat: float, lon: float):
        return self.get_n_closest(lat, lon, 1)[0]

    def get_n_closest(self, lat: float, lon: float, n: int):
        self.cursor.execute(
            'SELECT * FROM "public".STATIONS '
            'ORDER BY (lat - %s)^2 + (lon - %s)^2 ASC LIMIT %s',
            (lat, lon, n)
        )
        return self.cursor.fetchall()

    def update(self, id: int, lat: float, lon: float, name: str):
        assert type(lat) == float, f"Latitude should be type float but is instead {type(lat)}"
        assert type(lon) == float, f"Longitude should be type float but is instead {type(lon)}"
        assert type(name) == str, f"Station name should be type string but is instead {type(name)}"

        self.cursor.execute(
            'UPDATE "public".STATIONS SET lat=%s, lon=%s, name=%s WHERE id=%s AND active=true',
            (str(lat), str(lon), name, id))
        self.db.commit()
        return True

    def delete(self, id: int):
        self.cursor.execute('UPDATE "public".STATIONS SET active=false WHERE id=%s', (id,))
        self.db.commit()
        return True

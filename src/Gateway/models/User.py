from typing import Optional

from pydantic import BaseModel
import psycopg2
import logging

from psycopg2.errors import UndefinedTable


class User(BaseModel):
    firstname: str
    lastname: str
    password: str
    email: str
    region: int
    id: Optional[str] = None


class UserTable:
    def __init__(self, db=None):
        self.db = db or psycopg2.connect(
            database='users_db',
            user='docker',
            password='docker',
            host='users_db',
        )
        self.cursor = self.db.cursor()
        self.create_table()
        self.db.commit()

        self.column_names = ["id", "firstname", "lastname", "email", "region"]
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")

    def create_table(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "public".USERS ( \
                                        "id" SERIAL PRIMARY KEY, \
                                        "firstname" text NOT NULL, \
                                        "lastname" text NOT NULL, \
                                        "password" text NOT NULL, \
                                        "email" text NOT NULL, \
                                        "region" integer NOT NULL, \
                                        "active" boolean NOT NULL \
                                    )')

    def add(self, firstname: str, lastname: str, password: str, email: str, region: int):
        assert type(firstname) == str, f"First name should be a string type but is instead {(type(firstname))}"
        assert type(lastname) == str, f"Last name should be a string type but is instead {(type(lastname))}"
        assert type(password) == str, f"Password should be a string type but is instead {(type(password))}"
        assert type(email) == str, f"Email should be a string type but is instead {(type(email))}"
        assert type(region) == int, f"Region should be an integer type but is instead {(type(region))}"

        def _add():
            self.cursor.execute('INSERT INTO "public".USERS (firstname, lastname, password, email, region, active) \
                                            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                                (firstname, lastname, password, email, region, "true"))

        try:
            _add()
        except UndefinedTable as e:
            self.create_table()
            _add()

        uid = self.cursor.fetchone()[0]
        self.db.commit()
        return uid

    def get(self, id: str):
        def _get():
            self.cursor.execute('SELECT * FROM "public".USERS WHERE id=%s AND active=true', (id,))

        try:
            _get()
        except psycopg2.ProgrammingError as error:
            self.logger.error(f"Postgres Programming Error {error}")
            return False
        except UndefinedTable as e:
            self.create_table()
            _get()

        return self.cursor.fetchone()

    def update(self, id: str, firstname: str, lastname: str, password: str, email: str, region: int):

        def _update():
            self.cursor.execute('UPDATE "public".USERS SET firstname = %s, lastname = %s, password = %s, email = %s, \
                    region = %s WHERE id = %s', (firstname, lastname, password, email, region, id))
            self.db.commit()

        try:
            _update()
        except UndefinedTable as e:
            self.create_table()
            _update()

    def delete(self, id: str, hard=False):
        def _delete():
            if hard:
                self.cursor.execute('DELETE FROM "public".USERS WHERE id = %s', (id,))
            self.cursor.execute('UPDATE "public".USERS SET active = false WHERE id = %s', (id,))
            self.db.commit()

        try:
            _delete()
        except UndefinedTable as e:
            self.create_table()
            _delete()

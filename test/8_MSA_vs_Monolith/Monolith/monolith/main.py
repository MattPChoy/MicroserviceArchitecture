import time

from flask import Flask, request, jsonify
import psycopg2


class Monolith:
    def __init__(self):
        self.db = None
        self.read_queues = {}
        self.write_queues = {}

        while self.db is None:
            try:
                self.db = psycopg2.connect(
                    database='exampledb',
                    user='docker',
                    password='docker',
                    host='database'
                )
            except psycopg2.OperationalError:
                print("Waiting for database...")
                time.sleep(4)

        self.db.cursor().execute('CREATE TABLE IF NOT EXISTS "public".BATTERIES ( \
                            "id" SERIAL PRIMARY KEY, \
                            "capacity" integer NOT NULL, \
                            "charge" integer NOT NULL, \
                            "name" text NOT NULL \
                        ) \
                    ')


srv = Monolith()
app = Flask(__name__)


@app.route("/api/batteries", methods=["GET", "POST"])
def batteries():
    cursor = srv.db.cursor()
    if request.method == "POST":
        data = request.json
        capacity = data['capacity']
        charge = data['charge']
        name = data['name']

        cursor.execute("INSERT INTO batteries (capacity, charge, name) VALUES (%s,%s,%s)",
                       (capacity, charge, name))
        srv.db.commit()
        time.sleep(5 / 1000)
        return "Batteries added successfully", 200
    elif request.method == "GET":
        cursor.execute("SELECT * FROM batteries")
        return jsonify(cursor.fetchall())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

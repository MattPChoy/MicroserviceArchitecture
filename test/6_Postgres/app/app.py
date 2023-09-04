import psycopg2

# Connect to an existing database using the credentials defined in docker-compose.
conn = psycopg2.connect(
    database='exampledb',
    user='docker',
    password='docker',
    host='0.0.0.0'
)

# Open cursor to perform operations on db
cursor = conn.cursor()

# Query the db
cursor.execute("SELECT * FROM batteries")
rows = cursor.fetchall()

if not len(rows):
    print("Database table is empty")
else:
    for row in rows:
        print(row)

# Close the connection
cursor.close()
conn.close()

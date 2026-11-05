
import os
import psycopg2
from psycopg2 import sql

def connect():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "db"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "ibmi"),
        user=os.getenv("PGUSER", "ibmi"),
        password=os.getenv("PGPASSWORD", "ibmi_dev_2026")
    )


def create_library(name, description="User library"):
    name = name.upper()

    if not name.replace("_", "").isalnum() or len(name) > 10:
        print("CPF0001 - Invalid library name.")
        return

    conn = connect()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ibmi_libraries
                    (library_name, description)
                VALUES (%s, %s)
                ON CONFLICT (library_name) DO NOTHING
                RETURNING id
                """,
                (name, description)
            )

            created = cur.fetchone() is not None

            cur.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(name)
                )
            )

        conn.commit()

        if created:
            print(f"Library {name} created.")
        else:
            print(f"Library {name} already exists.")

    finally:
        conn.close()

def list_libraries():
    conn = connect()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT library_name, description
                FROM ibmi_libraries
                ORDER BY library_name
            """)

            rows = cur.fetchall()

            print()
            print("Library       Description")
            print("-------------------------------")

            for name, description in rows:
                print(f"{name:<14} {description or ''}")

            print()

    finally:
        conn.close()


def display_library(name):
    name = name.upper()
    conn = connect()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT library_name, description, created_at
                FROM ibmi_libraries
                WHERE library_name = %s
            """, (name,))

            row = cur.fetchone()

            if not row:
                print(f"Library {name} not found.")
                return

            print()
            print("Library:     ", row[0])
            print("Description: ", row[1])
            print("Created:     ", row[2])

            cur.execute("""
                SELECT object_name, object_type, description
                FROM ibmi_objects
                WHERE library_id = (
                    SELECT id FROM ibmi_libraries
                    WHERE library_name = %s
                )
                ORDER BY object_name
            """, (name,))

            objects = cur.fetchall()

            print()
            print("Object       Type       Description")
            print("------------------------------------------")

            for obj, obj_type, desc in objects:
                print(f"{obj:<13}{obj_type:<11}{desc or ''}")

            print()

    finally:
        conn.close()


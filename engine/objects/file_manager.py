
import re

from psycopg2 import sql

from engine.libraries.manager import connect


ALLOWED_TYPES = {
    "INTEGER": "INTEGER",
    "BIGINT": "BIGINT",
    "SMALLINT": "SMALLINT",
    "VARCHAR": "VARCHAR(100)",
    "TEXT": "TEXT",
    "DATE": "DATE",
    "NUMERIC": "NUMERIC(12,2)",
    "DECIMAL": "NUMERIC(12,2)",
    "BOOLEAN": "BOOLEAN"
}


def parse_file_name(value):
    parts = value.upper().split("/")

    if len(parts) != 2:
        raise ValueError("Use LIBRARY/FILE format.")

    library, file_name = parts

    for name in (library, file_name):
        if not re.fullmatch(r"[A-Z0-9_]{1,10}", name):
            raise ValueError(f"Invalid name: {name}")

    return library, file_name


def register_object(cur, library, name, object_type, description):
    cur.execute(
        """
        INSERT INTO ibmi_objects
            (library_id, object_name, object_type, description)
        SELECT id, %s, %s, %s
        FROM ibmi_libraries
        WHERE library_name = %s
        ON CONFLICT (library_id, object_name, object_type)
        DO UPDATE SET description = EXCLUDED.description
        """,
        (name, object_type, description, library)
    )


def create_physical_file(file_name, fields):
    library, name = parse_file_name(file_name)

    if not fields:
        raise ValueError("FIELDS parameter is required.")

    columns = []

    for field in fields.split(","):
        parts = field.strip().upper().split(":")

        if len(parts) != 2:
            raise ValueError(f"Invalid field definition: {field}")

        column_name, column_type = parts

        if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,29}", column_name):
            raise ValueError(f"Invalid field name: {column_name}")

        if column_type not in ALLOWED_TYPES:
            raise ValueError(f"Unsupported field type: {column_type}")

        columns.append((column_name, ALLOWED_TYPES[column_type]))

    conn = connect()

    try:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT id FROM ibmi_libraries WHERE library_name = %s",
                (library,)
            )

            if not cur.fetchone():
                raise ValueError(f"Library {library} does not exist.")

            definitions = [
                sql.SQL("{} {}").format(
                    sql.Identifier(column),
                    sql.SQL(data_type)
                )
                for column, data_type in columns
            ]

            cur.execute(
                sql.SQL("CREATE TABLE {}.{} ({})").format(
                    sql.Identifier(library),
                    sql.Identifier(name),
                    sql.SQL(", ").join(definitions)
                )
            )

            register_object(
                cur, library, name, "PF", "Physical File"
            )

        conn.commit()
        print(f"Physical file {library}/{name} created.")

    finally:
        conn.close()


def create_logical_file(file_name, base_file, order_by):
    library, name = parse_file_name(file_name)
    base_library, base_name = parse_file_name(base_file)

    columns = [column.strip().upper() for column in order_by.split(",")]

    if not columns or not all(
        re.fullmatch(r"[A-Z][A-Z0-9_]{0,29}", col)
        for col in columns
    ):
        raise ValueError("Invalid ORDERBY parameter.")

    conn = connect()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT 1
                FROM ibmi_objects
                WHERE object_name = %s
                  AND object_type = 'PF'
                  AND library_id = (
                      SELECT id FROM ibmi_libraries
                      WHERE library_name = %s
                  )
                """,
                (base_name, base_library)
            )

            if not cur.fetchone():
                raise ValueError(
                    f"Physical file {base_library}/{base_name} not found."
                )

            cur.execute(
                sql.SQL("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = %s
                      AND table_name = %s
                """),
                (base_library, base_name)
            )

            existing_columns = {row[0].upper() for row in cur.fetchall()}

            if not set(columns).issubset(existing_columns):
                raise ValueError("ORDERBY contains an unknown field.")

            cur.execute(
                "SELECT 1 FROM ibmi_libraries WHERE library_name = %s",
                (library,)
            )

            if not cur.fetchone():
                raise ValueError(f"Library {library} does not exist.")

            order_identifiers = sql.SQL(", ").join(
                sql.Identifier(column) for column in columns
            )

            cur.execute(
                sql.SQL("""
                    CREATE VIEW {}.{} AS
                    SELECT * FROM {}.{}
                    ORDER BY {}
                """).format(
                    sql.Identifier(library),
                    sql.Identifier(name),
                    sql.Identifier(base_library),
                    sql.Identifier(base_name),
                    order_identifiers
                )
            )

            register_object(
                cur, library, name, "LF", "Logical File"
            )

        conn.commit()

        print(f"Logical file {library}/{name} created.")

    finally:
        conn.close()


def display_file_description(file_name):
    library, name = parse_file_name(file_name)

    conn = connect()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.object_type, o.description, l.library_name
                FROM ibmi_objects o
                JOIN ibmi_libraries l ON l.id = o.library_id
                WHERE l.library_name = %s
                  AND o.object_name = %s
                """,
                (library, name)
            )

            obj = cur.fetchone()

            if not obj:
                print(f"File {library}/{name} not found.")
                return

            print()
            print("FILE DESCRIPTION")
            print("-----------------------------")
            print(f"File name:    {name}")
            print(f"Library:      {library}")
            print(f"Object type:  {obj[0]}")
            print(f"Description:  {obj[1]}")

            cur.execute(
                sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                    sql.Identifier(library),
                    sql.Identifier(name)
                )
            )

            records = cur.fetchone()[0]

            print(f"Records:      {records}")
            print()

    finally:
        conn.close()


def display_file_fields(file_name):
    library, name = parse_file_name(file_name)

    conn = connect()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT column_name, data_type,
                       character_maximum_length,
                       numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name = %s
                ORDER BY ordinal_position
                """,
                (library, name)
            )

            rows = cur.fetchall()

            if not rows:
                print(f"File {library}/{name} not found.")
                return

            print()
            print(f"FIELD DESCRIPTION: {library}/{name}")
            print("-" * 75)
            print(
                f"{'Field':<15}{'Type':<20}"
                f"{'Length':<12}{'Precision':<12}{'Scale':<8}"
            )
            print("-" * 75)

            for field, data_type, length, precision, scale in rows:
                print(
                    f"{field:<15}{data_type:<20}"
                    f"{str(length or ''):<12}"
                    f"{str(precision or ''):<12}"
                    f"{str(scale or ''):<8}"
                )

            print()

    finally:
        conn.close()

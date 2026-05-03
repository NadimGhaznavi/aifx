# aifx/db/DbMgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import sqlite3
from datetime import datetime, timezone

from aifx.constants.DDef import DDef as DDEF
from aifx.constants.DDb import DDb, DTable

STALE_VALUE = {
    DTable.INSTRUMENTS: DDEF.MAX_INSTRUMENT_AGE
    }

class DbMgr:

    def __init__(self, db_type: str, logfile=None):
        self._db_type = db_type

        if db_type == DDb.CACHE:
            self._db_path = ":memory:"
        else:
            raise ValueError(f"Unrecognized database type: {db_type}")

        try:
            self._conn = sqlite3.connect(self._db_path)
        except sqlite3.Error as exc:
            raise sqlite3.OperationalError(f"Unable to open DB file {self._db_path}") from exc

        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._cursor = self._conn.cursor()

        self._init_db()

    @property
    def conn(self):
        return self._conn

    def _add_updated_ts_column(self, table_name):
        """
        Add a computed (generated) ``updated_ts`` column to a table, if missing.

        ``updated_ts`` is stored as a Unix timestamp computed from the existing
        ``updated_*`` fields. An index is also created on ``updated_ts``.

        This method silently ignores ``ALTER TABLE`` errors if the column
        already exists.

        :param table_name: Name of the table to modify.
        :type table_name: str
        """
        # Avoid raising an exception because the index already exists
        try:
            self._conn.executescript(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN updated_ts INTEGER
                    GENERATED ALWAYS AS (
                        strftime('%s',
                            printf('%04d-%02d-%02d %02d:%02d:%02d',
                                updated_y, updated_mo, updated_d,
                                updated_h, updated_mi, updated_s
                            )
                        )
                    ) VIRTUAL;

                CREATE INDEX IF NOT EXISTS idx_{table_name}_updated_ts
                    ON {table_name}(updated_ts);
                """
            )
        except sqlite3.OperationalError as exc:
            if "duplicate column name" not in str(exc).lower():
                raise

    def close(self):
        self._conn.close()

    def _init_cache(self):
        """Create the in memory schema"""
        self._cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS instruments (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                display_name TEXT NOT NULL,
                pip_location INTEGER NOT NULL,
                margin_rate REAL NOT NULL,
                updated_y INTEGER NOT NULL,
                updated_mo INTEGER NOT NULL,
                updated_d INTEGER NOT NULL,
                updated_h INTEGER NOT NULL,
                updated_mi INTEGER NOT NULL,
                updated_s INTEGER NOT NULL
            );
            """
        )
        self._add_updated_ts_column(DTable.INSTRUMENTS)
        self._conn.commit()

    def _init_db(self):
        if self._db_type == DDb.CACHE:
            self._init_cache()

    def is_stale(self, table: str) -> bool:
        if table not in STALE_VALUE:
            raise ValueError(f"No stale value configured for table: {table}")

        row = self._cursor.execute(
            f"SELECT MAX(updated_ts) FROM {table}"
        ).fetchone()

        if row is None or row[0] is None:
            return True

        now_ts = int(datetime.now(timezone.utc).timestamp())
        age = now_ts - int(row[0])

        return age > STALE_VALUE[table]

    def update(self, table: str, records: list[dict], key_fields: list[str]) -> int:
        if not records:
            return 0

        now = datetime.now(timezone.utc)

        stamped_records = []
        for record in records:
            stamped = dict(record)
            stamped["updated_y"] = now.year
            stamped["updated_mo"] = now.month
            stamped["updated_d"] = now.day
            stamped["updated_h"] = now.hour
            stamped["updated_mi"] = now.minute
            stamped["updated_s"] = now.second
            stamped_records.append(stamped)

        self._upsert_many(
            table=table,
            records=stamped_records,
            key_fields=key_fields,
        )

        return len(stamped_records)


    def _upsert_many(self, table: str, records: list[dict], key_fields: list[str]) -> None:
        fields = sorted(records[0].keys())
        field_set = set(fields)

        for record in records:
            if set(record.keys()) != field_set:
                raise ValueError("Inconsistent record fields")

        columns = ", ".join(fields)
        placeholders = ", ".join(["?"] * len(fields))
        conflict_fields = ", ".join(key_fields)

        update_fields = [
            field for field in fields
            if field not in key_fields
        ]

        if update_fields:
            update_clause = ", ".join(
                f"{field}=excluded.{field}"
                for field in update_fields
            )
            conflict_action = f"DO UPDATE SET {update_clause}"
        else:
            conflict_action = "DO NOTHING"

        sql = f"""
            INSERT INTO {table} ({columns})
            VALUES ({placeholders})
            ON CONFLICT({conflict_fields})
            {conflict_action}
        """

        values = [
            tuple(record[field] for field in fields)
            for record in records
        ]

        with self._conn:
            self._cursor.executemany(sql, values)

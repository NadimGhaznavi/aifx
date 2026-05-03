# aifx/db/DbMgr.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import sqlite3

from aifx.constants.DDb import DDb, DTable

class DbMgr:

    def __init__(self, db_type: str, logfile=None):
        self._db_type = db_type

        if db_type == DDb.CACHE:
            self._db_path = ":memory:"
        else:
            raise ValueError(f"Unrecognized database type: {db_type}")

        try:
            self._conn = sqlite3.connect(self._db_path)
        except:
            raise sqlite3.OperationalError(f"Unable to open DB file {self._db_path}")

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
                pip_value REAL NOT NULL,
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





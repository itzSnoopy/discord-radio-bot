
SCHEMA_NAME: str = "suzaku"

TABLE_SONGS: str = "songs"
COLUMN_SONGS_NAME: str = "name"
COLUMN_SONGS_URL: str = "url"

TABLE_USERS: str = "users"
COLUMN_USERS_USERNAME: str = "name"
COLUMN_USERS_IS_ADMIN: str = "is_admin"

CREATE_SONGS_TABLE = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_SONGS}(
        {COLUMN_SONGS_NAME} TEXT NOT NULL,
        {COLUMN_SONGS_URL} TEXT NOT NULL UNIQUE
    );
    """
SELECT_USER_BY_USERNAME = f"""
    SELECT rowid, {COLUMN_USERS_IS_ADMIN} FROM {TABLE_USERS} WHERE {COLUMN_USERS_USERNAME} = ?;
"""

INSERT_USER = f"""
    INSERT INTO {TABLE_USERS} ({COLUMN_USERS_USERNAME}, {COLUMN_USERS_IS_ADMIN}) VALUES (?, 0);
"""

INSERT_SONG = f"""
    INSERT INTO {TABLE_SONGS} ({COLUMN_SONGS_NAME}, {COLUMN_SONGS_URL}) VALUES (?, ?);
"""

SELECT_SONG_ALL = f"""
    SELECT rowid, {COLUMN_SONGS_NAME}, {COLUMN_SONGS_URL} FROM {TABLE_SONGS};
"""


CREATE_USERS_TABLE = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_USERS}(
        {COLUMN_USERS_USERNAME} TEXT NOT NULL UNIQUE,
        {COLUMN_USERS_IS_ADMIN} INT NOT NULL DEFAULT 0
    );
"""

from sqlite3 import Connection, Error, IntegrityError
from contracts.db_constants import *


def CreateTables(conn: Connection) -> None:
    cur = conn.cursor()
    try:
        cur.execute(CREATE_SONGS_TABLE)
        cur.execute(CREATE_USERS_TABLE)
    finally:
        cur.close()


def IsUser(conn: Connection, username: str) -> bool:
    result: bool = False

    cur = conn.cursor()
    try:
        cur.execute(SELECT_USER_BY_USERNAME, (username,))
        if cur.fetchone():
            result = True

    except Exception as e:
        print(e)
        pass
    finally:
        cur.close()

    return result


def IsAdmin(conn: Connection, username: str) -> bool:
    result: bool = False

    cur = conn.cursor()
    try:
        cur.execute(SELECT_USER_BY_USERNAME, (username,))
        row = cur.fetchone()
        if row:
            result = row[1] == 1

    except Exception as e:
        print(e)
        pass
    finally:
        cur.close()

    return result


def InsertUser(conn: Connection, username: str) -> None:
    cur = conn.cursor()
    try:
        cur.execute(INSERT_USER, (username,))
        conn.commit()
    except Error as e:
        if e is IntegrityError:
            pass
    finally:
        cur.close()


def InsertSong(conn: Connection, song_name: str, song_url: str) -> None:
    cur = conn.cursor()
    try:
        cur.execute(INSERT_SONG, (song_name, song_url))
        conn.commit()
    except Error as e:
        if e is IntegrityError:
            pass
    finally:
        cur.close()


def ReadSongs(conn: Connection) -> dict:
    result: dict = dict()

    cur = conn.cursor()
    try:
        for row in cur.execute(SELECT_SONG_ALL):
            result[row[0]] = f"{row[1]} [{row[2]}]"
        pass
    finally:
        cur.close()

    return result

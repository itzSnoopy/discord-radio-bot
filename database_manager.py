import sqlite3
import contracts.database_models as dbModels
from logging import Logger
from typing import Callable


class DataManager:
    __dbPath: str = None
    __logger: Logger = None

    def __init__(self, dbPath: str, logger: Logger):
        self.__dbPath = dbPath
        self.__logger = logger

    def Connect(self, task: Callable = None, *args):
        try:
            connection = sqlite3.connect(self.__dbPath)

            if task:
                task(connection, *args)

        except sqlite3.Error as e:
            self.__logger.error(e)
        finally:
            connection.close()

    def ConnectWithResponse(self, task: Callable = None, *args):
        result = None

        try:
            connection = sqlite3.connect(self.__dbPath)

            if task:
                result = task(connection, *args)

        except sqlite3.Error as e:
            self.__logger.error(e)
        finally:
            connection.close()

        return result

    def Initialize(self) -> None:
        self.Connect(dbModels.CreateTables)
        self.Connect(dbModels.InsertUser, 'itzSnoopy#1542')
        self.Connect(dbModels.InsertUser, 'eoz#8096')

    def IsUser(self, username: str) -> bool:
        result = self.ConnectWithResponse(dbModels.IsUser, username)

        return result

    def InsertUser(self, username: str) -> None:
        result = self.Connect(dbModels.InsertUser, username)

        return result

    def IsAdmin(self, username: str) -> bool:
        result = self.ConnectWithResponse(dbModels.IsAdmin, username)

        return result

    def InsertSong(self, name, url) -> None:
        self.Connect(dbModels.InsertSong, name, url)

    def ReadSongs(self) -> dict:
        result = self.ConnectWithResponse(dbModels.ReadSongs)

        return result

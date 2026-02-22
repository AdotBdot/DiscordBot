import sqlite3 as sqlite
import os

class DatabaseDriver():
    def __init__(self, logger):
        self.logger = logger

    def initDatabase(self):
        if os.path.isfile("./data/data.db"):
            return
        
        self.createEmptyDatabase()

    def createEmptyDatabase(self):
        pass
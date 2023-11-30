import sqlite3

class DatabaseManager:
    def __init__(self, database='db.sql'):
        self.database = database
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.database)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.commit() 
            self.connection.close()

    def create_table(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    user_id TEXT PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    temp_threshold FLOAT NOT NULL,
                    humidity_threshold FLOAT NOT NULL,
                    light_threshold INTEGER NOT NULL
                )
            ''')

    def insert_data(self):
        query = '''
        INSERT OR IGNORE INTO settings (user_id, user_name, temp_threshold, humidity_threshold, light_threshold)
        VALUES 
            ('AC 85 23 E1', 'Brandon', 25.0, 60.0, 400),
            ('cc8523e1', 'Evan', 23.5, 55.0, 300),
            ('73fc5ea0', 'Phuc', 27.0, 65.0, 600);
        '''

        with self.connection:
            cursor = self.connection.cursor()
            cursor.executescript(query)

    def execute_query(self, query):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result

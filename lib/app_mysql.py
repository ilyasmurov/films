import MySQLdb

class DB:
    db = None
    cursor = None
    
    def __init__(self, db_name, db_user, db_password):
        self.db = MySQLdb.connect(
            host="localhost",
            user=db_user,
            passwd=db_password,
            db=db_name,
            charset='utf8')
        self.cursor = self.db.cursor()
        
    def close(self):
        self.db.close()
        
    def insert(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.lastrowid
        
    def select(self, sql):
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if self.cursor.rowcount > 0:
            return data
        else:
            return False
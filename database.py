import sqlite3 as sql


def connect(func, *args, **kwargs):

    conn = sql.connect("Data.db")
    cur = conn.cursor()
    data = func(cur, *args, **kwargs)
    conn.commit()
    conn.close()
    return data

def valid_date(cur, date: str) -> bool:
    SQL = f"SELECT Date FROM Data WHERE Date = \"{date}\";"
    for i in cur.execute(SQL):
        
        if str(i[0]) == date:
            return False
    return True


def fetch_last_row(cur) -> None:
    SQL = f"""SELECT * FROM Data ORDER BY Date DESC LIMIT 1;"""
    cur.execute(SQL)
    
    return cur.fetchone()

def add_record(cur, date: str, opening: float, result: float, closing: float, capital=None):
    SQL = f"INSERT INTO Data VALUES ('{date}', {opening}, {result}, {capital}, {closing});" 
    cur.execute(SQL)
    


def get_data(cur, start: str, end: str):
    SQL = f'SELECT * FROM Data WHERE Date BETWEEN "{start}" AND "{end}";'
    cur.execute(SQL)
    return cur.fetchall()

def get_closing(cur, start: str, end: str):
    SQL = f'SELECT Date, Opening, Closing FROM Data WHERE Date BETWEEN "{start}" AND "{end}";'
    cur.execute(SQL)
    return cur.fetchall()


def reset_database(cur):
    SQL = f'DROP TABLE IF EXISTS "Data";'
    cur.execute(SQL)

    SQL = '''CREATE TABLE "Data" (
	"Date"	TEXT NOT NULL UNIQUE,
	"Opening"	REAL,
	"Result"	REAL,
	"AddedCapital"	REAL,
	"Closing"	REAL,
	PRIMARY KEY("Date")
);'''
    cur.execute(SQL)

    SQL = f'DROP TABLE IF EXISTS "ScriptResult"'
    cur.execute(SQL)

    SQL = """CREATE TABLE "ScriptResult" (
	"Date"	TEXT NOT NULL,
	"Script"	TEXT NOT NULL,
	"Result"	REAL NOT NULL,
	PRIMARY KEY("Date","Script")
);"""
    cur.execute(SQL)
    print('[RESET COMPLETE]')



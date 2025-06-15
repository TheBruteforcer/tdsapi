from sqlite3 import connect
from json import loads, dumps, load, dump
from Cache.pp import main
import sqlite3
import os

with open("db.json", "r+") as f:
    info = load(f)
print(info)
conn = connect(info["name"])
ref = conn.cursor()

def change_distnation(conn_text):
    print(conn_text)
    with open("db.json", "w") as f:
        dump({"name" : conn_text}, f)

def Create(mode = "xlve"):
    if not mode == "nrml":
        ref.execute(
            """
                CREATE TABLE IF NOT EXISTS Students (
                    ID                 TEXT,
                    Name               TEXT,
                    OwnPhone           TEXT,
                    ParentPhone1       TEXT,
                    ParentPhone2       TEXT,
                    Rank               TEXT,
                    Attendance         TEXT,
                    Tests              TEXT,
                    Badges             TEXT,
                    OPercentage        TEXT,
                    PayHistory         TEXT,
                    SubscribtionAmount TEXT,
                    DroosIn            TEXT,
                    Additions          TEXT
                );
            """
        )
        ref.execute("""CREATE TABLE IF NOT EXISTS Teachers (
                ID        TEXT,
                Name      TEXT,
                Groups    TEXT,
                Additions TEXT
            )""")
        ref.execute(
            """
                CREATE TABLE IF NOT EXISTS Gains (
                    ID   TEXT,
                    Type TEXT,
                    Qnt  TEXT,
                    Date TEXT
                );
            """
        )
        ref.execute(
            """
                CREATE TABLE IF NOT EXISTS Spends (
                    Qnt         TEXT,
                    Date        DATE,
                    Description TEXT,
                    IsSupplies  TEXT
                );
            """
        )
        ref.execute(
            """
            CREATE TABLE IF NOT EXISTS Campigans (
                ID       TEXT,
                Title    TEXT,
                GroupName    TEXT,
                Stats    TEXT
            );
            """
        )
        ref.execute(
            """
                CREATE TABLE IF NOT EXISTS Sessions (
                    ID         TEXT,
                    Title      TEXT,
                    Duration   TEXT,
                    Price      TEXT,
                    Attendance TEXT,
                    SpendsCode TEXT,
                    GainsCode  TEXT,
                    Quiz       TEXT,
                    Tasks      TEXT,
                    Date       DATE,
                    StartTime  TEXT,
                    IsReplace  TEXT
                );
            """
        )
        ref.execute(
            """
                CREATE TABLE IF NOT EXISTS TSessions (
                    ID                  TEXT,
                    Title               TEXT,
                    Duration            TEXT,
                    PredictedAttendance TEXT,
                    RealAttendance      TEXT,
                    PresvPrice          TEXT,
                    Quiz                TEXT,
                    Date                TEXT,
                    Hour                TEXT,
                    IsReplace           TEXT
                );
            """
        )
        ref.execute(
            '''
            CREATE TABLE IF NOT EXISTS PGroups (
                ID       INTEGER,
                Name     TEXT,
                PayType  TEXT,
                JoinedNumber INTEGER
            );
            '''
        )
        ref.execute(
            '''
            CREATE TABLE IF NOT EXISTS Groups (
                Name     TEXT
            );
            '''
        )
        ref.execute(
            '''
            CREATE TABLE IF NOT EXISTS InvSessions (
                ID    INTEGER,
                Name  TEXT,
                JoinedNumber INTEGER,
                PayQuantity  INTEGER,
                Time         TEXT
            );
            '''
        )
        ref.execute(
    """
    CREATE TABLE IF NOT EXISTS Exams (
        ID          TEXT,
        Name        TEXT,
        Max         TEXT,
        Degrees     TEXT,
        Price       TEXT,
        IsInSession TEXT,
        StartDate   TEXT,
        Duration    TEXT
    );
    """)
        main()
        conn.commit()



def create_db_connection(db_path='Application.db'):
    """
    Create a database connection to the SQLite database specified by db_path.
    
    :param db_path
    : Path to the SQLite database file
    :return: Connection object or None
    """
    try:
        with open("db.json", "r+") as f:
            info = load(f)
        conn = sqlite3.connect(info["name"])  # Create a connection to the database
        conn.row_factory = sqlite3.Row   # This allows fetching rows as dictionaries
        return conn
    except sqlite3.Error as e:
        print(f"Error creating connection to database: {e}")
        return None

# --- Codes DB Management ---
def init_codes_db():
    db_path = os.path.join(os.path.dirname(__file__), 'Codes.db')
    conn = sqlite3.connect(db_path)
    ref = conn.cursor()
    ref.execute('''
        CREATE TABLE IF NOT EXISTS PendingCodes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID INTEGER,
            StudentName TEXT,
            DateAdded TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_pending_code(student_id, student_name, date_added):
    db_path = os.path.join(os.path.dirname(__file__), 'Codes.db')
    conn = sqlite3.connect(db_path)
    ref = conn.cursor()
    ref.execute('''
        INSERT INTO PendingCodes (StudentID, StudentName, DateAdded) VALUES (?, ?, ?)
    ''', (student_id, student_name, date_added))
    conn.commit()
    conn.close()

def get_all_pending_codes():
    db_path = os.path.join(os.path.dirname(__file__), 'Codes.db')
    conn = sqlite3.connect(db_path)
    ref = conn.cursor()
    ref.execute('SELECT * FROM PendingCodes')
    rows = ref.fetchall()
    conn.close()
    return rows

def delete_all_pending_codes():
    db_path = os.path.join(os.path.dirname(__file__), 'Codes.db')
    conn = sqlite3.connect(db_path)
    ref = conn.cursor()
    ref.execute('DELETE FROM PendingCodes')
    conn.commit()
    conn.close()


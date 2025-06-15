from sqlite3 import *

conn = connect("تجريبي شهر.db")
curs = conn.cursor()

curs.execute("SELECT * FROM Students")
print(curs.fetchall())
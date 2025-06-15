import random
import json
from sqlite3 import connect

# List of Arabic names
arabic_names = [
    "محمد أحمد",
    "علي حسن",
    "محمود سعيد",
    "خالد عمر",
    "أحمد علي",
    "فاطمة محمد",
    "سارة خالد",
    "ليلى أحمد",
    "نور محمد",
    "ريم علي",
    "عمر خالد",
    "ياسر محمود",
    "أمينة فاطمة",
    "حسن سعيد",
    "سعيد محمود",
    "مريم أحمد",
    "نادية علي",
    "هبة محمد",
    "إيمان خالد",
    "عائشة محمود",
]

def add_dummy_students(db_name, count=10):
    # Connect to the database
    conn = connect(db_name)
    ref = conn.cursor()
    
    # Get the last student ID
    ref.execute('SELECT ID FROM Students ORDER BY ID DESC LIMIT 1')
    last_student = ref.fetchone()
    start_id = 1 if last_student is None else int(last_student[0]) + 1
    
    for i in range(start_id, start_id + count):
        # Generate random student data
        student_data = {
            'id': i,
            'name': random.choice(arabic_names),
            'phone': f"01{random.randint(100000000, 999999999)}",
            'parent_phone': f"01{random.randint(100000000, 999999999)}",
            'second_parent_phone': f"01{random.randint(100000000, 999999999)}",
            'payment_type': random.choice(["بالحصة", "بالشهر"]),
            'group': "1 | لغة عربية"
        }
        
        # Generate payment data if monthly payment
        if student_data['payment_type'] == "بالشهر":
            payment_mode = random.choice(["بداية الشهر", "نهاية الشهر"])
            
            def get_expire_date(month_index):
                if payment_mode == "نهاية الشهر":
                    return f"30/{month_index + 3}"
                else:
                    return f"27/{month_index + 2}, 10/{month_index + 3}"
            
            payment_data = [
                {
                    "month": f"شهر {month_index + 3}",
                    "state": "لم يدفع",
                    "date_payed": "",
                    "expire": get_expire_date(month_index)
                }
                for month_index in range(3)
            ]
        else:
            payment_data = "BySession"
        
        # Insert student into database
        ref.execute(
            """
                INSERT INTO Students VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                student_data['id'],
                student_data['name'],
                student_data['phone'],
                student_data['parent_phone'],
                student_data['second_parent_phone'],
                i,  # student_id
                '[{}]',  # sessions
                '[{}]',  # exams
                'Temp' if student_data['payment_type'] == "بالشهر" else student_data['group'],
                '0',  # paid
                json.dumps(payment_data) if student_data['payment_type'] == "بالشهر" else payment_data,
                "0",  # total_paid
                "[]",  # notes
                "{}"   # extra_data
            )
        )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print(f"Successfully added {count} dummy students to {db_name}")

# Run the function
add_dummy_students("اولى ابتدائي.db", count=20)

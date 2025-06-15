import sqlite3
import json
from time import localtime
from requests import post
from json import loads, dumps
from threading import Thread
import os
from sqlite3 import *
data = {"stages" : [], "students" : {}}
def calculate_attendance_percentage(student_id, session_titles, replacement_map, conn):
    print(f"Calculating attendance for student {student_id}")
    cursor = conn.cursor()

    cursor.execute("SELECT Attendance FROM Students WHERE ID = ?", (student_id,))
    attendance_records_str = cursor.fetchone()[0]
    print(f"Attendance record fetched: {attendance_records_str}")

    if attendance_records_str:
        attendance_records = json.loads(attendance_records_str)
    else:
        return 0.0

    attended_sessions = set()
    for record in attendance_records:
        for session_title, status in record.items():
            if status == "Attended.":
                if session_title in replacement_map:
                    attended_sessions.add(replacement_map[session_title])
                else:
                    attended_sessions.add(session_title)

    total_sessions = len(session_titles)
    attended_count = len(attended_sessions)
    percentage = (attended_count / total_sessions) * 100 if total_sessions > 0 else 0
    print(f"Student {student_id} attendance percentage: {percentage}")
    return round(percentage, 2)

def update_student_percentage(student_id, percentage, conn):
    print(f"Updating student {student_id} attendance percentage to {percentage}")
    cursor = conn.cursor()
    cursor.execute("UPDATE Students SET OPercentage = ? WHERE ID = ?", (percentage, student_id))
    conn.commit()

def calculate_test_scores(student_id, conn):
    print(f"Calculating test scores for student {student_id}")
    cursor = conn.cursor()
    cursor.execute("SELECT Tests FROM Students WHERE ID = ?", (student_id,))
    tests_str = cursor.fetchone()[0]
    print(f"Test records fetched: {tests_str}")

    if tests_str:
        tests = json.loads(tests_str)
        tests = [test for test in tests if test]
    else:
        return 0.0

    total_score = sum(float(test['degree']) for test in tests)
    print(f"Total test score for student {student_id}: {total_score}")
    return total_score

def calculate_weighted_score(attendance_percentage, test_score, attendance_weight=0.4, test_weight=0.6):
    score = (attendance_percentage * attendance_weight) + (test_score * test_weight)
    print(f"Calculated weighted score: {score}")
    return score

def process_group(group, student_ids, conn):
    print(f"Processing group {group}")
    o_percentage_values = []
    students_data = []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Sessions WHERE StartTime = ?", (group,))
    all_sessions = cursor.fetchall()
    session_titles = {session[1] for session in all_sessions}
    replacement_map = {}

    for session in all_sessions:
        try:
            session_id, title, _, _, _, _, _, _, _, _, _, is_replace = session
            if is_replace:
                replacement_map[title] = is_replace
        except:
            session_id, title, _, _, _, _, _, _, _, _, is_replace = session
            if is_replace:
                replacement_map[title] = is_replace

    print(f"Sessions fetched: {session_titles}")

    cursor.execute("SELECT ID, DroosIn FROM Students WHERE SubscribtionAmount != 'BySession'")
    month_payers = cursor.fetchall()
    print("month payers  -----> ", month_payers)
    for student_id, droosin_str in month_payers:
        droosin = json.loads(droosin_str) if droosin_str else []
        droosinlst = [droosini["name"] for droosini in droosin]
        if ((group).split("|")[1]).strip() in droosinlst:
            student_ids.append(student_id)

    for student_id in student_ids:
        attendance_percentage = calculate_attendance_percentage(student_id, session_titles, replacement_map, conn)
        test_scores = calculate_test_scores(student_id, conn)
        weighted_score = calculate_weighted_score(attendance_percentage, test_scores)
        update_student_percentage(student_id, attendance_percentage, conn)
        o_percentage_values.append(attendance_percentage)
        students_data.append({'student_id': student_id, 'attendance_percentage': attendance_percentage, 'test_scores': test_scores, 'weighted_score': weighted_score})
    return o_percentage_values, students_data

def main2(conn_name):
    print(f"Connecting to database {conn_name}")
    conn = sqlite3.connect(conn_name)
    cursor = conn.cursor()
    ref = conn.cursor()
    today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
    print(f"Fetching data for {today}")

    ref.execute('SELECT * FROM Gains WHERE Date = ?', (today,))
    gains = sum(int(g[2]) for g in ref.fetchall())
    ref.execute('SELECT * FROM Spends WHERE Date = ?', (today,))
    spends = sum(int(s[0]) for s in ref.fetchall())
    print(f"Total gains: {gains}, Total spends: {spends}")

    cursor.execute("SELECT DISTINCT Badges FROM Students")
    groups = cursor.fetchall()

    for group_tuple in groups:
        group = group_tuple[0]
        if group == "Temp":
            continue
        
        # Sanitize group name for file path
        sanitized_group = group.replace("|", "_").replace(" ", "_")
        
        cursor.execute("SELECT ID FROM Students WHERE Badges = ?", (group,))
        student_ids = [student_id_tuple[0] for student_id_tuple in cursor.fetchall()]
        o_percentage_values, students_data = process_group(group, student_ids, conn)

        average_o_percentage = sum(o_percentage_values) / len(o_percentage_values) if o_percentage_values else 0
        highest_o_percentage = max(o_percentage_values) if o_percentage_values else 0
        higher_than_average = len([op for op in o_percentage_values if op >= average_o_percentage])
        lower_than_average = len([op for op in o_percentage_values if op < average_o_percentage])

        cache_data = {
            'group': group,
            'average_o_percentage': average_o_percentage,
            'highest_o_percentage': highest_o_percentage,
            'higher_than_average': higher_than_average,
            'lower_than_average': lower_than_average
        }
        os.makedirs(conn_name.replace(".db", ""), exist_ok=True)
        with open(f'{conn_name.replace(".db", "")}/cache_{sanitized_group}.json', 'w') as cache_file:
            json.dump(cache_data, cache_file)
        print(f"Cache saved for group {group}")
    
    # info processing
    
    data["students"][conn_name.replace(".db", "")] = []
    ref.execute("SELECT * FROM Students")
    stds = ref.fetchall()
    for std in stds:
        quizzes = list(loads(std[7]))
        quizzes.pop(0)
        attendances_record = []
        if std[10] == "BySession":
            ref.execute("SELECT * FROM Sessions WHERE StartTime = ?", (std[8],))
            all_sessions = ref.fetchall()
            print("Sessions ----------------> ", all_sessions)
            for session in all_sessions:
                if any(d.get(session[1]) == 'Attended.' for d in loads(std[6])):
                    attendances_record.append({"session_name" : session[1], "attended" : True})
                else:
                    attendances_record.append({"session_name" : session[1], "attended" : False})
        else:
            groups_std = [group["name"] for group in loads(std[12])]
            ref.execute("SELECT * FROM Groups")
            groups_all = ref.fetchall()
            print(groups_all)
            print(groups_std)
            for _group in groups_all:
                if (_group[0].split("|")[1]).strip() in groups_std:
                    print("YES !")
                    ref.execute("SELECT * FROM Sessions WHERE StartTime = ?", (_group[0],))
                    all_sessions = ref.fetchall()
                    print("Sessions ----------------> ", all_sessions)
                    for session in all_sessions:
                        if any(d.get(session[1]) == 'Attended.' for d in loads(std[6])):
                            attendances_record.append({"session_name" : session[1], "attended" : True})
                        else:
                            attendances_record.append({"session_name" : session[1], "attended" : False})
                    
        payhistory = std[10]
        data["students"][conn_name.replace(".db", "")].append({
            "student_code" : std[0],
            "student_name" : std[1],
            "student_owned_phone" : std[2],
            "student_1st_parent_phone" : std[3],
            "student_2nd_parent_phone" : std[4],
            "student_rank" : std[5],
            "student_group_or_groups_list" : std[8] if std[10] == "BySession" else [group["name"] for group in loads(std[12])],
            "tests_grades" : [{"_title" : quiz["title"], "_degree" : quiz["degree"], "_of_session_title" : quiz["session-data"]["title"]} for quiz in quizzes],
            "attendance_percentage" : f"{std[9]} %",
            "median_attendance_percentage_of_group" : average_o_percentage,
            "monthly_payment_history" : loads(payhistory) if std[10] != "BySession" else "هذا الطالب يقوم بالدفع بالحصة",
            "monthly_subscribtion_amount" : std[11] if std[10] != "BySession" else "هذا الطالب يقوم بالدفع بالحصة",
            "attendances" :  attendances_record
        })
        print("\n\n\n\n\n\n",data,"\n\n\n\n\n\n")

    conn.close()

def main():
    for db in [file for file in os.listdir(".") if file.endswith(".db") and "journal" not in file]:
        data["stages"].append(db.replace(".db", ""))
        main2(db)
    try:
        print(post("https://tdsworks.pythonanywhere.com/store", json=data).text)
    except Exception as e:
        print(e)

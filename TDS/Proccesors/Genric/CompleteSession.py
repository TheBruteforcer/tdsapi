from json import dumps, loads
from Proccesors.Database.db import *
from Views import Dashboard, DoneSession
from customtkinter import *
from Cache.pp import main
def complete(frame, session_data):
    qpath = 7
    apath = 4
    dpath = 9
    inpath = 2
    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
    session_data = ref.fetchone()
    quiz_data = loads(session_data[qpath])
    if quiz_data != []:
        if len(quiz_data['degrees']) == int(session_data[apath]):
            ref.execute('INSERT INTO Exams VALUES (?,?,?,?,?,?,?,?)', (
            'NW-0',
            quiz_data['title'], 
            quiz_data['max'], 
            dumps(quiz_data['degrees']), 
            'DONE',
            dumps({'name':session_data[1], 'id':session_data[0]}),
            session_data[dpath],
            session_data[2]
            ))
            conn.commit()
            for x in frame.winfo_children():
                x.destroy()
            main()
            DoneSession.show_complete(frame, session_data)
        else:
            ref.execute('INSERT INTO Exams VALUES (?,?,?,?,?,?,?,?)', (
            'NW-0',
            quiz_data['title'], 
            quiz_data['max'], 
            dumps(quiz_data['degrees']), 
            'PENDING',
            dumps({'name':session_data[1], 'id':session_data[0]}), 
            session_data[dpath],
            session_data[2]
            ))
            conn.commit()
            for x in frame.winfo_children():
                x.destroy()
            
            # main()
            DoneSession.show_complete(frame, session_data)

    else:
        for x in frame.winfo_children():
            x.destroy()
        
        #main()
        DoneSession.show_complete(frame, session_data)

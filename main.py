from fastapi import FastAPI, Query
from json import dump, load

with open('info.json', 'w') as data:
    dump(
        {'msname' : '',
         'stdnum' : 0,
         'sessions' : {
                        '1': {'attendance' : ['2', '40']}
                    }
         },
        data
    )
    data.close()

app=FastAPI()
@app.post('/attend/{data}')
def attend(data : str):
    splitted_data = data.split('|')
    code = splitted_data[0]
    sscode = splitted_data[1]
    with open('info.json', 'w') as data:
        js = load(data)
        js['sessions'][sscode] = {'attendance' : []}
        js['sessions'][sscode]['attendance'].append(code)
        dump(js, data)

@app.get('/sa')
def sa():
    return load(open('info.json', 'w'))
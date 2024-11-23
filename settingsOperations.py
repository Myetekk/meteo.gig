import json
import os
import sqlite3
import datetime
        




## ustawia ustawienia domyślne i zapisuje w pliku JSON 
def createDefaultSettings(settings):
    settings.updateTime = 600

    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\settings.json", "w") as outfile:
            data = { "updateTime": int(settings.updateTime) }
            json_object = json.dumps(data, indent=3)
            outfile.write(json_object)


    except Exception as e:
        print(f"An error occurred in createDefaultSettings: {e}")
        saveError(e, "createDefaultSettings")





## ładuje ustawienia z pliku JSON, jeśli napotka jakieś problemy  -->  ustawia ustawienia domyślne
def loadSettings(settings):
    filePath = "outputs\\settings.json"
    
    try:
        if os.path.exists(filePath):  ## jeśli plik istnieje 
            fileSize = os.path.getsize(filePath)
            if fileSize >= 20  and  fileSize <= 40:  ## jeśli plik ma w sobie jakieś dane i są odpowiednio długie
                with open(filePath) as outfile:
                    data = json.load(outfile)

                    settings.updateTime = int(data["updateTime"])
            else: 
                createDefaultSettings(settings)
        else:
            createDefaultSettings(settings)
        
        
    except Exception as e:
        print(f"An error occurred in loadSettings: {e}. Using default settings")
        saveError(e, "loadSettings")
        createDefaultSettings(settings)










## loguje errory do pliku .txt;   ta sama funkcja co w 'utils.py', poniewać circular import
def saveError(message, locatin):
    try:
        path = "outputs\\logs.db"
        conn = sqlite3.connect(path)
        cur = conn.cursor()

        sql1 ='''CREATE TABLE IF NOT EXISTS errors (
            date	TEXT NOT NULL,
            message	TEXT NOT NULL,
            locatin	TEXT NOT NULL
        );'''
        cur.execute(sql1)

        sql2 ='''INSERT INTO errors (date, message, locatin) VALUES (?, ?, ?);'''
        cur.execute(sql2, [str(datetime.datetime.now()), str(message), str(locatin)])

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred in saveLogsError: {e}.")

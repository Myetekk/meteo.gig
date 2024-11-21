import tkinter as tk
import urllib.request  
import time
import datetime
import os
import sqlite3
import threading
from pyModbusTCP.server import ModbusServer, DataBank





class Meteo:
    arrayText = []
    arrayHeaderTextLine0 = ""
    arrayHeaderTextLine1 = ""
    arrayCurrentText = ""
    for i in range(36):
        arrayCurrentText += "0  " 
    
    arrayHeader = ["x" for i in range(36)]
    arrayCurrent = ["0" for i in range(36)]

    arrayCurrentModbus = [0 for i in range(36)]
    
    dataBank = DataBank()


    
    def main(self):
        ## host modbus server
        self.server = ModbusServer(host='0.0.0.0', port=502, no_block=True, data_bank=self.dataBank)
        self.server.start()

        ## send life signal
        inteager_thread = threading.Thread(target=self.sendModbusLifeSignal, daemon=True)
        inteager_thread.start()

        self.getData()
        self.Modbus()
        self.createInterface()


    
    def getData(self):
        self.getDataText()
        self.makeHeaders()
        self.makeCurrent()
        
        self.saveLogsData()


    def getDataText(self):
        try:
            url = "https://meteo.gig.eu/archiwum/aktualne.txt"
            file = urllib.request.urlopen(url, timeout=5)
            self.arrayText = []

            for line in file:
                self.arrayText.append(line.decode('utf-8'))
            
            arrayLength = len(self.arrayText)
            self.arrayHeaderTextLine0 = self.arrayText[0]
            self.arrayHeaderTextLine1 = self.arrayText[1]
            self.arrayCurrentText = self.arrayText[arrayLength-1]
        except Exception as e:
            print(f"An error occurred in getDataText: {e}")
            self.saveLogsError(e)
            for i in range(36):
                self.arrayCurrentText += "0  " 

    
    def makeHeaders(self):
        try:
            self.arrayHeaderLine0 = self.arrayHeaderTextLine0.split()
            self.arrayHeaderLine1 = self.arrayHeaderTextLine1.split()

            self.arrayHeader.clear()
            for index in range(len(self.arrayHeaderLine1)):
                if index == 21: 
                    self.arrayHeaderLine0[21] += ' ' + self.arrayHeaderLine0[22]
                    self.arrayHeaderLine0.pop(22)
                
                if (index in [0, 1, 16, 17, 31]):
                    self.arrayHeaderLine0.insert(index, '')
                    self.arrayHeader.append(self.arrayHeaderLine1[index])
                else:
                    self.arrayHeader.append(self.arrayHeaderLine0[index] + ' ' + self.arrayHeaderLine1[index])
        except Exception as e:
            print(f"An error occurred in makeHeaders: {e}")
            self.saveLogsError(e)
            self.arrayHeader = ["x" for i in range(36)]


    def makeCurrent(self):
        try:
            self.arrayCurrent = self.arrayCurrentText.split()
        except Exception as e:
            print(f"An error occurred in makeCurrent: {e}")
            self.saveLogsError(e)
            self.arrayCurrent = ["0" for i in range(36)]





    def Modbus(self):
        self.prepareModbus()
        self.sendModbus()


    def prepareModbus(self):
        try:
            arrayCurrentModbusTemp = self.arrayCurrent
            
            self.arrayCurrentModbus.clear()
            for index in range(len(arrayCurrentModbusTemp)):
                try:
                    self.arrayCurrentModbus.append(float(arrayCurrentModbusTemp[index]))

                except Exception as e:
                    if arrayCurrentModbusTemp[index].find("---") != -1:  ## no data / error
                        self.arrayCurrentModbus[index].append(0)
                    
                    ## wind directions
                    elif arrayCurrentModbusTemp[index].find("N") != -1:  ## wind direction NORTH- 1
                        self.arrayCurrentModbus.append(1)
                    elif arrayCurrentModbusTemp[index].find("E") != -1:  ## wind direction EAST-  2
                        self.arrayCurrentModbus.append(2)
                    elif arrayCurrentModbusTemp[index].find("S") != -1:  ## wind direction SOUTH- 3
                        self.arrayCurrentModbus.append(3)
                    elif arrayCurrentModbusTemp[index].find("W") != -1:  ## wind direction WEST-  4
                        self.arrayCurrentModbus.append(4)

                    elif arrayCurrentModbusTemp[index].find("-") != -1:  ## date
                        sliced = arrayCurrentModbusTemp[index].split('-')
                        self.arrayCurrentModbus.append(2000+int(sliced[0]))
                        self.arrayCurrentModbus.append(int(sliced[1]))
                        self.arrayCurrentModbus.append(int(sliced[2]))
                    elif arrayCurrentModbusTemp[index].find(":") != -1:  ## time
                        sliced = arrayCurrentModbusTemp[index].split(':')
                        self.arrayCurrentModbus.append(int(sliced[0]))
                        self.arrayCurrentModbus.append(int(sliced[1]))
                        
                    else:
                        self.arrayCurrentModbus.append(arrayCurrentModbusTemp[index])
        except Exception as e:
            print(f"An error occurred in prepareModbus: {e}")
            self.saveLogsError(e)
            self.arrayCurrentModbus = [0 for i in range(36)]


    def sendModbus(self):
        try:
            date = datetime.datetime.now()

            ## clear list
            blancList = []
            for i in range(125):   blancList += [0] 
            self.dataBank.set_input_registers(address=0, word_list=blancList)

            ## sets date and time
            dateList = [date.year] + [date.month] + [date.day] + [date.hour] + [date.minute] + [date.second]
            self.dataBank.set_input_registers(address=0, word_list=dateList) 


            dateList = self.arrayCurrentModbus
            self.dataBank.set_input_registers(address=10, word_list=dateList) 
        except Exception as e:
            print(f"An error occurred in sendModbus: {e}")
            self.saveLogsError(e)
            self.sendModbus()


    def sendModbusLifeSignal(self):
        try:
            integer = 0
            while True:
                self.dataBank.set_input_registers(address=6, word_list=[integer])
                integer += 1
                if integer == 10: integer=0
                time.sleep(1)
        except Exception as e:
            print(f"An error occurred in sendModbusLifeSignal: {e}")
            self.saveLogsError(e)
            self.sendModbusLifeSignal()

    



    def createInterface(self):
        try:
            self.window = tk.Tk()
            self.window.title('meteo.gig')
            self.window.resizable(False, False)
            self.window.geometry("+20+20")
            
            self.createInterfaceHeader()
            self.populateInterface()
            
            self.window.mainloop()
        except Exception as e:
            print(f"An error occurred in createInterface: {e}")
            self.saveLogsError(e)
    


    def createInterfaceHeader(self):
        try:
            headerFrame = tk.Frame(self.window)
            tk.Button(headerFrame, text="REFRESH").pack(side='left', padx=15)
            tk.Button(headerFrame, text="JSON", command=self.exportJSON).pack(side='left', padx=15)
            headerFrame.pack(padx=40, pady=15)
        except Exception as e:
            print(f"An error occurred in createInterfaceHeader: {e}")
            self.saveLogsError(e)
    


    def populateInterface(self):
        try:
            dataFrame = tk.Frame(self.window)
            secondColumn = 0
            for index in range(len(self.arrayHeader)): 
                rowIndex = index
                if (index >= len(self.arrayHeader)/2): 
                    secondColumn = 3
                    rowIndex -= int(len(self.arrayHeader)/2)
                tk.Label(dataFrame, text=(self.arrayHeader[index])).grid(row=rowIndex+1, column=(0+secondColumn), sticky='E', padx=5)
                tk.Label(dataFrame, text=(self.arrayCurrent[index])).grid(row=rowIndex+1, column=(1+secondColumn), sticky='W', padx=5)
                tk.Label(dataFrame, text=('|')).grid(row=rowIndex+1, column=(2), padx=15)
            dataFrame.pack(padx=40, pady=15)
        except Exception as e:
            print(f"An error occurred in populateInterface: {e}")
            self.saveLogsError(e)

    



    def exportJSON(self):
        try:
            if os.path.exists("outputs") == False: os.mkdir("outputs") 
            with open("outputs\\data.json", "w") as outfile:
                outfile.write('{\n')
                for index in range(len(self.arrayHeader)):
                    outfile.write('  "' + self.arrayHeader[index] + '": "' + self.arrayCurrent[index] + '"')
                    if index < len(self.arrayHeader)-1: outfile.write(", \n")
                outfile.write('\n}')
        except Exception as e:
            print(f"An error occurred in exportJSON: {e}.")
            self.saveLogsError(e)

    

    def saveLogsData(self):
        try:
            path = "outputs\\logs.db"
            conn = sqlite3.connect(path)
            cur = conn.cursor()

            sql1 ='''CREATE TABLE IF NOT EXISTS data (
                upload_date	    TEXT NOT NULL,
                data      TEXT NOT NULL
            );'''
            cur.execute(sql1)

            sql2 ='''INSERT INTO data (upload_date, data) VALUES (?, ?);'''
            cur.execute(sql2, [str(datetime.datetime.now()), str(self.arrayCurrent)])

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred in saveLogsData: {e}.")

    

    def saveLogsError(self, message):
        try:
            path = "outputs\\logs.db"
            conn = sqlite3.connect(path)
            cur = conn.cursor()

            sql1 ='''CREATE TABLE IF NOT EXISTS errors (
                date	TEXT NOT NULL,
                message	TEXT NOT NULL
            );'''
            cur.execute(sql1)

            sql2 ='''INSERT INTO errors (date, message) VALUES (?, ?);'''
            cur.execute(sql2, [str(datetime.datetime.now()), str(message)])

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred in saveLogsError: {e}.")





if __name__ == '__main__':
    meteo = Meteo()
    meteo.main()





## TO DO
## - zapętlić 
## - zapezpieczyć przed "HTTP Error 500: Internal Server Error"

## + logować dane i errory 
## + pozabezpieczać 



## PYTANIA
## - wystarczą w formie intów czy robić na floaty? 
## - jak często ma się odświeżać? 
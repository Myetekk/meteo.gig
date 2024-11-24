import tkinter as tk
import urllib.request  
import time
import datetime
import os
import sqlite3
import threading
from pyModbusTCP.server import ModbusServer, DataBank
from settingsOperations import loadSettings





class Settings:
    updateTime = 600  ## seconds





class Meteo:
    errors = 0

    arrayText = []
    arrayHeaderTextLine0 = ""
    arrayHeaderTextLine1 = ""
    arrayCurrentText = ""
    for i in range(36):  arrayCurrentText += "0  " 
    
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
        
        self.settings = Settings()
        loadSettings(self.settings)

        if self.tryInternetConnection():  self.getData()
        self.Modbus()
        self.createInterface()


    
    ## manages getting data - downloads data and converts it
    def getData(self):
        self.getDataText()
        self.makeHeaders()
        self.makeCurrent()
        
        self.saveLogsData()


    ## gets data in text form
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
            self.saveLogsError(e, "getDataText")
            self.errors += 1
            if self.errors <= 20: 
                self.getDataText()
            else: 
                for i in range(36):
                    self.arrayCurrentText += "0  " 


    ## gets headers from data and converts it     
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
            self.saveLogsError(e, "makeHeaders")
            self.arrayHeader = ["x" for i in range(36)]


    ## gets current data and converts it
    def makeCurrent(self):
        try:
            self.arrayCurrent = self.arrayCurrentText.split()
        except Exception as e:
            print(f"An error occurred in makeCurrent: {e}")
            self.saveLogsError(e, "makeCurrent")
            self.arrayCurrent = ["0" for i in range(36)]





    ## manages sending data with Modbus - converts data to numbers and sends it
    def Modbus(self):
        self.prepareModbus()
        self.sendModbus()


    ## converts data from strings t onumbers
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
            self.saveLogsError(e, "prepareModbus")
            self.arrayCurrentModbus = [0 for i in range(36)]


    ## sends data with Modbus
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
            self.saveLogsError(e, "sendModbus")
            self.sendModbus()


    ## sends lifesignal indicating whether app still works
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
            self.saveLogsError(e, "sendModbusLifeSignal")
            self.sendModbusLifeSignal()

    



    ## creates new window with interface
    def createInterface(self):
        try:
            self.window = tk.Tk()
            self.window.title('meteo.gig')
            self.window.resizable(False, False)
            self.window.geometry("+20+20")
            
            self.createInterfaceHeader()
            self.populateInterface()

            self.afterFunc = self.window.after(self.settings.updateTime*1000, self.updateData)
            
            self.window.mainloop()
        except Exception as e:
            print(f"An error occurred in createInterface: {e}")
            self.saveLogsError(e, "createInterface")
    

    ## creates 'header' with buttons
    def createInterfaceHeader(self):
        try:
            headerFrame = tk.Frame(self.window)
            tk.Button(headerFrame, text="REFRESH", command=self.refreshData).pack(side='left', padx=15)
            tk.Button(headerFrame, text="JSON", command=self.exportJSON).pack(side='left', padx=15)
            headerFrame.pack(padx=40, pady=15)
        except Exception as e:
            print(f"An error occurred in createInterfaceHeader: {e}")
            self.saveLogsError(e, "createInterfaceHeader")


    ## inserts data into interface
    def populateInterface(self):
        try:
            self.dataFrame = tk.Frame(self.window)
            secondColumn = 0
            for index in range(len(self.arrayHeader)): 
                rowIndex = index
                if (index >= len(self.arrayHeader)/2): 
                    secondColumn = 3
                    rowIndex -= int(len(self.arrayHeader)/2)
                tk.Label(self.dataFrame, text=(self.arrayHeader[index])).grid(row=rowIndex+1, column=(0+secondColumn), sticky='E', padx=5)
                tk.Label(self.dataFrame, text=(self.arrayCurrent[index])).grid(row=rowIndex+1, column=(1+secondColumn), sticky='W', padx=5)
                tk.Label(self.dataFrame, text=('|')).grid(row=rowIndex+1, column=(2), padx=15)
            self.dataFrame.pack(padx=40, pady=15)
        except Exception as e:
            print(f"An error occurred in populateInterface: {e}")
            self.saveLogsError(e, "populateInterface")


    ## updates app - downloads new data and inserts it into interface
    def updateData(self):
        try:
            print("updating " + str(datetime.datetime.now())[:19] + "..")
            self.dataFrame.destroy()
            
            if self.tryInternetConnection():  self.getData()
            self.populateInterface()
            self.Modbus()

            loadSettings(self.settings)
            self.afterFunc = self.window.after(self.settings.updateTime*1000, self.updateData)

            self.errors = 0
            print("updated")
        except Exception as e:
            print(f"An error occurred in updateData: {e}")
            self.saveLogsError(e, "updateData")
            self.errors += 1
            if self.errors <= 20: self.updateData()
    

    ## updates app on request (button click)
    def refreshData(self):
        self.window.after_cancel(self.afterFunc)
        self.updateData()

    



    ## checks whether app can access internet
    def tryInternetConnection(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True
        
        except urllib.request.URLError as err: 
            print('no internet connection')
            self.saveLogsError('no internet connection', "tryInternetConnection")
            return False
    

    ## exports data to .json file
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
            self.saveLogsError(e, "exportJSON")

    
    ## saves data in database
    def saveLogsData(self):
        try:
            path = "outputs\\logs.db"
            conn = sqlite3.connect(path)
            cur = conn.cursor()

            sql1 = '''CREATE TABLE IF NOT EXISTS odczyt_''' + str(datetime.datetime.now()).replace("-", "_")[:10] + ''' (
                upload_date	    TEXT NOT NULL,
                data      TEXT NOT NULL
            );'''
            cur.execute(sql1)

            sql2 ='''INSERT INTO odczyt_''' + str(datetime.datetime.now()).replace("-", "_")[:10] + ''' (upload_date, data) VALUES (?, ?);'''
            cur.execute(sql2, [str(datetime.datetime.now()), str(self.arrayCurrent)])

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred in saveLogsData: {e}.")

    
    ## saves error in database
    def saveLogsError(self, message, locatin):
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





if __name__ == '__main__':
    meteo = Meteo()
    meteo.main()
    
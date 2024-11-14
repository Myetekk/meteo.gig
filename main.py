import tkinter as tk
import urllib.request  
import time
import datetime
import os
import threading
from pyModbusTCP.server import ModbusServer, DataBank





class Meteo:
    arrayText = []
    arrayHeaderTextLine0 = []
    arrayHeaderTextLine1 = []
    arrayCurrentText = []
    
    arrayHeader = []
    arrayCurrent = []

    arrayCurrentModbus = []
    
    dataBank = DataBank()


    
    def main(self):
        ## host modbus server
        self.server = ModbusServer(host='0.0.0.0', port=502, no_block=True, data_bank=self.dataBank)
        self.server.start()

        ## life signal
        inteager_thread = threading.Thread(target=self.sendModbusLifeSignal, daemon=True)
        inteager_thread.start()

        self.getData()
        self.Modbus()
        self.createInterface()


    
    def getData(self):
        self.getDataText()
        self.makeHeaders()
        self.makeCurrent()



    def getDataText(self):
        url = "https://meteo.gig.eu/archiwum/aktualne.txt"
        file = urllib.request.urlopen(url, timeout=5)
        self.arrayText = []

        for line in file:
            self.arrayText.append(line.decode('utf-8'))
        
        arrayLength = len(self.arrayText)
        self.arrayHeaderTextLine0 = self.arrayText[0]
        self.arrayHeaderTextLine1 = self.arrayText[1]
        self.arrayCurrentText = self.arrayText[arrayLength-1]


    
    def makeHeaders(self):
        self.arrayHeaderLine0 = self.arrayHeaderTextLine0.split()
        self.arrayHeaderLine1 = self.arrayHeaderTextLine1.split()

        for index in range(len(self.arrayHeaderLine1)):
            if index == 21: 
                self.arrayHeaderLine0[21] += ' ' + self.arrayHeaderLine0[22]
                self.arrayHeaderLine0.pop(22)
            
            if (index in [0, 1, 16, 17, 31]):
                self.arrayHeaderLine0.insert(index, '')
                self.arrayHeader.append(self.arrayHeaderLine1[index])
            else:
                self.arrayHeader.append(self.arrayHeaderLine0[index] + ' ' + self.arrayHeaderLine1[index])


    
    def makeCurrent(self):
        self.arrayCurrent = self.arrayCurrentText.split()

    



    def createInterface(self):
        self.window = tk.Tk()
        self.window.title('meteo.gig')
        self.window.resizable(False, False)
        self.window.geometry("+20+20")

        self.createInterfaceHeader()
        self.populateInterface()
        
        self.window.mainloop()
    


    def createInterfaceHeader(self):
        headerFrame = tk.Frame(self.window)
        tk.Button(headerFrame, text="REFRESH").pack(side='left', padx=15)
        tk.Button(headerFrame, text="JSON", command=self.exportJSON).pack(side='left', padx=15)
        headerFrame.pack(padx=40, pady=15)
    


    def populateInterface(self):
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





    def Modbus(self):
        self.prepareModbus()
        self.sendModbus()



    def prepareModbus(self):
        arrayCurrentModbusTemp = self.arrayCurrent
        
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
    


    def sendModbus(self):
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

    


    def sendModbusLifeSignal(self):
        integer = 0
        while True:
            self.dataBank.set_input_registers(address=6, word_list=[integer])
            integer += 1
            if integer == 10: integer=0
            time.sleep(1)

    



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





if __name__ == '__main__':
    meteo = Meteo()
    meteo.main()





## TO DO
## - zapętlić 
## - pozabezpieczać 

## PYTANIA
## - wystarczą w formie intów czy robić na floaty? 
import tkinter as tk
import urllib.request  
import json
import os





class Meteo:
    arrayText = []
    arrayCurrentText = []
    arrayHeaderTextLine0 = []
    arrayHeaderTextLine1 = []
    
    arrayCurrent = []
    arrayHeader = []


    
    def main(self):
        self.getData()
        # self.printElements()
        
        self.createInterface()


    
    def getData(self):
        self.getDataText()
        self.makeHeaders()
        self.getCurrent()



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


    
    def getCurrent(self):
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
            if (index >= len(self.arrayHeader)/2): 
                secondColumn = 3
                index -= int(len(self.arrayHeader)/2)
            tk.Label(dataFrame, text=(self.arrayHeader[index])).grid(row=index+1, column=(0+secondColumn), sticky='E', padx=5)
            tk.Label(dataFrame, text=(self.arrayCurrent[index])).grid(row=index+1, column=(1+secondColumn), sticky='W', padx=5)
            tk.Label(dataFrame, text=('|')).grid(row=index+1, column=(2), padx=15)
        dataFrame.pack(padx=40, pady=15)

    



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
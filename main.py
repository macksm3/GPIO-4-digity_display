# as of Friday evening

import tkinter as tk
import RPi.GPIO as GPIO
import time
import threading

# setup pins on GPIO
SDI   = 24
RCLK  = 23
SRCLK = 18

PAUSE = .0001    # for timer.sleep

placePin = (10, 22, 27, 17)    # this drives the digit enable control pins
number = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90)    # values that drive the LED segments for 4-digit display
# segCode = [0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f,0x77,0x7c,0x39,0x5e,0x79,0x71]
display_character = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]  # troubleshooting aid from different project

counter = 0
# timer1 = 0


class DisplayOn:
    ''' Object for the GPIO controls '''
    def __init__(self):
        self.numberToDisplay = 8888
        self.running = False
        self.timer1 = 0


    def timer(self):  # from sample code
        global counter
        # global timer1
        self.timer1 = threading.Timer(1.0, self.timer) 
        self.timer1.start()  
        counter += 1
        # print("%d" % counter)


    def setup(self):  # from sample code
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SDI, GPIO.OUT)
        GPIO.setup(RCLK, GPIO.OUT)
        GPIO.setup(SRCLK, GPIO.OUT)
        for i in placePin:
            GPIO.setup(i, GPIO.OUT)
        # global timer1
        self.timer1 = threading.Timer(1.0, self.timer)  
        self.timer1.start()
        print("run setup")

       
    def clearDisplay(self):  # from sample code
        for i in range(8):
            GPIO.output(SDI, 1)
            GPIO.output(SRCLK, GPIO.HIGH)
            GPIO.output(SRCLK, GPIO.LOW)
        GPIO.output(RCLK, GPIO.HIGH)
        GPIO.output(RCLK, GPIO.LOW)    
        for i in placePin:
            GPIO.output(i,GPIO.LOW)


    def hc595_shift(self, data):   # from sample code
        for i in range(8):
            GPIO.output(SDI, 0x80 & (data << i))
            GPIO.output(SRCLK, GPIO.HIGH)
            GPIO.output(SRCLK, GPIO.LOW)
        GPIO.output(RCLK, GPIO.HIGH)
        GPIO.output(RCLK, GPIO.LOW)


    def pickDigit(self, digit):  # from sample code
        for i in placePin:
            GPIO.output(i,GPIO.LOW)
        GPIO.output(placePin[digit], GPIO.HIGH)

    def setRun(self, newSetting):    # loop control variable on/off setting
        self.running = newSetting
        return self.running


    def loop(self):  # from sample code
        self.running = True
        global counter
    #    global gui
        print("Starting loop")
        while self.running:
            self.clearDisplay() 
            self.pickDigit(0)  
            self.hc595_shift(number[counter % 10])
            time.sleep(PAUSE)
            
            self.clearDisplay()
            self.pickDigit(1)
            self.hc595_shift(number[counter % 100//10])
            time.sleep(PAUSE)

            self.clearDisplay()
            self.pickDigit(2)
            self.hc595_shift(number[counter % 1000//100])
            time.sleep(PAUSE)

            self.clearDisplay()
            self.pickDigit(3)
            self.hc595_shift(number[counter % 10000//1000])           
            time.sleep(PAUSE)
        else:
            self.clearDisplay()
#        print("timer pause???")
        
# methods to set each digit by itself for testing
    def setDigit0(self, onesValue):
        self.clearDisplay() 
        self.pickDigit(0)  
        self.hc595_shift(number[onesValue])
        
    def setDigit1(self, tensValue):
        self.clearDisplay() 
        self.pickDigit(1)  
        self.hc595_shift(number[tensValue])
        
    def setDigit2(self, hundredsValue):
        self.clearDisplay() 
        self.pickDigit(2)  
        self.hc595_shift(number[hundredsValue])
        
    def setDigit3(self, thousandsValue):
        self.clearDisplay() 
        self.pickDigit(3)  
        self.hc595_shift(number[thousandsValue])
        

# end of object definition start of main code, functions to get buttons to call methods within GPIO object. 
def setOnes():
    myDisplay.setDigit0(ones.get())   # value from radio button

def setTens():
    myDisplay.setDigit1(tens.get())   # value from radio button

def setHundreds():
    myDisplay.setDigit2(hundreds.get())   # value from radio button

def setThousands():
    myDisplay.setDigit3(thousands.get())   # value from radio button

def startLoop():
    # myDisplay.loop()
    try:
        myDisplay.loop()
    # When 'Ctrl+C' is pressed, the program
    # destroy() will be  executed.
    except KeyboardInterrupt:
        cleanup()
    
def initDisplay():
    myDisplay.setup()
    

def submit():
    global counter
    counter = int(d.get())
    print(counter)


def cleanup():
    myDisplay.setRun(False)
    # global timer1
    GPIO.cleanup
    myDisplay.timer1.cancel()  # cancel the timer
    print("Stop loop")
    
'''
class AppWindow(tk.Frame):
    def __init__(self, parent, *args, **kwarsg):
        tk.Frame.__init__(self, parent, *args, **kwarsg)
        self.parent = parent
        
        # self.run = tk.BooleanVar()
'''
myDisplay = DisplayOn()    # instantiate object

# GUI code starts here
window = tk.Tk()
window.title("Raspberry Pi GPIO")
window.geometry("800x450")
window.config(bg='cyan')

myLabel = tk.Label(window, text="Raspberry Pi GPIO controls test")
myLabel.grid(row=0, column=0, columnspan=4)

setup_button = tk.Button(window, text="Setup", command=initDisplay)
setup_button.grid(row=1, column=0, pady=10)
cleanup_button = tk.Button(window, text="Cleanup", command=cleanup)
cleanup_button.grid(row=1, column=1)

# tring to isolate buttons that launch loop from window to see if that resolves the lockout, it does not. 
isoFrame = tk.Frame(window)
isoFrame.grid(row=1, column=2, rowspan=2)

run = tk.BooleanVar()
run_button = tk.Checkbutton(isoFrame, text="Run", onvalue=True,
                            offvalue=False, variable=run,
                            command=startLoop,
                            )
run_button.pack()
# run_button.grid(row=1, column=2)

d = tk.Entry(window, width=10, )    # for inputing number to display
d.grid(row=2, column=0)
submit_button = tk.Button(window, text="Submit", command=submit)
submit_button.grid(row=2, column=1, pady=10)

start_button = tk.Button(isoFrame, text="Start", command=startLoop)
start_button.pack()
# start_button.grid(row=2, column=2)
stop_button = tk.Button(window, text="Stop", command=cleanup)
stop_button.grid(row=2, column=3, padx=10)

# radio buttons to drive individual digit activation
ones = tk.IntVar()
tens = tk.IntVar()
hundreds = tk.IntVar()
thousands = tk.IntVar()

for index in range(10):
    radiobutton0 = tk.Radiobutton(window,
                              text=index,
                              variable=ones,
                              value=display_character[index],
                              command=setOnes)
    radiobutton0.grid(row=index+4, column=3)

for index in range(10):
    radiobutton1 = tk.Radiobutton(window,
                              text=index,
                              variable=tens,
                              value=display_character[index],
                              command=setTens)
    radiobutton1.grid(row=index+4, column=2)

for index in range(10):
    radiobutton2 = tk.Radiobutton(window,
                              text=index,
                              variable=hundreds,
                              value=display_character[index],
                              command=setHundreds)
    radiobutton2.grid(row=index+4, column=1)

for index in range(10):
    radiobutton3 = tk.Radiobutton(window,
                              text=index,
                              variable=thousands,
                              value=display_character[index],
                              command=setThousands)
    radiobutton3.grid(row=index+4, column=0)



window.mainloop()


'''
def main():
    pass

    try:
        loop()
    # When 'Ctrl+C' is pressed, the program
    # destroy() will be  executed.
    except KeyboardInterrupt:
        cleanup()
   
    
# If run this script directly, do:
if __name__ == '__main__':
    setup()
    # main()
    window = tk.Tk()
    AppWindow(window).grid(row=0, column=0)
    window.mainloop()

''' 


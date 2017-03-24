from tkinter import *
from tkinter import filedialog, messagebox

import functools
import numpy as np
import matplotlib.pyplot as plt

canvas_width = 500
canvas_height = 500

elementsInX = 10
elementsInY = 20



dX = int(canvas_width / elementsInX)
dY = int(canvas_height / elementsInY)

XSecArray = np.zeros(shape=[elementsInY-2,elementsInX-2])

def checkered(canvas, line_distanceX, line_distanceY):
   # Cleaning up the whole space
   w.create_rectangle(0, 0, canvas_width, canvas_height, fill="white", outline="gray")
   # vertical lines at an interval of "line_distance" pixel
   for x in range(line_distanceX,canvas_width,line_distanceX):
      canvas.create_line(x, line_distanceY, x, canvas_height-line_distanceY, fill="gray")
   # horizontal lines at an interval of "line_distance" pixel
   for y in range(line_distanceY,canvas_height,line_distanceY):
      canvas.create_line(line_distanceX, y, canvas_width-line_distanceX, y, fill="gray")



def showXsecArray(event):
    print(XSecArray)


def displayArrayAsImage():
    print(XSecArray)
    printTheArray(XSecArray)

    # plt.style.use('bmh')
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # im = ax.imshow(XSecArray, cmap='jet', aspect="auto", interpolation='None')
    # plt.show()

def clearArrayAndDisplay():
    if np.sum(XSecArray) != 0: # Test if there is anything draw on the array
        q = messagebox.askquestion("Delete", "This will delete current shape. Are You Sure?", icon='warning')
        if q == 'yes':
            XSecArray[:] = 0
            checkered(w, dX, dY)
    else:
            XSecArray[:] = 0
            checkered(w, dX, dY)


def saveArrayToFile():
    filename = filedialog.asksaveasfilename()
    if filename:
        saveTheData(filename)

def loadArrayFromFile():
    if np.sum(XSecArray) != 0: # Test if there is anything draw on the array
        q = messagebox.askquestion("Delete", "This will delete current shape. Are You Sure?", icon='warning')
        if q == 'yes':
            filename = filedialog.askopenfilename()
            if filename:
                loadTheData(filename)
    else:
        filename = filedialog.askopenfilename()
        if filename:
            loadTheData(filename)




def saveTheData(filename):
    print('Saving to file :' + filename)
    np.save(filename, XSecArray)

def loadTheData(filename):
    global XSecArray
    print('Readinf from file :' + filename)
    XSecArray =  np.load(filename)
    printTheArray(XSecArray)




def setUpPoint( event, Set ):

    Col = int(event.x/dX)
    Row = int(event.y/dY)

    if event.x < canvas_width-dX and event.y < canvas_height-dY and event.x > dX and event.y > dY:
        inCanvas = True
    else:
        inCanvas = False


    if Set and inCanvas:
        w.create_rectangle(Col*dX, Row*dY, Col*dX+dX, Row*dY+dY, fill="orange", outline="gray")
        XSecArray[Row-1][Col-1] = 1

    elif not(Set) and inCanvas:
        w.create_rectangle(Col*dX, Row*dY, Col*dX+dX, Row*dY+dY, fill="white", outline="gray")
        XSecArray[Row-1][Col-1] = 0

def printTheArray(dataArray):
    global dX, dY
    # Let's check the size
    elementsInY = dataArray.shape[0]
    elementsInX = dataArray.shape[1]

    # Now we calculate the propper dX and dY for this array
    dX = int(canvas_width / (elementsInX+2))
    dY = int(canvas_height / (elementsInY+2))

    # Now we cleanUp the field
    checkered(w, dX, dY)

    for Row in range(elementsInY):
        for Col in range(elementsInX):
            if dataArray[Row][Col] == 1:
                fillColor = "orange"
            else:
                fillColor = "white"

            w.create_rectangle((Col+1)*dX, (Row+1)*dY, (Col+1)*dX+dX, (Row+1)*dY+dY, fill=fillColor, outline="gray")

master = Tk()
master.title( "Cross Section Designer" )

w = Canvas(master,
           width=canvas_width,
           height=canvas_height)
w.configure(background='white')
w.pack(expand = YES, fill = BOTH, side= TOP)

print_button = Button(master, text='Display View', command=displayArrayAsImage)
print_button.pack(side = LEFT)

print_button_save = Button(master, text='Save to File', command=saveArrayToFile)
print_button_save.pack()

print_button_load = Button(master, text='Load from File', command=loadArrayFromFile)
print_button_load.pack()

print_button_clear = Button(master, text='Clear All', command=clearArrayAndDisplay)
print_button_clear.pack()


w.bind( "<Button 1>", functools.partial(setUpPoint, Set=True))
w.bind( "<Button 3>", functools.partial(setUpPoint, Set=False))
w.bind( "<B1-Motion>", functools.partial(setUpPoint, Set=True))
w.bind( "<B3-Motion>", functools.partial(setUpPoint, Set=False))

w.bind( "<Button 2>", showXsecArray)


message = Label( master, text = "use: Left Mouse Button to Set conductor, Right to reset" )
message.pack( side = BOTTOM )
master.resizable(width=False, height=False)

checkered(w, dX, dY)



mainloop()

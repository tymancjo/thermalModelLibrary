from tkinter import *
from tkinter import filedialog, messagebox

import functools
import numpy as np
import matplotlib.pyplot as plt

canvas_width = 500
canvas_height = 500

elementsInX = 10
elementsInY = 10



dX = int(canvas_width / elementsInX)
dY = int(canvas_height / elementsInY)

XSecArray = np.zeros(shape=[elementsInY,elementsInX])

def checkered(canvas, line_distanceX, line_distanceY):
   # Cleaning up the whole space
   w.create_rectangle(0, 0, canvas_width, canvas_height, fill="white", outline="gray")
   # vertical lines at an interval of "line_distance" pixel
   for x in range(0,canvas_width,int(line_distanceX)):
      canvas.create_line(x, 0, x, canvas_height, fill="gray")
   # horizontal lines at an interval of "line_distance" pixel
   for y in range(0,canvas_height,int(line_distanceY)):
      canvas.create_line(0, y, canvas_width, y, fill="gray")

def arraySlicer(inputArray, subDivisions):
    return inputArray.repeat(subDivisions,axis=0).repeat(subDivisions,axis=1)

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
    global XSecArray, dX, dY
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

    if event.x < canvas_width and event.y < canvas_height and event.x > 0 and event.y > 0:
        inCanvas = True
    else:
        inCanvas = False


    if Set and inCanvas:
        w.create_rectangle(Col*dX, Row*dY, Col*dX+dX, Row*dY+dY, fill="orange", outline="gray")
        XSecArray[Row][Col] = 1

    elif not(Set) and inCanvas:
        w.create_rectangle(Col*dX, Row*dY, Col*dX+dX, Row*dY+dY, fill="white", outline="gray")
        XSecArray[Row][Col] = 0

def printTheArray(dataArray):
    global dX, dY
    # Let's check the size
    elementsInY = dataArray.shape[0]
    elementsInX = dataArray.shape[1]

    # Now we calculate the propper dX and dY for this array
    dX = (canvas_width / (elementsInX))
    dY = (canvas_height / (elementsInY))

    # Now we cleanUp the field
    checkered(w, dX, dY)

    for Row in range(elementsInY):
        for Col in range(elementsInX):
            if dataArray[Row][Col] == 1:
                fillColor = "orange"
            else:
                fillColor = "white"

            w.create_rectangle((Col)*dX, (Row)*dY, (Col)*dX+dX, (Row)*dY+dY, fill=fillColor, outline="gray")

def subdivideArray():
    global XSecArray
    XSecArray = arraySlicer(inputArray = XSecArray, subDivisions = 2)
    printTheArray(dataArray=XSecArray)


########


master = Tk()
master.title( "Cross Section Designer" )

img = PhotoImage(file='CSDico.gif')
master.tk.call('wm', 'iconphoto', master._w, img)

w = Canvas(master,
           width=canvas_width,
           height=canvas_height)
w.configure(background='white')
w.grid(row=0, column=1, columnspan=2, rowspan=10, sticky=W+E+N+S, padx=1, pady=1)

opis = Label(text='Cross Section\n Designer\n v0.1', height=15)
opis.grid(row=8, column=0,)

emptyOpis = Label(text='', height=3)
emptyOpis.grid(row=5, column=0,)

print_button = Button(master, text='Refresh View', command=displayArrayAsImage, height=2, width=16)
print_button.grid(row=7, column=0, padx=5, pady=5)

print_button_slice = Button(master, text='Subdivide', command=subdivideArray, height=2, width=16)
print_button_slice.grid(row=6, column=0 , padx=5, pady=5)



print_button_load = Button(master, text='Load from File', command=loadArrayFromFile, height=2, width=16)
print_button_load.grid(row=2, column=0, padx=5, pady=5)

print_button_save = Button(master, text='Save to File', command=saveArrayToFile, height=2, width=16)
print_button_save.grid(row=3, column=0, padx=5, pady=5)

print_button_clear = Button(master, text='New Geometry', command=clearArrayAndDisplay, height=2, width=16)
print_button_clear.grid(row=1, column=0, padx=5, pady=5)

w.bind( "<Button 1>", functools.partial(setUpPoint, Set=True))
w.bind( "<Button 3>", functools.partial(setUpPoint, Set=False))
w.bind( "<B1-Motion>", functools.partial(setUpPoint, Set=True))
w.bind( "<B3-Motion>", functools.partial(setUpPoint, Set=False))

w.bind( "<Button 2>", showXsecArray)


message = Label( master, text = "use: Left Mouse Button to Set conductor, Right to reset" )
#message.pack( side = BOTTOM )
message.grid(row=10, column=0, columnspan=2)

master.resizable(width=False, height=False)

checkered(w, dX, dY)



mainloop()

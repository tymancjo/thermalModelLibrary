from tkinter import *
import functools
import numpy as np
import matplotlib.pyplot as plt

canvas_width = 500
canvas_height = 500

elementsInX = 20
elementsInY = 20



dX = int(canvas_width / elementsInX)
dY = int(canvas_height / elementsInY)

XSecArray = np.zeros(shape=[elementsInY-2,elementsInX-2])

def checkered(canvas, line_distance):
   # Cleaning up the whole space
   w.create_rectangle(0, 0, canvas_width, canvas_height, fill="white", outline="gray")
   # vertical lines at an interval of "line_distance" pixel
   for x in range(line_distance,canvas_width,line_distance):
      canvas.create_line(x, line_distance, x, canvas_height-line_distance, fill="gray")
   # horizontal lines at an interval of "line_distance" pixel
   for y in range(line_distance,canvas_height,line_distance):
      canvas.create_line(line_distance, y, canvas_width-line_distance, y, fill="gray")

def oczymsTam():
    return 'o niczym'

def showXsecArray(event):
    print(XSecArray)


def displayArrayAsImage():
    print(XSecArray)
    plt.style.use('bmh')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(XSecArray, cmap='jet', aspect="auto", interpolation='None')
    plt.show()

def clearArrayAndDisplay():
    XSecArray[:] = 0
    checkered(w, dX)

def saveArrayToFile():

    def saveTheData():
        numpyArray = np.array(XSecArray)
        fileName = str(E1.get())+"_xsecArray"
        print('Saving to file :' + fileName)
        np.save('xsecData/'+fileName, numpyArray)

    toplevel = Toplevel()
    L1 = Label(toplevel, text="File Name")
    L1.pack()
    E1 = Entry(toplevel, bd =1)
    E1.pack()
    B1 = Button(toplevel, text='Save the data', command=saveTheData)
    B1.pack()






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


master = Tk()
master.title( "Cross Section Designer" )

w = Canvas(master,
           width=canvas_width,
           height=canvas_height)
w.configure(background='white')
w.pack(expand = YES, fill = BOTH, side= TOP)

print_button = Button(master, text='Display View', command=displayArrayAsImage)
print_button.pack(side = LEFT)

print_button_clear = Button(master, text='Save to File', command=saveArrayToFile)
print_button_clear.pack()

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

checkered(w, dX)



mainloop()

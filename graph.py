from tkinter import *
import functools
import numpy as np

canvas_width = 500
canvas_height = 500

elementsInX = 20
elementsInY = 20



dX = int(canvas_width / elementsInX)
dY = int(canvas_height / elementsInY)

XSecArray = np.zeros(shape=[elementsInY-2,elementsInX-2])

def checkered(canvas, line_distance):
   # vertical lines at an interval of "line_distance" pixel
   for x in range(line_distance,canvas_width,line_distance):
      canvas.create_line(x, line_distance, x, canvas_height-line_distance, fill="gray")
   # horizontal lines at an interval of "line_distance" pixel
   for y in range(line_distance,canvas_height,line_distance):
      canvas.create_line(line_distance, y, canvas_width-line_distance, y, fill="gray")

def showXsecArray(event):
    print(XSecArray)

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
master.title( "Painting using Ovals" )

w = Canvas(master, 
           width=canvas_width, 
           height=canvas_height)
w.configure(background='white')
w.pack(expand = YES, fill = BOTH)

w.bind( "<Button 1>", functools.partial(setUpPoint, Set=True))
w.bind( "<Button 3>", functools.partial(setUpPoint, Set=False))
w.bind( "<B1-Motion>", functools.partial(setUpPoint, Set=True))
w.bind( "<B3-Motion>", functools.partial(setUpPoint, Set=False))

w.bind( "<Button 2>", showXsecArray)


message = Label( master, text = "Press and Drag the mouse to draw" )
message.pack( side = BOTTOM )
master.resizable(width=False, height=False)    

checkered(w, dX)

mainloop()
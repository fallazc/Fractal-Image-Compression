from Decoder import *
from FractalEncoder import *
from tkinter import *
from PIL import ImageTk, Image
import time
import sys

nSteps = 10
canvas = None
img = None
compressedImagePath=""

if len(sys.argv) < 2:
        print("Path to compressed image is not specified")
        quit(-1)
else:
        compressedImagePath = sys.argv[1];

def showDecoding():
        global canvas
        global img
        
        decoder = FractalDecoder(compressedImagePath, 5)
        
        print("Decoding the image...\n")
        
        for i  in range (nSteps):
                canvas.delete("all")
                img  = ImageTk.PhotoImage(decoder.decodeImage(0))
                canvas.create_image(0, 0, image = img, anchor = "nw")
                canvas.update()
                time.sleep(1)

        print("Done")

if __name__ == "__main__":
        root = Tk()
        root.geometry('800x640')
        canvas = Canvas(root, width = 640, height = 640)
        canvas.pack()
        root.after(100, showDecoding)
        
        root.mainloop()

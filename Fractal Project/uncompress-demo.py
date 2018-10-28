from FractalDecoder import *
from tkinter import *
from PIL import ImageTk, Image
import time
import sys

nSteps = 10
canvas = None
img = None
saveOutput = True;
compressedImagePath=""
decompressionScale = 0
nArguments = len(sys.argv);

if nArguments < 2:
        print("Path to compressed image is not specified")
        quit(-1)
else:
        compressedImagePath = sys.argv[1];
        saveOutput = (nArguments > 3)
if nArguments < 2:
        print("Path to compressed image is not specified")
        quit(-1)
else:
        decompressionScale = int(sys.argv[2]);
        saveOutput = (nArguments > 3)
        
def showDecoding():
        global canvas
        global img
        
        decoder = FractalDecoder(compressedImagePath, decompressionScale)
        
        print("Decoding the image...\n")
        
        for i  in range (nSteps):
                canvas.delete("all")
                img  = ImageTk.PhotoImage(decoder.nextStep())
                canvas.create_image(0, 0, image = img, anchor = "nw")
                canvas.update()
                time.sleep(1)

        if (saveOutput):
                decoder.saveResult();
                
        print("Done")

if __name__ == "__main__":
        root = Tk()
        frameWidth = decompressionScale * 160
        frameHeight = decompressionScale * 128
        root.geometry('{0}x{1}'.format(frameWidth, frameHeight))
        canvas = Canvas(root, width = frameHeight, height = frameHeight)
        canvas.pack()
        root.after(100, showDecoding)
        
        root.mainloop()

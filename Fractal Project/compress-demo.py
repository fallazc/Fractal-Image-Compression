#Falla Coulibaly

#Simple implementation of the fractal compression.
#The algorithm used is not optimal and average error
#is quite high because of the mapping algorithm.

from FractalEncoder import *
import time
import sys

#Setup variables

imagePath=""

if len(sys.argv) < 2:
        print("Path to image to compress is not specified")
        quit(-1)
else:
        imagePath = sys.argv[1];

if __name__ == '__main__':
        #for the decoder
        nSteps = 10
        
        #Must be a power of two
        #A lower blocksize means more details
        blockSize = 8
        
        #Encoder
        encoder = FractalEncoder(blockSize)
                                 
        #Benchmark the encoding
        start = time.time()
        encoder.encodeImage(imagePath)
        print("Elapsed time : {0}\n".format(time.time() - start))

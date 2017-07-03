#Falla Coulibaly

#Simple implementation of the fractal compression.
#The algorithm used is not optimal and average error
#is quite high because of the mapping algorithm.

from FractalDecoder import *
from FractalEncoder import *
import time

if __name__ == '__main__':
        #Setup variables

        #for the decoder
        nSteps = 10
        
        #Must be a power of two
        #A lower blocksize means more details
        blockSize = 4
        
        #Must be a power of two as well
        #A scale > blcokSize will result in
        #a seamless upscaled image
        decompressionScale = 8
        
        #Encoder
        encoder = FractalEncoder(blockSize)
        #Benchmark the encoding
        start = time.time()
        encoder.encodeImage("LennaLow.bmp")
        print("Elapsed time : {0}\n".format(time.time() - start))

        #Decoder
        decoder = FractalDecoder("Lenna.fif", decompressionScale)
        ##Benchmark the decoding
        start = time.time()
        decoder.decodeImage(nSteps)
        print("Elapsed time : {0}".format(time.time() - start))

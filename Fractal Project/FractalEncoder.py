#Falla Coulibaly

import sys
import multiprocessing
import threading
from PIL import Image
          
class RangeBlock:
        def __init__(self, pixels):
                """
                Constructor for RangeBlock
                :param pixels: List of pixel brightness for a
                               region of the range image
                """
                self.pixels = pixels
                self.bestFit = None
                self.contrast = 0
                self.brightness = 0
        
        def __str__(self):
                """
                Convert this object to a string
                :return: String representation of this object
                """
                tType, dBlock = self.bestFit
                return '{0} {1} {2} {3}'.format(str(dBlock), tType, int(self.brightness), self.contrast)

class DomainBlock:
        def __init__(self, x, y, region):
                """
                Constructor for DomainBlock
                :param x: x coordinate of this block in the domain image
                :param y: y coordinate of this block in the domain image
                :param region: Represents a sub-region of the downscaled image to use
                               to initialize the transformations
                """
                self.x = x
                self.y = y
                self.transforms = [None] * 8
                self.__initTransforms(region)

        def __initTransforms(self, region):
                """
                Compute the 8 different transformations of the
                domain block
                :param region: Represents a sub-region of the downscaled image to use
                               to initialize the transformations
                """
                #Initial image
                self.transforms[0] = region.tobytes()
                #90 degree rotation
                self.transforms[1] = region.transpose(Image.ROTATE_90).tobytes()
                #180 degree rotation
                self.transforms[2] = region.transpose(Image.ROTATE_180).tobytes()
                #270 degree rotation
                self.transforms[3] = region.transpose(Image.ROTATE_270).tobytes()
                
                #Reflection (left --> right)
                tmp = region.transpose(Image.FLIP_LEFT_RIGHT)
                self.transforms[4] = tmp.tobytes()
                #90 degree rotation of the reflected image
                self.transforms[5] = tmp.transpose(Image.ROTATE_90).tobytes()
                #180 degree rotation of the reflected image
                self.transforms[6] = tmp.transpose(Image.ROTATE_180).tobytes()
                #270 degree rotation of the reflected image
                self.transforms[7] = tmp.transpose(Image.ROTATE_270).tobytes()

        def __str__(self):
                """
                Convert this object to a string
                :return: String representation of this object
                """
                return '{0} {1}'.format(self.x, self.y)

        
class EncoderThread(threading.Thread):
        def __init__(self, n_Pow2, rBlocks, dBlocks, begin, end):
                """
                Constructor for EncoderThread
                
                :param n_Pow2:
                :param rBlocks:
                :param dBlocks:
                :param begin:
                :param end:
                """
                threading.Thread.__init__(self)
                self.__rBlocks = rBlocks
                self.__dBlocks = dBlocks
                self.__begin = begin
                self.__end = end
                self.__N_POW2 = n_Pow2

        def run(self):
                """
                Starting point for the thread
                """
                self.mapRangeToDomain()
        """
        Compute the contrast(scale factor) between the
        range block and the domain image

        :param rPixels: List of pixel brightness for a
                                region of the range image
        :param dPixels: List of pixel brightness for a
                        region of the domain image
        :return: Returns the scale factor
        """
        def computeContrast(self, rPixels, dPixels):
                size = len(rPixels)
                
                contrast = self.__N_POW2 * sum(dPixels[k] * rPixels[k] for k in range(size))
                
                temp = -sum(dPixels)
                temp *= sum(rPixels)

                contrast += temp

                temp = self.__N_POW2 * sum(pixel ** 2 for pixel in dPixels)
                temp -= sum(dPixels) ** 2

                if temp != 0:
                        return contrast / temp
                
                return 0

        
        def computeBrightness(self, contrast, rPixels, dPixels):
                """
                Compute the brightness offset between the
                specified blocks
                    
                :param contrast: The scale factor between domain block and
                                 range block
                :param rPixels: List of pixel brightness for a
                                region of the range image
                :param dPixels: List of pixel brightness for a
                                region of the domain image
                """
                return (sum(rPixels) - (contrast * sum(dPixels))) // self.__N_POW2
        
        def computeRMS(self, contrast, brightness, rPixels, dPixels):
                """
                Compute the root mean square difference

                :param contrast: The scale factor between domain block and
                                 range block
                :param brightness: The brightness offset between domain block
                                   and range block
                :param rPixels: List of pixel brightness for a
                                region of the range image
                :param dPixels: List of pixel brightness for a
                                region of the domain image
                :return: Returns root mean square difference
                """
                rms = 0
                for i in range (len(rPixels)):
                        rms += ((contrast * dPixels[i]) + brightness - rPixels[i]) ** 2
                
                return rms
        
        def mapRangeToDomain(self):
                """
                Match each range block to a domain block based on the lowest
                root mean quare difference.
                """
                for b in range(self.__begin, self.__end):
                        rBlock = self.__rBlocks[b]
                        minRMS = sys.float_info.max
                        for dBlock in self.__dBlocks:
                                for tType in range(len(dBlock.transforms)):
                                        #Compare current transformation of the domain block
                                        #to each range block to find the best match
                                        contrast = self.computeContrast(rBlock.pixels, dBlock.transforms[tType])
                                        #An optimal contrast will be less than 1 or 1.2
                                        #because it ensures a low value for rms
                                        if contrast < 1.2:
                                                brightness = self.computeBrightness(contrast, rBlock.pixels, dBlock.transforms[tType])
                                                #Compute the root mean square difference
                                                rms = self.computeRMS(contrast, brightness, rBlock.pixels, dBlock.transforms[tType])
                                                if minRMS > rms:
                                                        minRMS = rms
                                                        rBlock.contrast = contrast
                                                        rBlock.brightness = brightness
                                                        rBlock.bestFit = (tType, dBlock)



class FractalEncoder:
        def __init__(self, BLOCK_SIZE):
                """
                Constructor for FractalEncoder

                :param BLOCK_SIZE: size of the range block
                """
                self.__width = 0
                self.__height =  0
                self.__rBlocks = []
                self.__dBlocks = []
                self.__threads = []
                self.__BLOCK_SIZE = BLOCK_SIZE

        def __setupEncoder(self, filename):
                """
                Takes care of initializing the instance variables

                :param filename: The name of the file to compress
                """
                #Original image will be used to create the range
                image = Image.open(filename)
                #Downscaled image will be used to create the domain
                downImage = image.resize((image.width//2, image.height//2))

                #Partition the original and downscaled images into
                #squares of equal sizes
                rBoxes = self.__createBoxes(image.width, image.height)
                dBoxes = self.__createBoxes(downImage.width, downImage.height)

                #
                self.__width = image.width
                self.__height = image.height
                #Create range blocks from the partitioned image
                self.__rBlocks = [RangeBlock(image.crop(box).tobytes()) for box in rBoxes]
                #Create the codeBooks(domain block + its 8 transformations)
                #from the partitioned downscaled image
                self.__dBlocks = [DomainBlock(box[0], box[1], downImage.crop(box)) for box in dBoxes]
                print('{0} {1}'.format(len(rBoxes), len(dBoxes)))
                #
                #mapRangeToDomain(rBlocks, dBlocks)
                size = len(self.__rBlocks)
                nCores = multiprocessing.cpu_count()
                stepSize = size // nCores
                n_Pow2 = self.__BLOCK_SIZE ** 2
                
                for i in range(nCores - 1):
                        begin = i * stepSize
                        end = begin + stepSize
                        self.__threads.append(EncoderThread(n_Pow2, self.__rBlocks, self.__dBlocks, begin, end))
                if nCores > 1:
                        #Let the last core deal with the last set of data
                        #this takes care of rounding off error for the stepSize
                        self.__threads.append(EncoderThread(n_Pow2, self.__rBlocks, self.__dBlocks, size - stepSize, size))
                
                #Free resources
                image.close()
                downImage.close()

        
        def __createBoxes(self, width, height):
                """
                Partition the image in square boxes 
                based on "BLOCK_SIZE"

                :param width = Width of the image to partition
                :param height = Height of the image to partition
                :return: returns A list of boxes that represent
                     regions of an image
                """
                i = 0
                boxes = []
                
                while (i < height):
                        j = 0
                        while (j < width):
                                boxes.append((j, i, j + self.__BLOCK_SIZE, i + self.__BLOCK_SIZE))
                                j += self.__BLOCK_SIZE
                        i += self.__BLOCK_SIZE
                return boxes



        def __writeToFIle(self, filename):
                """
                Export the compressed data to a file

                :param filename: The name of the file to create
                """
                try:
                        f = open(filename, 'w')
                        #Write the size of the original image
                        f.write('{0} {1}\n'.format(self.__width, self.__height))
                        #Write the range and domain sizes
                        f.write('{0} {1}\n'.format(self.__BLOCK_SIZE, self.__BLOCK_SIZE * 2))
                        #Write the range blocks' transformtions
                        for rBlock in self.__rBlocks:
                                if rBlock.bestFit is None:
                                        continue
                                f.write('{0}\n'.format(str(rBlock)))
                        f.close()
                except IOError:
                        print('Failed to write to the file')
                        f.close()
                        exit()
                 
        def encodeImage(self, filename):
                """
                Compress the image using the fractal
                compression algorithm

                :param filename: The name of the file to compress
                :returns: return the compressed image
                """
                
                #Initialize the encoder's variables
                self.__setupEncoder(filename)
                
                #Start all the threads to compress the range blocks
                for thread in self.__threads:
                        thread.start()

                #Synchronize the threads
                for thread in self.__threads:
                        thread.join()

                #Write the transformation data the file
                self.__writeToFIle('Lenna.fif')

import sys
import os
from PIL import Image

BLOCK_SIZE = 8
N_POW2 = BLOCK_SIZE ** 2

class CompressedImage:
        """
        DOCUMENT ME!!!
        """
        def __init__(self, filename):
                self.width = 0
                self.height = 0
                self.rSize = 0
                self.dSize = 0
                self.rBlocksInfo = []
                self.__readFromFile(filename)

        def __readFromFile(self, filename):
                """
                DOCUMENT ME!!!
                """
                try:
                        with open(filename, 'r') as f:
                                data = f.readline().split()
                                self.width = int(data[0])
                                self.height = int(data[1])
                                
                                data = f.readline().split()
                                self.rSize = int(data[0])
                                self.dSize = int(data[1])
                                
                                for line in f:
                                        data = line.split()
                                        dX = int(data[0])
                                        dY = int(data[1])
                                        tType = int(data[2])
                                        brightness = int(float(data[3]))
                                        contrast = float(data[4])
                                        
                                        self.rBlocksInfo.append((dX, dY, tType, contrast, brightness))
                except IOError:
                        print('Error occured while reading from the file')
                        exit()

class FractalDecoder:
        def __init__(self, filename):
                self.cmpImage = CompressedImage(filename)
                self.image = Image.new("L", (self.cmpImage.width, self.cmpImage.height), 128)

        def nextStep(self):
                scale = float(self.cmpImage.rSize)/self.cmpImage.dSize
                buffer = self.image.resize((int(scale * self.cmpImage.width), int(scale * self.cmpImage.height)))
                nRangeX = self.cmpImage.width // self.cmpImage.rSize

                for i in range (0, len(self.cmpImage.rBlocksInfo)):
                        x = (i % nRangeX) * self.cmpImage.rSize
                        y = int((i / nRangeX) * self.cmpImage.rSize)
                        imgRegion = self.image.crop((x, y, self.cmpImage.rSize, self.cmpImage.rSize))

                        dX, dY, tType, contrast, brightness = self.cmpImage.rBlocksInfo[i]

                        if tType == 1:
                                imgRegion = imgRegion.rotate(Image.ROTATE_90)
                        elif tType == 2:
                                imgRegion = imgRegion.rotate(Image.ROTATE_180)
                        elif tType == 3:
                                imgRegion = imgRegion.rotate(Image.ROTATE_270)
                        else:
                                tmp = imgRegion.transpose(Image.FLIP_LEFT_RIGHT)
                                if tType == 4:
                                        imgRegion = tmp
                                if tType == 5:
                                        imgRegion = tmp.rotate(Image.ROTATE_90)
                                elif tType == 6:
                                        imgRegion = imgRegion.rotate(Image.ROTATE_180)
                                elif tType == 7:
                                        imgRegion = imgRegion.rotate(Image.ROTATE_270)

                        def linearTransform(pixel):
                                return (pixel * contrast) + brightness
                        
                        imgRegion = imgRegion.point(linearTransform)
                        self.image.paste(imgRegion, (dX, dY, dX + imgRegion.width, dY + imgRegion.height))                
                
        def showResult(self):
                self.image.show()

        
                
class RangeBlock:
        '''
            Description here
            :param region =
        '''
        def __init__(self, pixels):
                self.pixels = pixels
                self.bestFit = ()
                self.contrast = 0
                self.brightness = 0
        
        def __str__(self):
                tType, dBlock = self.bestFit
                return '{0} {1} {2} {3}'.format(str(dBlock), tType, self.brightness, self.contrast)

class DomainBlock:
        '''
            Constructor for DomainBlock
            :param region = Represents a sub-region of the downscaled image to use
                            to initialize the transformations
        '''
        def __init__(self, x, y, region):
                self.x = x
                self.y = y
                self.transforms = [None] * 8
                self.__initTransforms(region)

        '''
            Compute the 8 different transformations of the
            domain block
        '''
        def __initTransforms(self, region):
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
                return '{0} {1}'.format(self.x, self.y)
	
'''
    Partition the image in square boxes 
    based on "BLOCK_SIZE"
    
    :param width = Width of the image to partition
    :param height = Height of the image to partition
    :return: returns A list of boxes that represent
             regions of an image
'''
def createBoxes(width, height):
	i = 0
	boxes = []
	
	while (i < width - BLOCK_SIZE):
		j = 0
		while (j < height - BLOCK_SIZE):
			boxes.append((i, j, i + BLOCK_SIZE, j + BLOCK_SIZE))
			j += BLOCK_SIZE
		i += BLOCK_SIZE
		
	return boxes

'''
    Compute the contrast factor between the
    specified blocks
    
    :param rPixels =
    :param dPixels = 
    :return: returns
'''
def computeContrast(rPixels, dPixels):
        size = len(rPixels)
        
        contrast = N_POW2 * sum(dPixels[k] * rPixels[k] for k in range(0, size))
        
        temp = -sum(dPixels)
        temp *= sum(rPixels)

        contrast += temp

        temp = N_POW2 * sum(pixel ** 2 for pixel in dPixels)
        temp -= sum(dPixels) ** 2

        if temp != 0:
                return contrast / temp
        
        return 0

'''
    Compute the brightness offset between the
    specified blocks
    
    :param
    :param
    :return: Returns brightness offset
'''
def computeBrightness(contrast, rPixels, dPixels):
        return (sum(rPixels) - (contrast * sum(dPixels))) // N_POW2

"""
    Compute the root mean square difference
    
    :param 
    :return: Returns root mean square difference
"""
def computeRMS(contrast, brightness, rPixels, dPixels):
        rms = 0
        for i in range (0, len(rPixels)):
                rms += ((contrast * dPixels[i]) + brightness - rPixels[i]) ** 2
        
        return rms

'''
    Match each range block to a domain block based on the lowest
    root mean quare difference.
    
    :param domainBlocks = The blocks in the domain
    :param rangeBlocks = The blocks in the range
'''
def mapRangeToDomain(rBlocks, dBlocks):
        mapped = False
        i = 1
        for rBlock in rBlocks:
                print('Mapping range block #{0}\n'.format(i))
                mapped - False
                minRMS = sys.float_info.max
                for dBlock in dBlocks:
                        for tType in range(0, len(dBlock.transforms)):
                                #Compare current transformation of the domain block
                                #to each range block to find the best match
                                contrast = computeContrast(rBlock.pixels, dBlock.transforms[tType])
                                #An optimal contrast will be less than 1 or 1.2
                                #because it ensures a low value for rms
                                if contrast < 1:
                                        brightness = computeBrightness(contrast, rBlock.pixels, dBlock.transforms[tType])
                                        #Compute the root mean square difference
                                        rms = computeRMS(contrast, brightness, rBlock.pixels, dBlock.transforms[tType])
                                        if minRMS > rms:
                                                minRMS = rms
                                                rBlock.contrast = contrast
                                                rBlock.brightness = brightness
                                                rBlock.bestFit = (tType, dBlock)
                                                mapped = True
                print('Done mapping range block #{0}\n'.format(i))
                i += 1
        return mapped

def writeToFIle(filename, width, height, rBlocks):
        """
        DOCUMENT ME!!!
        """
        try:
                f = open(filename, 'w')
                #
                f.write('{0} {1}\n'.format(width, height))
                #
                f.write('{0} {1}\n'.format(BLOCK_SIZE, BLOCK_SIZE * 2))
                #
                for rBlock in rBlocks:
                        f.write('{0}\n'.format(str(rBlock)))
                f.close()
        except IOError:
                print('Failed to write to the file')
                f.close()
                exit()
        

def encode(filename):
        """
        Compress the image using the fractal
        compression algorithm

        :param filename: The name of the file to compress
        :returns: return the compressed image
        """

        #Original image will be used to create the range
        image = Image.open(filename)
        #Downscaled image will be used to create the domain
        downImage = image.resize((image.width//2, image.height//2))

        #Partition the original and downscaled images into
        #squares of equal sizes
        rBoxes = createBoxes(image.width, image.height)
        dBoxes = createBoxes(downImage.width, downImage.height)

        #Create range blocks from the partitioned image
        rBlocks = [RangeBlock(image.crop(box).tobytes()) for box in rBoxes]
        #Create the codeBooks(domain block + its 8 transformations)
        #from the partitioned downscaled image
        dBlocks = [DomainBlock(box[0], box[1], downImage.crop(box)) for box in dBoxes]
        print('{0} {1}'.format(len(rBoxes), len(dBoxes)))
        #
        mapRangeToDomain(rBlocks, dBlocks)

        #
        writeToFIle('Lenna.f', image.width, image.height, rBlocks)

        #Free resources
        image.close()
        downImage.close()

def decode(filename):
        """
        DOCUMENT ME!!!
        """
        decoder = FractalDecoder(filename)
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        decoder.nextStep()
        
        decoder.showResult()
        input("")

###########################################################################
if __name__ == '__main__':
	#encode("Lenna.jpg")
        decode("Lenna.f")

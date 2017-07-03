#Falla Coulibaly

from PIL import Image

class CompressedImage:
        def __init__(self, filename, scale):
                """
                Constructor for the CompressedImage
                :param filename: name of the file to decode
                :param scale: Scale at which the file should
                              decompressed
                """
                self.width = 0
                self.height = 0
                self.rSize = 0
                self.dSize = 0
                self.rBlocksInfo = []
                self.__readFromFile(filename, scale)

        def __readFromFile(self, filename, scale):
                """
                Initializes class instance's variables from
                the data stored in the FIF file
                :param filename: name of the file to decode
                :param scale: Scale at which the file should
                              decompressed
                """
                try:
                        with open(filename, 'r') as f:
                                data = f.readline().split()
                                self.width = int(data[0]) * scale
                                self.height = int(data[1]) * scale
                                
                                data = f.readline().split()
                                self.rSize = int(data[0]) * scale
                                self.dSize = int(data[1]) * scale
                                
                                for line in f:
                                        data = line.split()
                                        dX = int(data[0]) * scale
                                        dY = int(data[1]) * scale
                                        tType = int(data[2])
                                        brightness = int(float(data[3]))
                                        contrast = float(data[4])
                                        
                                        self.rBlocksInfo.append((dX, dY, tType, contrast, brightness))
                except IOError:
                        print('Error occured while reading from the file')
                        exit()


class FractalDecoder:
        def __init__(self, filename, decompressionScale):
                """
                Constructor for the `FIF` format decoder
                :param filename: name of the file to decode
                :param decompressionScale: Scale at which the file should
                                           decompressed
                """
                self.cmpImage = CompressedImage(filename, decompressionScale)
                self.rImage = Image.new("L", (self.cmpImage.width, self.cmpImage.height), 128)
                
        def __showResult(self):
                """
                Dispaly the result of the decompression after the
                specified number of steps
                """
                self.rImage.show()
                
        def __nextStep(self):
                """
                Apply the stored transformations to the each range block
                from the previous transformation of the Image
                """
                scale = float(self.cmpImage.rSize)/self.cmpImage.dSize
                dImage = self.rImage.resize((int(scale * self.cmpImage.width), int(scale * self.cmpImage.height)))
                nRangeX = self.cmpImage.width // self.cmpImage.rSize

                for i in range (0, len(self.cmpImage.rBlocksInfo)):
                        x = (i % nRangeX) * self.cmpImage.rSize
                        y = int((i / nRangeX) * self.cmpImage.rSize)
                        
                        dX, dY, tType, contrast, brightness = self.cmpImage.rBlocksInfo[i]
                        rangeChunk = dImage.crop((dX, dY, dX + self.cmpImage.rSize, dY + self.cmpImage.rSize))

                        if tType == 0:
                                pass
                        elif tType == 1:
                                rangeChunk = rangeChunk.transpose(Image.ROTATE_90)
                        elif tType == 2:
                                rangeChunk = rangeChunk.transpose(Image.ROTATE_180)
                        elif tType == 3:
                                rangeChunk = rangeChunk.transpose(Image.ROTATE_270)
                        else:
                                rangeChunk = rangeChunk.transpose(Image.FLIP_LEFT_RIGHT)
                                if tType == 4:
                                        pass
                                elif tType == 5:
                                        rangeChunk = rangeChunk.transpose(Image.ROTATE_90)
                                elif tType == 6:
                                        rangeChunk = rangeChunk.transpose(Image.ROTATE_180)
                                elif tType == 7:
                                        rangeChunk = rangeChunk.transpose(Image.ROTATE_270)

                        def linearTransform(pixel):
                                return (pixel * contrast) + brightness
    
                        rangeChunk = rangeChunk.point(linearTransform)
                        self.rImage.paste(rangeChunk, (x, y))

        def decodeImage(self, nSteps):
                """
                Decode the image by repeatedly applying
                the transformations read

                :param nSteps: Number of iterations of the
                               transformations
                """
                for i in range(nSteps):
                        self.__nextStep()
                #Display result of the decoding
                self.__showResult()

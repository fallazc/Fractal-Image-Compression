# Fractal-Image-Compression
This is a program that allows compression(lossy) and decompression of an image at any scale using the concept of fractals.
**Note:** Right now the algorithm works only on power of two grayscale ".bmp" images.

## Demo
![demo](images/demo.gif)

### Compression usage
```
python compress-demo.py filename
```
**filename** - image file to compress

### Uncompression usage
```bat
python uncompress-demo.py filename scaleFactor saveOutput
```
**filename** - compressed image file to display

**scaleFactor** - this number will be used when converting the compressed file to a regular image

**saveOutput** - this is an optional argument that specifies if the decoded image should be saved

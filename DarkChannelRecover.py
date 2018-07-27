# -*- coding: utf-8 -*-


from PIL import Image
import numpy as np


def getDarkChannel(img, radius):

    height,width = img.shape[:2]
    imgGray = np.zeros((height, width), dtype=np.uint8)
    imgDark = np.zeros((height, width), dtype=np.uint8)
    
    #get min value of rgb
    imgGray = img.min(axis=-1) 
    #get dark channel
    min_filter = lambda i,j: imgGray[max(0,i-radius):min(i+radius, height),max(0,j-radius):min(j+radius, width)].min()
    row,col = np.unravel_index(np.arange(height*width), (height, width))
    for i,j in zip(row,col):
    	imgDark[i,j] = min_filter(i,j)
    return imgDark


def getAtomsphericLight(darkChannel, img, meanMode=False, percent=0.001):
    height, width = darkChannel.shape[:2]
    size = height*width
    num = int(size * percent)
    atomsphericLight = 0
    max_ind = np.argsort(darkChannel.reshape(size))[-num:]
    if meanMode:
	atomsphericLight = img.reshape(size*3)[max_ind].mean()
    else:
	atomsphericLight = img.reshape(size*3)[max_ind].max()
    return atomsphericLight

def recoverSceneRadiace(img, omega=0.95, t0=0.1, radius=7, meanModel=False, percent=0.001):

    img = np.array(Image.open(img))
    imgDark = getDarkChannel(img, radius)
    Image.fromarray(imgDark).save("dark.png")
    atomsphericLight = getAtomsphericLight(imgDark,img)
    imgDark = np.float64(imgDark)
    img = np.float64(img)
    transmission = 1 - omega * imgDark / atomsphericLight
    Image.fromarray(np.uint8(transmission*255)).save("trans.png")
    transmission[transmission<t0] = t0
    sceneRadiance = np.zeros(img.shape)
    for i in range(3):
    	sceneRadiance[:,:,i] = (img[:,:,i] - atomsphericLight)/transmission + atomsphericLight
    sceneRadiance[sceneRadiance>255] = 255
    sceneRadiance = np.uint8(sceneRadiance)
    return sceneRadiance
    
	

if __name__ == '__main__':
    res = recoverSceneRadiace("ny1.bmp", meanModel=True)
    im = Image.fromarray(res, 'RGB')
    im.save("result.png")


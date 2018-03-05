import mp_img_manip.tiling as til
import mp_img_manip.bulk_img_processing as blk
import numpy as np
import SimpleITK as sitk

def calculateRetardanceOverArea(retardance, orientation):
    
    # This gives me the orientation in 360 degrees, doubled to calculate alignment.
    circularOrientation = (2*np.pi/180)*(orientation/100);
    complexOrientation = np.exp(1j*circularOrientation);
    
    retardanceWeightedByOrientation = retardance*complexOrientation;
    
    numPixels = np.size(retardance);
    
    averageRetardance = np.sum(retardanceWeightedByOrientation)/numPixels;
    
    retMag = np.absolute(averageRetardance);
    retBaseAngle= np.angle(averageRetardance, deg=True)
    
    if retBaseAngle < 0:
        retBaseAngle += 360
        
    retAngle = retBaseAngle*100/2

    
    #bug: retAngle does not give right value.
    
    return (retMag,retAngle)



def convertIntensityToRetardance(itkImg, retCeiling, wavelength = 546, nmInput = True, degOutput = True):
    """Convert retardance intensities that are scaled to the image input 
    (e.g., 16 bit int) into to actual retardance values.  
    
    Input: 
        itkImg: The image being converted, as an ITK Image object
        retCeiling: The maximum retardance value corresponding to max intensity
        wavelength: The wavelength of light used to image, for converting 
            between degrees and retardance.  Defaults to 546 for the LOCI
            PolScope wavelength
        nmInput: The input retCeiling is in nm if true, degrees if false
        degOutput: The output is in degrees if true, nm if false
        
    Output:
        A new ITK image with retardance values either in degrees (default)
        or in nm (if degOutput is set to False)
    
    """



def DownsampleRetardanceImage(retImgPath, orientImgPath, scalePixelFactor, simulatedResolutionFactor = None):

    if not simulatedResolutionFactor:
        simulatedResolutionFactor = scalePixelFactor

    retImg = sitk.ReadImage(retImgPath)
    orientImg = sitk.ReadImage(orientImgPath)

    retArray= sitk.GetArrayFromImage(retImg)
    orientArray = sitk.GetArrayFromImage(orientImg)


    #if np.size(retImg) != np.size(orientImg):
     #   warn('The retardance and orientation image sizes do not match.  Please select inputs from the same image')    
      #  return

    #if (np.remainder(scalePixelFactor,1) != 0) or (np.remainder(simulatedResolutionFactor,1) != 0):
     #   warn('The scale factor(s) needs to be a positive integer, representing the number of pixels that compose the new pixel value')
      #  return
        #todo: allow non-integer resolution scaling
    
    arraySize = np.shape(retArray)
    
    (xPixelNum, xOffset) = til.calculateNumberOfTiles(arraySize[0], scalePixelFactor, simulatedResolutionFactor)
    (yPixelNum, yOffset) = til.calculateNumberOfTiles(arraySize[1], scalePixelFactor, simulatedResolutionFactor)

    downRetArray = np.zeros((xPixelNum, yPixelNum))
    downOrientArray = np.zeros((xPixelNum, yPixelNum))
    
    for y in range(0, yPixelNum):
        for x in range(0, xPixelNum):
            
            (xStart, xEnd) = til.getTileStartEndIndex(x, scalePixelFactor, xOffset, simulatedResolutionFactor)
            (yStart, yEnd) = til.getTileStartEndIndex(y, scalePixelFactor, yOffset, simulatedResolutionFactor)

            retNeighborhood = retArray[range(xStart,xEnd+1),range(yStart,yEnd+1)]
            orientNeighborhood = orientArray[range(xStart,xEnd+1),range(yStart,yEnd+1)]
            
            (retPixel, orientPixel) = calculateRetardanceOverArea(retNeighborhood,orientNeighborhood)
                
            downRetArray[x,y] = retPixel
            downOrientArray[x,y] = orientPixel

    downRetImg = sitk.GetImageFromArray(downRetArray)
    downRetImg = sitk.Cast(downRetImg, retImg.GetPixelID())
    
    downOrientImg = sitk.GetImageFromArray(downOrientArray)
    downOrientImg = sitk.Cast(downOrientImg, orientImg.GetPixelID())

    return (downRetImg, downOrientImg) 






def BatchDownsampleRetardance(retDir, orientDir, outputDir, scaleFactor, simulatedResolutionFactor = None):
    outputSuffix = '_DownsampledBy-' + str(scaleFactor) + 'x'

    if simulatedResolutionFactor and simulatedResolutionFactor != scaleFactor:
        outputSuffix = outputSuffix + '_SimRes-' + str(simulatedResolutionFactor) + 'x'

    (retImgPathList, orientImgPathList) = blk.findSharedImages(retDir, orientDir)
    
    for i in range(0, np.size(retImgPathList)):
        (downRetImg, downOrientImg) = DownsampleRetardanceImage(retImgPathList[i], orientImgPathList[i], scaleFactor, simulatedResolutionFactor)
        
        downRetPath = blk.createNewImagePath(retImgPathList[i], outputDir, outputSuffix + '_Ret')
        downOrientPath = blk.createNewImagePath(orientImgPathList[i], outputDir, outputSuffix + '_SlowAxis')
        
        sitk.WriteImage(downRetImg, downRetPath)
        sitk.WriteImage(downOrientImg, downOrientPath)
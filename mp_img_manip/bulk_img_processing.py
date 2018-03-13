import os
import csv
import mp_img_manip.utility_functions as util

def read_write_column_file(imgPath, fileName, numColumns = 3):
    """"Read in a file that specifies a name, and a number"""
    
    (imgDir, imgName) = os.path.split(imgPath)
    
    with open(imgDir + '/' + fileName, 'a+') as file:
        reader = csv.reader(file)
        writer = csv.writer(file)

        file.seek(0)

        try:
            header = next(reader)
        except StopIteration:
            message = 'Creating new file ' + fileName + ' in ' + imgDir 
            header = util.query_str_list(numColumns, message , 'Header')
            writer.writerow(header)
            
        
        for row in reader:
            if row[0] == imgName:
                return row
       
        print('There are no existing values for ' + imgName)
        
        new_row = [imgName]
        new_row.extend(util.query_float_list(header[1:]))
        
        #bug: This next line writes a blank row first.  
        
        writer.writerow(new_row)
        
        return new_row
        
        
def getBaseFileName(fileName):
    """This function extracts the 'base name' of a file, which is defined as
    the string up until the first underscore, or until the extension if
    there is no underscore"""
    
    fullFileName = os.path.split(fileName)[1]
    
    nameStr = os.path.splitext(fullFileName)[0]
    
    underscoreIndexes = nameStr.find('_')
    
    if underscoreIndexes > 0:     
        return nameStr[0:underscoreIndexes]
    else:
        return nameStr
    
def createNewImagePath(baseImgPath, outputDir, outputSuffix):
    """Create a new path string based on the pre-modification image path,
    an output directory, and the new output suffix to rename the file with"""
    baseName = getBaseFileName(baseImgPath)
    
    newName = baseName + outputSuffix + '.tif'
        
    newPath = os.path.join(outputDir, newName)
    return newPath
    

def findSharedImages(dirOne, dirTwo):
    """Base image names derived from directory one, are mapped to images from
    directory two."""
    
    #todo: modify dirOne_baseFileNames into a list of names, and then
    #implement a .txt file?
    
    #todo: make a check for different categories of name, if there are multiple instances of a single name?
    
    fileListOne = [f for f in os.listdir(dirOne) if f.endswith('.tif')]
    fileListTwo = [f for f in os.listdir(dirTwo) if f.endswith('.tif')]
        
    dirOneImagePaths = list()
    dirTwoImagePaths = list()

    for i in range(0,len(fileListOne)):
        baseNameOne = getBaseFileName(fileListOne[i])
        
        for j  in range(0,len(fileListTwo)):
            baseNameTwo = getBaseFileName(fileListTwo[j])
          
            if baseNameOne == baseNameTwo:
                
                dirOneImagePaths.append(dirOne + fileListOne[i])
                dirTwoImagePaths.append(dirTwo + fileListTwo[j])

    
    return (dirOneImagePaths, dirTwoImagePaths)
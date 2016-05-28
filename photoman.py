import click
import re
import logging
import sys as Sys
import os
from PIL.ExifTags import TAGS
import PIL.Image
import shutil
from datetime import datetime

# https://github.com/andrewning/sortphotos/blob/master/src/sortphotos.py
# https://github.com/jmathai/elodie/blob/master/elodie/filesystem.py
# https://gist.github.com/attilaolah/1940208

class FilesystemHelper(object):
    dateInPathRegex = re.compile(ur'(20\d{2})[-/](\d{2})[-](\d{2})')
    minimalDateInPathRegex = re.compile(ur'(20\d{2})[-/](\d{2})')

    def getRecursiveFilesWithExtension(self, path, extensions=None):
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if(
                    extensions is None or
                    filename.lower().endswith(extensions)
                ):
                    files.append(os.path.join(dirname, filename))
        return files

    def createFolder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    def createFolderWithDateStructure(self, base, dateobj):
        base = os.path.dirname(base)
        fullpath = os.path.join(base, str(dateobj.year), dateobj.strftime("%B"))
        self.createFolder(fullpath)
        return fullpath

    def findUniqueName(self, basePath, fileName, fileExtension):
        imageDestFullName = os.path.join(basePath, '{}.{}'.format(fileName, fileExtension))
        indexCurrentFile = 1
        while os.path.isfile(imageDestFullName):
            imageDestFullName = os.path.join(basePath, '{}_{}.{}'.format(fileName, indexCurrentFile, fileExtension))
            indexCurrentFile += 1
        return imageDestFullName

    def getDateFromFileName(self, fileName):
        dateMatches = self.dateInPathRegex.search(fileName)
        imageDateObject = datetime.strptime('1970-1-1', '%Y-%m-%d')
        if dateMatches and dateMatches.group():
            imageDateObject = datetime.strptime('{}-{}-{}'.format(dateMatches.group(1), dateMatches.group(2), dateMatches.group(3)), '%Y-%m-%d')
        else:
            dateMatches = self.minimalDateInPathRegex.search(fileName)
            if dateMatches and dateMatches.group():
                imageDateObject = datetime.strptime('{}-{}-{}'.format(dateMatches.group(1), dateMatches.group(2), '01'), '%Y-%m-%d')
            else:
                logging.info('Unable to identify date for [{}]'.format(fileName))
        return imageDateObject


class ImageExifHelper(object):
    def getExifByTag(self, imageExifInfo, tag):
        for (k,v) in imageExifInfo.iteritems():
            if TAGS.get(k) == tag:
                return v
        return None

    def getDateFromExif(self, image):
        dateTimeForImage = None
        if image != None and hasattr(image, '_getexif') and image._getexif() != None:
            dateTimeForImage = self.getExifByTag(image._getexif(), "DateTimeOriginal")
            if dateTimeForImage is None:
                dateTimeForImage = self.getExifByTag(image._getexif(), "DateTime")
        return dateTimeForImage

class Photoman(object):
    def importImagesByExtension(self, sourcePath, destinationPath, extension='jpg'):
        filesystemHelper = FilesystemHelper()
        imageExifHelper = ImageExifHelper()
        uiUtils = UIUtils()
        sourceImageFileList = filesystemHelper.getRecursiveFilesWithExtension(sourcePath, extension)

        globalImagesCounter = 1
        globalImagesTotalCount = len(sourceImageFileList)
        uiUtils.outputToUser('Identified {} files with extension {}'.format(globalImagesTotalCount, extension))
        for imageFile in sourceImageFileList:
            imageObject = PIL.Image.open(imageFile)
            imageDate = imageExifHelper.getDateFromExif(imageObject)
            if imageDate is None:
                imageDateObject = filesystemHelper.getDateFromFileName(imageFile)
                destImageFileName = imageDateObject.strftime('%d %A')
            else:
                imageDateObject = datetime.strptime(imageDate, '%Y:%m:%d %H:%M:%S')
                destImageFileName = imageDateObject.strftime('%d %A %Hh%M')
            baseDestImagePath = filesystemHelper.createFolderWithDateStructure(destinationPath, imageDateObject)
            uniqueFileFullName = filesystemHelper.findUniqueName(baseDestImagePath, destImageFileName, extension)
            shutil.copyfile(imageFile, uniqueFileFullName)
            uiUtils.printProgress(globalImagesCounter, globalImagesTotalCount, 'Completed')
            globalImagesCounter += 1

class UIUtils(object):
    def __init__(self):
        logging.basicConfig(filename='/tmp/photoman.log', filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M', level=logging.DEBUG)

    def printProgress (self, iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : number of decimals in percent complete (Int) 
            barLength   - Optional  : character length of bar (Int) 
        """
        filledLength    = int(round(barLength * iteration / float(total)))
        percents        = round(100.00 * (iteration / float(total)), decimals)
        bar             = '#' * filledLength + '-' * (barLength - filledLength)
        Sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
        Sys.stdout.flush()
        if iteration == total:
            print("\n")

    def outputToUser(self, string):
        print string

@click.command('import')
@click.option('--source', type=click.Path(file_okay=False),
        help='Import files from this directory, if specified.')
@click.option('--dest', type=click.Path(file_okay=False),
        help='Destination folder for the import. It does not necessarily exist')
def _import(source, dest):
    photoman = Photoman()
    photoman.importImagesByExtension(source, dest, 'jpg')
    photoman.importImagesByExtension(source, dest, 'jpeg')
    photoman.importImagesByExtension(source, dest, 'png')

@click.group()
def main():
    pass

main.add_command(_import)

if __name__ =='__main__':
    main()

import click
import hashlib
import re
import logging
import sys as Sys
import os
import shutil
from datetime import datetime
from lib.media import ExifTool

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

    def getMd5Hexdigest(self, fileName):
        return hashlib.md5(open(fileName, 'rb').read()).hexdigest()

    def getFirstIdenticalFileInFolder(self, sourceFile, targetFolder):
        sourceFileHash = self.getMd5Hexdigest(sourceFile)
        sourceFileSize = os.stat(sourceFile).st_size
        for dirname, dirnames, fileNames in os.walk(targetFolder):
            for fileName in fileNames:
                targetFile = os.path.join(dirname, fileName)
                if sourceFileSize == os.stat(targetFile).st_size:
                    if sourceFileHash == self.getMd5Hexdigest(targetFile):
                        return targetFile
        return None


class MediaHelper(object):
    def __init__(self, fileSystemHelper):
        self.fileSystemHelper = fileSystemHelper

    def getDateFromMediaFile(self, fileName):
        if fileName is None:
            return None
        mediaFileDate = None
        exifMediaFileDate = self.getExifByTags(fileName, ('DateTimeOriginal', 'DateTime'))
        if exifMediaFileDate is not None:
            mediaFileDate = datetime.strptime(exifMediaFileDate, '%Y:%m:%d %H:%M:%S')
        if mediaFileDate is None:
            mediaFileDate = self.fileSystemHelper.getDateFromFileName(fileName)
        return mediaFileDate


    def getExifByTags(self, mediaFile, tags):
        with ExifTool() as et:
            exifInfo = et.get_metadata(mediaFile)
            for key in tags:
                lookupKey = 'EXIF:' + key
                if lookupKey in exifInfo:
                    return exifInfo[lookupKey]
        return None

class Photoman(object):
    def importImagesByExtension(self, sourcePath, destinationPath, extension='jpg'):
        filesystemHelper = FilesystemHelper()
        mediaHelper = MediaHelper(filesystemHelper)
        uiUtils = UIUtils()
        mediaFileInputList = filesystemHelper.getRecursiveFilesWithExtension(sourcePath, extension)

        uiUtils.setProgressTotal(len(mediaFileInputList))
        uiUtils.resetProgress()
        uiUtils.outputToUser('Identified {} files with extension {}'.format(len(mediaFileInputList), extension))
        for mediaFile in mediaFileInputList:
            mediaFileDate = mediaHelper.getDateFromMediaFile(mediaFile)
            if mediaFileDate is not None:
                mediaFileOutputFileName = mediaFileDate.strftime('%d %A %Hh%M' if mediaFileDate.hour != 0 and mediaFileDate.minute != 0 else '%d %A')
                mediaFileOutputPath = filesystemHelper.createFolderWithDateStructure(destinationPath, mediaFileDate)
                duplicateMediaFile = filesystemHelper.getFirstIdenticalFileInFolder(mediaFile, mediaFileOutputPath)
                if duplicateMediaFile is None:
                    mediaFileOutputFullName = filesystemHelper.findUniqueName(mediaFileOutputPath, mediaFileOutputFileName, extension)
                    shutil.copyfile(mediaFile, mediaFileOutputFullName)
                else:
                    logging.warn('File [{}] already exists in destination [{}]. Skipping.'.format(mediaFile, duplicateMediaFile))
            else:
                logging.warn('File [{}] does not have any information about date. Skipping.'.format(mediaFile))
            uiUtils.incrementProgress()

class UIUtils(object):
    def __init__(self):
        logging.basicConfig(filename='/tmp/photoman.log', filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M', level=logging.DEBUG)
        self.progressBarTotal = 100
        self.progressBarCurrent = 0

    def setProgressTotal(self, progressBarTotal):
        self.progressBarTotal = progressBarTotal

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

    def incrementProgress(self, quantity = 1):
        self.progressBarCurrent += quantity
        self.printProgress(self.progressBarCurrent, self.progressBarTotal, 'Completed')

    def resetProgress(self):
        self.progressBarCurrent = 0

    def outputToUser(self, string):
        print string

@click.command('import')
@click.option('--source', type=click.Path(file_okay=False),
        help='Import files from this directory, if specified.')
@click.option('--dest', type=click.Path(file_okay=False),
        help='Destination folder for the import. It does not necessarily exist')
def _import(source, dest):
    photoman = Photoman()
    photoman.importImagesByExtension(source, dest, 'mov')
    photoman.importImagesByExtension(source, dest, 'jpg')
    photoman.importImagesByExtension(source, dest, 'jpeg')
    photoman.importImagesByExtension(source, dest, 'png')

@click.group()
def main():
    pass

main.add_command(_import)

if __name__ =='__main__':
    main()

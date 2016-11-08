import click
import hashlib
import mimetypes
import re
import sys
import logging
import sys as Sys
import os
import time
import shutil
from datetime import datetime
from lib.media import ExifTool
import magic

# https://github.com/andrewning/sortphotos/blob/master/src/sortphotos.py
# https://github.com/jmathai/elodie/blob/master/elodie/filesystem.py
# https://gist.github.com/attilaolah/1940208

class FilesystemHelper(object):
    dateInPathRegex = re.compile(ur'(20\d{2})[-/]?(\d{2})[-]?(\d{2})')
    minimalDateInPathRegex = re.compile(ur'(20\d{2})[-/](\d{2})')

    @staticmethod
    def folderExists(folder):
        return os.path.isdir(folder)

    @staticmethod
    def listFiles(path, extensions=None):
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if(
                    extensions is None or
                    filename.lower().endswith(extensions)
                ):
                    files.append(os.path.join(dirname, filename))
        return files

    @staticmethod
    def createFolder(folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    @staticmethod
    def createFolderWithDateStructure(base, dateobj):
        base = os.path.normpath(base) # this is wrong. truncates the last part of the string.
        fullpath = os.path.join(base, str(dateobj.year), dateobj.strftime("%B"))
        FilesystemHelper.createFolder(fullpath)
        return fullpath

    @staticmethod
    def findUniqueName(basePath, fileName, fileExtension):
        imageDestFullName = os.path.join(basePath, '{}{}'.format(fileName, fileExtension))
        indexCurrentFile = 1
        while os.path.isfile(imageDestFullName):
            imageDestFullName = os.path.join(basePath, '{}_{}{}'.format(fileName, indexCurrentFile, fileExtension))
            indexCurrentFile += 1
        return imageDestFullName

    @classmethod
    def getDateFromFileName(cls, fileName):
        dateMatches = cls.dateInPathRegex.search(fileName)
        imageDateObject = None
        if dateMatches and dateMatches.group():
            try:
                imageDateObject = datetime.strptime('{}-{}-{}'.format(dateMatches.group(1), dateMatches.group(2), dateMatches.group(3)), '%Y-%m-%d')
            except ValueError:
                imageDateObject = None
        if imageDateObject is None:
            dateMatches = cls.minimalDateInPathRegex.search(fileName)
            if dateMatches and dateMatches.group():
                try:
                    imageDateObject = datetime.strptime('{}-{}-{}'.format(dateMatches.group(1), dateMatches.group(2), '01'), '%Y-%m-%d')
                except ValueError:
                    imageDateObject = None
        if imageDateObject is None:
            imageDateObject = datetime.strptime('1970-1-1', '%Y-%m-%d')
            logging.info('Unable to identify date for [{}]'.format(fileName))
        return imageDateObject

    @staticmethod
    def getMd5Hexdigest(fileName):
        return hashlib.md5(open(fileName, 'rb').read()).hexdigest()

    @staticmethod
    def getFirstIdenticalFileInFolder(sourceFile, targetFolder):
        sourceFileSize = os.stat(sourceFile).st_size
        for dirname, dirnames, fileNames in os.walk(targetFolder):
            for fileName in fileNames:
                targetFile = os.path.join(dirname, fileName)
                if sourceFileSize == os.stat(targetFile).st_size:
                    sourceFileHash = FilesystemHelper.getMd5Hexdigest(sourceFile)
                    if sourceFileHash == FilesystemHelper.getMd5Hexdigest(targetFile):
                        return targetFile
        return None

    @staticmethod
    def copyFileWithProperties(sourceFile, targetPath):
        shutil.copy2(sourceFile, targetPath)


class MediaHelper(object):
    @staticmethod
    def getDateFromMediaFile(fileName):
        if fileName is None:
            return None
        mediaFileDate = None
        exifMediaFileDate = MediaHelper.getExifByTags(fileName, ('DateTimeOriginal', 'DateTime'))
        if exifMediaFileDate is not None:
            mediaFileDate = datetime.strptime(exifMediaFileDate, '%Y:%m:%d %H:%M:%S')
        if mediaFileDate is None:
            mediaFileDate = FilesystemHelper.getDateFromFileName(fileName)
        return mediaFileDate

    @staticmethod
    def getExifByTags(fileName, tags):
        with ExifTool() as et:
            exifInfo = et.get_metadata(fileName)
            for key in tags:
                lookupKey = 'EXIF:' + key
                if lookupKey in exifInfo:
                    return exifInfo[lookupKey]
        return None

class MediaFile(object):
    def __init__(self, fileName):
        self.fileName = fileName
        mimeMagic = magic.Magic(mime=True, uncompress=True)
        self.mimeType = mimeMagic.from_file(self.fileName)
        self.mimeExtension = mimetypes.guess_extension(self.mimeType)
        # mimetype returns jpe for jpeg files. http://stackoverflow.com/a/11396288
        if self.mimeExtension in ('.jpe', '.jpeg'):
            self.mimeExtension = '.jpg'
        self.isMedia = self.mimeType.split('/')[0] in ('video', 'image')
        if self.isMedia:
            self.date = MediaHelper.getDateFromMediaFile(fileName)

    def __str__(self):
        return 'Name: [{}] Mime: {} Extension: {} Date: {}'.format(self.fileName, self.mimeType, self.mimeExtension, self.date.strftime("%Y-%m-%d %H:%M"))


class DuplicateMediaFileException(Exception):
    def __init__(self, existingFile):
        self.existingFile = existingFile


class MediaSorter(object):
    @staticmethod
    def sortFiles(sourceFolder, targetFolder, limitCount = None):
        uiUtils = UIUtils()
        mimeMagic = magic.Magic(mime=True, uncompress=True)
        mimetypes.init()
        inputFileList = FilesystemHelper.listFiles(sourceFolder)

        if limitCount is not None:
            inputFileList = inputFileList[:limitCount]

        uiUtils.setProgressTotal(len(inputFileList))
        uiUtils.outputToUser('Identified {} files'.format(len(inputFileList)))
        for inputFile in inputFileList:
            sourceMediaFile = MediaFile(inputFile)
            if sourceMediaFile.isMedia:
                try:
                    MediaFileManager.copyMediaFile(sourceMediaFile, targetFolder)
                except DuplicateMediaFileException as duplicateException:
                    logging.warn('File [{}] already exists in destination as [{}]. Skipping.'.format(inputFile, duplicateException.existingFile))
            else:
                logging.warn('File [{}] does not have a recognized media type [{}]. Skipping.'.format(inputFile, sourceMediaFile.mimeExtension))
            uiUtils.incrementProgress()

class MediaFileManager(object):
    @staticmethod
    def generateUniqueTargetFileName(sourceMediaFile, targetFolder):
        mediaFileDate = sourceMediaFile.date
        if mediaFileDate.hour != 0 and mediaFileDate.minute != 0:
            targetFileDateBaseName = mediaFileDate.strftime('%d %A %Hh%M')
        else:
            targetFileDateBaseName = mediaFileDate.strftime('%d %A')
        return FilesystemHelper.findUniqueName(targetFolder, targetFileDateBaseName, sourceMediaFile.mimeExtension)

    @staticmethod
    def generateTargetFolder(sourceMediaFile, targetBasePath):
        return FilesystemHelper.createFolderWithDateStructure(targetBasePath, sourceMediaFile.date)

    @staticmethod
    def checkDuplicates(mediaFile, targetBasePath):
        identicalFileInFolder = FilesystemHelper.getFirstIdenticalFileInFolder(mediaFile.fileName, targetBasePath)
        if identicalFileInFolder is not None:
            raise DuplicateMediaFileException(identicalFileInFolder)

    @staticmethod
    def copyMediaFile(mediaFile, targetBasePath):
        targetFolder = MediaFileManager.generateTargetFolder(mediaFile, targetBasePath)
        if not FilesystemHelper.folderExists(targetFolder):
            FilesystemHelper.createFolder(targetFolder)
        try:
            MediaFileManager.checkDuplicates(mediaFile, targetFolder)
        except DuplicateMediaFileException as duplicateException:
            raise duplicateException
        targetUniqueFile = MediaFileManager.generateUniqueTargetFileName(mediaFile, targetFolder)
        targetUniquePath = os.path.join(targetFolder, targetUniqueFile)
        FilesystemHelper.copyFileWithProperties(mediaFile.fileName, targetUniquePath)


class UIUtils(object):
    def __init__(self):
        logging.basicConfig(filename='/tmp/mediasorter.log', filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M', level=logging.DEBUG)
        self.progressBarTotal = 100
        self.progressBarCurrent = 0

    def setProgressTotal(self, progressBarTotal):
        self.progressBarTotal = progressBarTotal
        self.resetProgress()

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
@click.argument('source', type=click.Path(file_okay=True),
        required=True)
@click.argument('target', type=click.Path(file_okay=False),
        required=True)
@click.option('--limit', type=int, default=None)
@click.pass_context
def _import(ctx, source, target, limit):
    mediasorter = MediaSorter()
    mediasorter.sortFiles(source, target, limit)

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj['DEBUG'] = debug

main.add_command(_import)

if __name__ =='__main__':
    main(obj={})

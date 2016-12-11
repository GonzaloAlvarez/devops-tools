import click
import hashlib
import mimetypes
import re
import sys
import logging
import sys as Sys
import os
import platform
import shutil
import cProfile
import magic
import time
import warnings
from datetime import timedelta
from pstats import Stats
from datetime import datetime
from lib.media import ExifTool
from lib.lang import Singleton
from PIL import Image
from PIL.ExifTags import TAGS
from lib.exceptions import DuplicateMediaFileException

class FilesystemHelper(object):
    dateInPathRegex = re.compile(ur'(20\d{2})[-/]?(\d{2})[-]?(\d{2})')
    eurFuzzyDateInPathRegex = re.compile(ur'([0-3][0-9])([0-1][0-9])([9,0,1][0-9])')
    minimalDateInPathRegex = re.compile(ur'(20\d{2})[-/](\d{2})')

    @staticmethod
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    @staticmethod
    def which(program):
        fpath, fname = os.path.split(program)
        if fpath:
            if FilesystemHelper.is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if FilesystemHelper.is_exe(exe_file):
                    return exe_file

        return None

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
    def createFolder(base, *args):
        base = os.path.normpath(base)
        if not args:
            fullpath = base
        else:
            path_parts = [str(arg) for arg in args]
            fullpath = os.path.join(base, *path_parts)
        if not os.path.exists(fullpath):
            os.makedirs(fullpath)
        return fullpath

    @staticmethod
    def symlink(source, target):
        if not os.path.isdir(os.path.dirname(target)):
            FilesystemHelper.createFolder(os.path.dirname(target))
        sourceFolder = os.path.dirname(source)
        targetFolder = os.path.dirname(target)
        relPath = os.path.relpath(sourceFolder, targetFolder)
        sourcerel = os.path.join(relPath, os.path.basename(source))
        initialPath = os.getcwd()
        os.chdir(targetFolder)
        os.symlink(sourcerel, target)
        os.chdir(initialPath)

    @staticmethod
    def getDateFromFileTime(file_time):
        time_localtime = time.localtime(file_time)
        return datetime.fromtimestamp(time.mktime(time_localtime))

    @staticmethod
    def getFileCreationDate(path_to_file):
        """
        Try to get the date that a file was created, falling back to when it was
        last modified if that isn't possible.
        See http://stackoverflow.com/a/39501288/1709587 for explanation.
        """
        if platform.system() == 'Windows':
            return FilesystemHelper.getDateFromFileTime(os.path.getctime(path_to_file))
        else:
            stat = os.stat(path_to_file)
            try:
                return FilesystemHelper.getDateFromFileTime(stat.st_birthtime)
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                return FilesystemHelper.getDateFromFileTime(stat.st_mtime)

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
            dateMatches = cls.eurFuzzyDateInPathRegex.search(fileName)
            if dateMatches and dateMatches.group():
                try:
                    imageDateObject = datetime.strptime('{}-{}-{}'.format(dateMatches.group(1), dateMatches.group(2), dateMatches.group(3)), '%d-%m-%y')
                except ValueError:
                    imageDateObject = None
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
    latest_date = None

    @staticmethod
    def getDateFromMediaFile(mediaFile):
        if mediaFile is None or mediaFile.fileName is None:
            return None
        mediaFileDate = None
        exifMediaFileDate = MediaHelper.getExifByTags(mediaFile, ('DateTimeOriginal', 'DateTime', 'CreateDate', 'ModifyDate'))
        if exifMediaFileDate:
            try:
                mediaFileDate = datetime.strptime(exifMediaFileDate, '%Y:%m:%d %H:%M:%S')
                MediaHelper.latest_date = mediaFileDate
            except:
                mediaFileDate = None
        if not mediaFileDate:
            mediaFileDate = FilesystemHelper.getDateFromFileName(mediaFile.fileName)
        if not mediaFileDate:
            logging.info('Unable to identify date for [{}]'.format(mediaFile.fileName))
            EventHandler.instance().count('unknown_date')
            if MediaHelper.latest_date:
                EventHandler.instance().count('using_previous_date')
                mediaFileDate = MediaHelper.latest_date
            else:
                EventHandler.instance().count('using_filedate')
                mediaFileDate = FilesystemHelper.getFileCreationDate(mediaFile.fileName).strftime('%Y-%m-%d')
        return mediaFileDate

    @staticmethod
    def getExifByTags(mediaFile, lookupTags):
        if mediaFile.isImage:
            exifValue = MediaHelper.getExifByTagsUsingPIL(mediaFile, lookupTags)
            if exifValue is not None:
                return exifValue
        else:
            EventHandler.instance().count('Video')
        return MediaHelper.getExifByTagsUsingExifTool(mediaFile, lookupTags)

    @staticmethod
    def getExifByTagsUsingExifTool(mediaFile, lookupTags):
        with ExifTool() as et:
            exifInfo = et.get_metadata(mediaFile.fileName)
            for key in lookupTags:
                lookupKey = 'EXIF:' + key
                if lookupKey in exifInfo:
                    return exifInfo[lookupKey]
        return None

    @staticmethod
    def getExifByTagsUsingPIL(mediaFile, lookupTags):
        try:
            pilImage = Image.open(mediaFile.fileName)
            if '_getexif' in dir(pilImage):
                pilExif = pilImage._getexif()
                if pilExif is not None:
                    for tag, value in pilExif.items():
                        for lookupTag in lookupTags:
                            if TAGS.get(tag) == lookupTag:
                                return value
                    EventHandler.instance().count('PIL_nodate')
                else:
                    EventHandler.instance().count('PIL_noexif')
            else:
                EventHandler.instance().count('PIL_notsupported')
        except:
            EventHandler.instance().count('PIL_exception')
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
        self.isImage = self.mimeType.split('/')[0] == 'image'
        if self.isMedia:
            self.date = MediaHelper.getDateFromMediaFile(self)

    def __str__(self):
        return 'Name: [{}] Mime: {} Extension: {} Date: {}'.format(self.fileName, self.mimeType, self.mimeExtension, self.date.strftime("%Y-%m-%d %H:%M"))

class MediaSorter(object):
    @staticmethod
    def importFiles(sourceFolder, targetFolder, limitCount = None, skipCount = None, dryrun = False):
        uiUtils = UIUtils.instance()
        uiUtils.outputNoNewLine('Looking up files...')
        mimeMagic = magic.Magic(mime=True, uncompress=True)
        mimetypes.init()
        inputFileList = FilesystemHelper.listFiles(sourceFolder)
        uiUtils.output('Identified {} files'.format(len(inputFileList)))

        if limitCount is not None:
            if skipCount is not None and skipCount < len(inputFileList):
                inputFileList = inputFileList[skipCount:limitCount+skipCount]
                uiUtils.output('Working on {} files starting from {}'.format(limitCount, skipCount))
            else:
                inputFileList = inputFileList[:limitCount]
                uiUtils.output('Working on the first {} files'.format(limitCount))

        warnings.filterwarnings('ignore') #required for PIL
        uiUtils.setProgressTotal(len(inputFileList))
        for inputFile in inputFileList:
            sourceMediaFile = MediaFile(inputFile)
            if sourceMediaFile.isMedia and not dryrun:
                try:
                    MediaFileManager.importMediaFile(sourceMediaFile, targetFolder, sourceFolder)
                except DuplicateMediaFileException as duplicateException:
                    EventHandler.instance().count('duplicated')
                    logging.warn('File [{}] already exists in destination as [{}]. Skipping.'.format(inputFile, duplicateException.existingFile))
            elif not sourceMediaFile.isMedia:
                EventHandler.instance().count('unknown_media_type')
                logging.warn('File [{}] does not have a recognized media type [{}]. Skipping.'.format(inputFile, sourceMediaFile.mimeExtension))
            uiUtils.incrementProgress()

@Singleton
class EventHandler(object):
    def __init__(self):
        self.metrics = {}

    def count(self, event):
        if event not in self.metrics:
            self.metrics[event] = 0
        self.metrics[event] += 1;

    def __str__(self):
        strings = []
        for key, value in self.metrics.iteritems():
            strings.append('Event [{}] count [{}]'.format(key, value))
        return '\n'.join(strings)


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
        dateobj = sourceMediaFile.date
        mime = sourceMediaFile.mimeType.split('/')[0].capitalize()
        return FilesystemHelper.createFolder(targetBasePath, mime, str(dateobj.year), dateobj.strftime("%B"))

    @staticmethod
    def checkDuplicates(mediaFile, targetBasePath):
        identicalFileInFolder = FilesystemHelper.getFirstIdenticalFileInFolder(mediaFile.fileName, targetBasePath)
        if identicalFileInFolder is not None:
            raise DuplicateMediaFileException(identicalFileInFolder)

    @staticmethod
    def importMediaFile(mediaFile, targetBasePath, sourceBasePath):
        targetFolder = MediaFileManager.generateTargetFolder(mediaFile, targetBasePath)
        try:
            MediaFileManager.checkDuplicates(mediaFile, targetFolder)
        except DuplicateMediaFileException as duplicateException:
            raise duplicateException
        targetUniqueFile = MediaFileManager.generateUniqueTargetFileName(mediaFile, targetFolder)
        targetUniquePath = os.path.join(targetFolder, targetUniqueFile)
        FilesystemHelper.copyFileWithProperties(mediaFile.fileName, targetUniquePath)
        targetSymbolicLink = os.path.join(targetBasePath, 'Original', os.path.relpath(mediaFile.fileName, sourceBasePath))
        logging.info('target: [{}]'.format(targetSymbolicLink))
        FilesystemHelper.symlink(targetUniquePath,targetSymbolicLink)


@Singleton
class UIUtils(object):
    def __init__(self):
        logging.basicConfig(filename='/tmp/mediasorter.log', filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M', level=logging.DEBUG)
        self.progressBarTotal = 100
        self.progressBarCurrent = 0

    def setProgressTotal(self, progressBarTotal):
        self.progressBarTotal = progressBarTotal
        self.resetProgress()

    def printProgress (self, iteration, total, prefix = '', suffix = '', decimals = 2, barLength=100):
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
        rows, columns = os.popen('stty size', 'r').read().split()
        barLength = min(int(columns) - 20, barLength)
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

    def output(self, string):
        print string

    def outputNoNewLine(self, string):
        sys.stdout.write('{}\r'.format(str(string)))
        sys.stdout.flush()

@click.command('import')
@click.argument('source', type=click.Path(file_okay=True),
        required=True)
@click.argument('target', type=click.Path(file_okay=False),
        required=True)
@click.option('--limit', type=int, default=None)
@click.option('--skip', type=int, default=None)
@click.option('--dryrun/--no-dryrun', default=False)
@click.pass_context
def _import(ctx, source, target, limit, skip, dryrun):
    if ctx.obj['DEBUG']:
        profile = cProfile.Profile()
        profile.enable()
        startTime = time.time()
    mediasorter = MediaSorter()
    mediasorter.importFiles(source, target, limit, skip, dryrun)
    if ctx.obj['DEBUG']:
        profile.disable()
        UIUtils.instance().output('Time elapsed: {}'.format(str(timedelta(seconds=(time.time() - startTime)))))
        UIUtils.instance().output('Profiler data:')
        stats = Stats(profile).sort_stats('time')
        stats.print_stats(10)
        UIUtils.instance().output(EventHandler.instance())

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj['DEBUG'] = debug

main.add_command(_import)

if __name__ =='__main__':
    main(obj={})

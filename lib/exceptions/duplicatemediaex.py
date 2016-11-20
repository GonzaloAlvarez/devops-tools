class DuplicateMediaFileException(Exception):
    def __init__(self, existingFile):
        self.existingFile = existingFile



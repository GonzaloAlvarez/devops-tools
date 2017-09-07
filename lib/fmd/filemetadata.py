from blitzdb import Document
from blitzdb import FileBackend

class FileMetadata(Document):
    class Meta(Document.Meta):
        primary_key = 'fid'

class FileMetadataStore():
    def __init__(self, dbFilePath):
        self.db = FileBackend(dbFilePath)
        self.db.create_index(FileMetadata, 'fid')

    def insert(self, fileId, attributes):
        try:
            self.get(fileId)
        except Document.DoesNotExist:
            metadata = {'fid': fileId}
            metadata.update(dict(attributes))
            fileMetadata = FileMetadata(metadata)
            self.db.save(fileMetadata)
            self.db.commit()
            return True
        return False

    def get(self, fileId):
        return self.db.get(FileMetadata, {'fid': fileId})

    def delete(self, fileId):
        self.db.delete(FileMetadata({'fid': fileId}))
        self.db.commit()
        return True

    def update(self, fileId, attributes):
        try:
            currentFM = self.get(fileId)
        except Document.DoesNotExist:
            return False
        attrs = currentFM.attributes
        attrs.update(dict(attributes))
        newFM = FileMetadata(attrs)
        self.db.save(newFM)
        self.db.commit()
        return True

    def list(self):
        return [k for k in self.db.filter(FileMetadata, {})]

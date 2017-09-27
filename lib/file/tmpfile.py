import tempfile
import os, errno
from lib.lang.singleton import Singleton

@Singleton
class TemporaryFile(object):
    _stack = []

    def new(self):
        descriptor, filename = tempfile.mkstemp()
        self._stack.append({'descriptor': descriptor, 'filename': filename})
        return descriptor, filename

    def _silent_remove(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def cleanup(self):
        for entry in self._stack:
            if 'descriptor' in entry and isinstance(entry['descriptor'], int):
                os.close(entry['descriptor'])
            if 'descriptor' in entry and callable(getattr(entry['descriptor'], 'close', None)):
                entry['descriptor'].close()
            if 'filename' in entry:
                self._silent_remove(entry['filename'])
        self._stack = []

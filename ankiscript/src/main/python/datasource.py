import os.path
import zipfile
import shutil
from urllib import request
from aqt import mw


def get_datasource(source):
    if os.path.isdir(source):
        # if source is a dir assume is local and uncompressed, 
        return LocalDirectoryDataSource(source)
    elif os.path.isfile(source) and zipfile.is_zipfile(source):
        # otherwise if a file test if is a zip file
        return ZipFileDataSource(source)
    else:
        # assume is a url to a web hosted zip file
        return UrlDataSource(source)


class DataSource:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def read(self, dirs, filename, binary=False):
        '''
        Return text/binary contents of a file, None if file does not exist.
        '''
        return self._read([_sanitise(d) for d in dirs], _sanitise(filename), binary)

    def copy_file(self, filename, src, dest, mkdirs=True):
        # create target directory if it does not exist
        if mkdirs and not os.path.exists(destination):
            os.makedirs(destination)
        return self._copy_file(filename, src, dest)

    def copy_files(self, src, dest, mkdirs=True):
        # create target directory if it does not exist
        if mkdirs and not os.path.exists(destination):
            os.makedirs(destination)
        return self._copy_files(src, dest)

    def install_media_file(self, filename, binary=None):
        '''
            install file to media collection, returning actual filename used by Anki
        '''
        if binary is None:
            binary = _is_binary_file(filename)

        data = self.read(['media'], filename, binary)
        if data:
            return mw.col.media.writeData(filename, data if binary else data.encode('utf-8'))
        else:
            return None


class LocalDirectoryDataSource(DataSource):

    def __init__(self, name):
        self.name = name

    def _read(self, dirs, filename, binary=False):
        '''
        Return text/binary contents of a file, None if file does not exist.
        '''
        pathname = os.path.join(self.name, *dirs, filename)
        if os.path.exists(pathname):
            if binary:
                with open(pathname, 'rb') as f:
                    return f.read()
            else:
                with self._open_text_file(pathname) as f:
                    return f.read()
        else:
            return None

    def _copy_file(self, filename, src, dest):
        shutil.copyfile(os.path.join(self.name, src, filename), os.path.join(dest, filename))

    def _copy_files(self, src, dest):
        for filename in os.listdir(os.path.join(self.name, src)):
            self.copy_file(filename, src, dest)

    def _open_text_file(self, filename):
        '''
        Return file object to read from.
        
        Tries to load it as UTF-8, falling back to the system default file encoding if that fails.
        '''
        try:
            return open(os.path.join(self.name, filename), 'r', encoding='utf-8')
        except:
            return open(os.path.join(self.name, filename), 'r')


class ZipDataSource(DataSource):

    def __enter__(self):
        self._zipfile = self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._zipfile.close()
        return False

    def _read(self, dirs, filename, binary=False):
        '''
        Return text/binary contents of a file, None if file does not exist.
        '''
        dirpath = '/'.join(dirs) + '/' + filename if len(dirs) else ''
        path = zipfile.Path(self._zipfile, dirpath + filename)
        if path.exists():
            if binary:
                return path.read_bytes()
            else:
                with path.open() as f:
                    return '\n'.join(f.readlines())
        else:
            return None
    
    def _copy_file(self, filename, src, dest):
        path = zipfile.Path(self._zipfile, src + '/' + filename)
        with open(dest, 'wb') as f:
            f.write(path.read_bytes())

    def _copy_files(self, src, dest):
        for path in zipfile.Path(self._zipfile, src).iterdir():
            with open(dest, 'wb') as f:
                f.write(path.read_bytes())

    
class ZipFileDataSource(ZipDataSource):

    def __init__(self, name):
        self.name = name

    def open(self):
        return ZipFile(self.name)

    
class UrlDataSource(ZipDataSource):

    def __init__(self, url):
        '''
        url - URL of zip file containing setup/lesson contents
        '''
        self.url = url

    def open(self):
        response = request(self.url)
        if response.status != 200:
            raise Exception('Cannot open {0} - got {1} {2}'.format(self.url, response.status, response.reason))
        return ZipFile(io.BytesIO(response.read()))


def _sanitise(name):
    s = name
    s = s.replace(' ', '_')
    s = s.replace('<', '_from_')
    s = s.replace('>', '_to_')
    s = s.replace('(', '_')
    s = s.replace(')', '_')
    s = s.replace('[', '_')
    s = s.replace(']', '_')
    s = s.replace('{', '_')
    s = s.replace('}', '_')
    s = s.replace(':', '_')
    s = s.replace('$', '')
    s = s.replace('*', '')
    s = s.replace(',', '')
    
    while '__' in s:
        s = s.replace('__', '_')

    s = s.replace('_.front', '.front')
    s = s.replace('_.back', '.back')
        
    if s[0] == '_':
        s = s[1:]
    if s[-1] == '_':
        s = s[:-1]

    return s

def _is_binary_file(filename):
    return os.path.splitext(filename)[1] in ['.mp3', '.ogg', '.jpg', '.png']

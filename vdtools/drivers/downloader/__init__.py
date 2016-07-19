import os
import wget
from threading import Thread
from vdtools.dev.driver import Driver, check_output

PRINT = False
PATH_DOWNLOADER = "/opt/downloads"

class Downloader(Driver):
    def setup(self):
        if not os.path.exists(PATH_DOWNLOADER):
            os.makedirs(PATH_DOWNLOADER, 0o755)
    
    def _do_download(self, url):
        try:
            filename = wget.download(url, out=PATH_DOWNLOADER, bar=None)
            if PRINT:
                print('Downloader: filename=%s' % str(filename))
        except:
            if PRINT:
                print('Downloader: failed to download')
    
    def _download(self, url):
        Thread(target=self._do_download, args=(url,)).start()
        return True
    
    @check_output
    def put(self, args):
        url = args.get('url')
        if url:
            if self._download(url):
                return {'enable':'true'}

#
# Copyright (C) 2016 Yi-Wei Ci
#
# Distributed under the terms of the MIT license.
#

import langid
from base64 import b64decode
from vdtools.dev.driver import Driver, wrapper

PRINT = False

class LangIdentifiyer(Driver):
    def _get_lang(self, text):
        buf = b64decode(text)
        if buf:
            doc = buf.decode('utf8')
            lang = langid.classify(doc)[0]
            if PRINT:
                print('LangIdentifier: lang=%s' % lang)
            return lang

    @wrapper
    def put(self, *args, **kwargs):
        text = kwargs.get('content')
        if text:
            lang = self._get_lang(text)
            if lang:
                return {'lang':lang}

#      blob.py
#      
#      Copyright (C) 2014 Yi-Wei Ci <ciyiwei@hotmail.com>
#      
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#      
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#      
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#      MA 02110-1301, USA.

from dev.anon import VDevAnon
from textblob import TextBlob
from base64 import decodestring

DEBUG_BLOB = False

class Blob(VDevAnon):    
    def get_sentiment(self, text):
        buf = decodestring(text)
        if buf:
            blob = TextBlob(buf.decode('utf8'))
            return (blob.sentiment.polarity,  blob.sentiment.subjectivity)
        else:
            return (None, None)
    
    def put(self, buf):
        args = self.get_args(buf)
        if args and type(args) == dict:
            text = args.get('File')
            if text:
                polarity, subjectivity = self.get_sentiment(text)
                if polarity != None and subjectivity != None:
                    if DEBUG_BLOB:
                        print('Blob: polarity=%f, subjectivity=%f' % (polarity, subjectivity))
                    ret = {'Polarity':polarity, 'Subjectivity':subjectivity}
                    name = args.get('Name')
                    if name:
                        ret.update({'Name':name})
                    timer = args.get('Timer')
                    if timer:
                        ret.update({'Timer':timer})
                    return ret
    
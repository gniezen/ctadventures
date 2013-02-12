import json
import re

#shameless copy paste from json/decoder.py
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

class ConcatJSONDecoder(json.JSONDecoder):
    def decode(self, s, _w=WHITESPACE.match):
        s_len = len(s)

        objs = []
        end = 0
        while end != s_len:
            obj, end = self.raw_decode(s, idx=_w(s, end).end())
            end = _w(s, end).end()
            objs.append(obj)
        return objs

d = json.load(open('big.json').read(), cls=ConcatJSONDecoder)

for i in d:
    print i

#def iload_json(buff, decoder=None, _w=json.decoder.WHITESPACE.match):
#    """Generate a sequence of top-level JSON values declared in the
#    buffer.

#    >>> list(iload_json('[1, 2] "a" { "c": 3 }'))
#    [[1, 2], u'a', {u'c': 3}]
#    """

#    decoder = decoder or json._default_decoder
#    idx = _w(buff, 0).end()
#    end = len(buff)

#    try:
#        while idx != end:
#            (val, idx) = decoder.raw_decode(buff, idx=idx)
#            yield val
#            idx = _w(buff, idx).end()
#    except ValueError as exc:
#        raise ValueError('%s (%r at position %d).' % (exc, buff[idx:], idx))


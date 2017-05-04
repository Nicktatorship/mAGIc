class NLDecoder(object):
    _struct = ''
    _fields = {}
    _flags = {}

    def __init__(self, stream):
        self._value = struct.unpack(self._struct,
            stream.read(struct.calcsize(self._struct)))

    def __getattr(self, item):
        if item in self._fields.keys():
            keyid = self._fields[item]
            return self._value[keyid]

        elif item in self._flags.keys():
            flag, bit = self._flags[item]
            return bool(self._value[flag] & bit)

        else:
            raise AttributeError(item)

    def __repr__(self):
        return repr(self._value)

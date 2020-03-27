""" philoseismos: engineering seismologist's toolbox.

This file defines the BinaryFileHeader object - a dictionary-like representation of a SEG-Y
binary file header.

author: Ivan Dubrovin
e-mail: io.dubrovin@icloud.com """

import struct

from philoseismos.segy import constants as const


class BinaryFileHeader:
    """ This object represents a binary file header of a SEG-Y file. """

    def __init__(self):
        """ Create a new BFH object. """

        self._dict = None

    @classmethod
    def load(cls, file: str):
        """ Load BFH from a SEG-Y file.

        Args:
            file (str) : Path to the SEG-Y file to load from.

        """

        bfh = cls()

        with open(file, 'br') as sgy:
            # skip the TFH, read the BFH bytes
            sgy.seek(3200)
            raw = sgy.read(400)

        # check the endiannes
        if 1 <= struct.unpack('>h', raw[24:26])[0] <= 16:
            endian = '>'
        else:
            endian = '<'

        # unpack and store the values
        values = struct.unpack(endian + const.BFHFS, raw)
        bfh._dict = dict(zip(const.BFHCOLS, values))

        return bfh

    def __getitem__(self, key):
        return self._dict.get(key)

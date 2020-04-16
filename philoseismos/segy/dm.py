""" philoseismos: engineering seismologist's toolbox.

author: Ivan Dubrovin
e-mail: io.dubrovin@icloud.com """

import struct
import numpy as np

from philoseismos.segy import gfunc
from philoseismos.segy import constants as const


class DataMatrix:
    """ This object represents traces of the SEG-Y file. """

    def __init__(self):
        self.dt = None
        self.t = None
        self._m = None
        self._headers = None

    @classmethod
    def load(cls, file: str):
        """ Load the DataMatrix from a SEG-Y file. """

        dm = cls()

        with open(file, 'br') as sgy:
            # grab endian, format letter, trace length, sample size, number of traces, data type, and sample interval
            endian = gfunc.grab_endiannes(sgy)
            sfc = gfunc.grab_sample_format_code(sgy)
            tl = gfunc.grab_trace_length(sgy)
            nt = gfunc.grab_number_of_traces(sgy)
            si = gfunc.grab_sample_interval(sgy)

            ss, fl, _ = const.SFC[sfc]
            dtype = const.DTYPEMAP[sfc]

            dm._m = np.empty(shape=(nt, tl), dtype=dtype)

            sgy.seek(3600)

            if sfc == 1:  # IBM is a special case
                pass
            else:
                format_string = endian + fl * tl

                for i in range(nt):
                    sgy.seek(sgy.tell() + 240)  # skip trace header
                    raw_trace = sgy.read(ss * tl)

                    values = struct.unpack(format_string, raw_trace)
                    dm._m[i] = values

        dm.dt = si
        dm.t = np.arange(0, si * tl / 1000, si / 1000)

        return dm

    def extract_by_indices(self, indices):
        """ Return a new DM, constructed from traces extracted by given indices. """

        new = DataMatrix()
        new.dt = self.dt
        new.t = np.copy(self.t)
        new._m = np.copy(self._m[indices])
        new._headers = self._headers.loc[indices, :].copy()

        return new

    def filter(self, header, first, last, step):
        """ Return a new DM filtered in a way that header = range(first, last + 1, step).

        Args:
            header (str): Header name to filter by.
            first (float): First value of the header.
            last (float): Last value of the header (inclusive).
            step (float): Step of the header.

        Returns:
            A new DataMatrix object.

        """

        new = DataMatrix()
        new.dt = self.dt
        new.t = np.copy(self.t)

        subset = self._headers._df.loc[self._headers._df[header] >= first]
        subset = subset.loc[subset[header] <= last]
        subset = subset.loc[subset.OFFSET % step == 0]

        new._m = self._m[subset.index]
        new._headers = subset.reset_index().drop('index', axis=1)
        new._headers.TRACENO = new._headers.index + 1
        new._headers.SEQNO = new._headers.index + 1

        return new

    def __repr__(self):
        return f'DataMatrix: {self._m.shape[0]} traces, {self._m.shape[1]} samples, dt={self.dt}'

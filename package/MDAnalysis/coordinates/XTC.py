# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://www.MDAnalysis.org
# Copyright (c) 2006-2015 Naveen Michaud-Agrawal, Elizabeth J. Denning, Oliver
# Beckstein and contributors (see AUTHORS for the full list)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#
from .XDR import XDRBaseReader, XDRBaseWriter
from ..lib.formats.xdrlib import XTCFile
from ..lib.mdamath import triclinic_vectors


class XTCWriter(XDRBaseWriter):
    format = 'XTC'
    units = {'time': 'ps', 'length': 'nm'}
    _file = XTCFile

    def write_next_timestep(self, ts):
        """Write timestep object into trajectory.

        Parameters
        ----------
        ts: TimeStep

        See Also
        --------
        <FormatWriter>.write(AtomGroup/Universe/TimeStep)
        The normal write() method takes a more general input
        """
        xyz = ts.positions.copy()
        time = ts.time
        step = ts.frame
        dimensions = ts.dimensions

        if self._convert_units:
            xyz = self.convert_pos_to_native(xyz, inplace=False)
            dimensions = self.convert_dimensions_to_unitcell(ts, inplace=False)

        box = triclinic_vectors(dimensions)

        self._xdr.write(xyz, box, step, time)


class XTCReader(XDRBaseReader):
    """XTC is a compressed trajectory format from Gromacs. The trajectory is saved
    with reduced precision (3 decimal places) compared to other lossless
    formarts like TRR and DCD. The main advantage of XTC files is that they
    require significantly less disk space and the loss of precision is usually
    not a problem.

    Parameter
    ---------
    filename: str
        filename of the trajectory
    convert_units: bool (optional)
        convert into MDAnalysis units
    sub: atomgroup (optional)
        Yeah what is that exactly
    refresh_offsets: bool (optional)
        Recalculate offsets for random access from file. If ``False`` try to
        retrieve offsets from hidden offsets file.

    """
    format = 'XTC'
    units = {'time': 'ps', 'length': 'nm'}
    _writer = XTCWriter
    _file = XTCFile

    def _frame_to_ts(self, frame, ts):
        """convert a xtc-frame to a mda TimeStep"""
        ts.frame = self._frame
        ts.time = frame.time
        ts.data['step'] = frame.step

        if self._sub is not None:
            ts.positions = frame.x[self._sub]
        else:
            ts.positions = frame.x
        if self.convert_units:
            self.convert_pos_from_native(ts.positions)

        return ts

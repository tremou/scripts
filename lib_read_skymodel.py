#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 - Francesco de Gasperin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This library has a read_skymodel function which read a skymodel and return a dict with all the entries.
# One can specify a subset of entries to be returned. Default values and missing fields are properly handled.
# Version: 20131027

import os, re
import lib_coordinates_mode as cm
import numpy as np

def read_skymodel(skymodel, fields=[]):
    """
    Read a skymodel file (BBS format)
    skymodel -- the skymodel file generated by PyBDSM
    fields -- list of fields to load
    Return:
    numpy array with all the sources in the skymodel
    """
    names = []
    formats = []
    usecols = []
    converters = {}
    filling_values = {}

    f = open(skymodel, 'r')
    header = f.readline()
    # remove useless part of the header
    header = re.sub(r'\s', '', header)
    header = re.sub(r'\)=format', '', header)
    header = re.sub(r'#\(', '', header)
    headers = header.split(',')
    for i, h in enumerate(headers):

        if not h in fields and fields != []: continue

        # if there's a default value, set it and remove it from the header name
        if re.search('=', h):
            default_value = re.sub(r'.*=', '', h).replace('\'','')
            filling_values[i]=default_value 
            h = re.sub(r'=.*', '', h)

        names.append(h)
        usecols.append(i)

        if h == "Ra":
            formats.append(np.float)
            converters[i] = lambda x: cm.hmstora(float(x.split(':')[0]),float(x.split(':')[1]),float(x.split(':')[2])) if x else 0.0

        elif h == "Dec":
            formats.append(np.float)
            converters[i] = lambda x: cm.dmstodec(float(x.split('.')[0]),float(x.split('.')[1]),float(x.split('.')[2])) if x else 0.0

        elif h == "I" or h == "Q" or h == "U" or h == "V" or h == "ReferenceFrequency" or h == "MajorAxis" or h == "MinorAxis" or h == "Orientation":
            formats.append(np.float)
            if not i in filling_values:
                if h == "I": filling_values[i]=1
                else: filling_values[i]=0
            else:
                filling_values[i]=np.float(filling_values[i])

        # note that SpectralIndex also end up as a string with no comma!!
        else:
            formats.append('S100')

    types = np.dtype({'names':names,'formats':formats})

    n = len(types)-1

    # generator
    def fileiter(skymodel, n):
        for line in open(skymodel,'r'):
            # remove comments, patches and white lines
            if line[0] == '#' or line[0] == ',' or len(line) == 1: continue
            #  remove commas inside [] for spidx
            line = re.sub('\(\[.*\),\(.*\]\)', '\1\2', line)
            # add the missing commas at the end of the lines
            n_commas = line.count(',')
            missing_commas = n - n_commas
            yield line+','*missing_commas

    skymodel_data = np.genfromtxt(fileiter(skymodel, n), names=names, comments='#', unpack=True, dtype=formats, delimiter=',', autostrip=True, usecols=usecols, converters=converters, filling_values=filling_values)

    return skymodel_data

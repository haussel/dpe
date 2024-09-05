__author__ = 'haussel'
import numpy as np
import os
import re
from astropy.table import Table

from .config import DPE_INSTALL_DIR, DEBUG
DATA_DIR = os.path.join(DPE_INSTALL_DIR, 'data/')

def get_zone_climatique(departement):
    """
    find the zone climatique of a departement

    Parameter:
    ----------
    departement: str
       the departement code (e.g. '75', '2A', etc...)

    Output:
    -------
    retunrs the zone climatique code.
    """
    found = False
    lines = read_data_file('zones_climatiques.txt')
    m = re.compile('(\d[\dAB]) (\D+) (H\d[abcd]?)')
    for line in lines:
        if line[0] != '#':
            if not found:
                for x in m.finditer(line):
                    if x.group(1) == departement:
                        found = True
                        zc = x.group(3)
    if found:
        return(zc)
            

def read_data_file(filename):
    """
    Read a dpe data file

    Parameters
    ----------
    filename: str
        The name of the file. If the file is not found, the file is
        searched for in the data/ directory of the installation of
        the dpe  package. If more than one is found, an error is raised

    Returns
    -------
    list of lines
    """
    if not os.path.exists(filename):
        result = []
        for root, dirs, files in os.walk(DATA_DIR):
            if filename in files:
                result.append(os.path.join(root, filename))
        if len(result) == 1:
            fullpath = result[0]
        else:
            raise ValueError('could not locate {} filename, found {}'.format(
                filename, result))
    else:
        fullpath = filename

    f = open(fullpath, 'r')
    lines = f. readlines()
    f.close()
    return lines
        
def get_zone_climatique(departement):
    """
    find the zone climatique of a departement

    Parameter:
    ----------
    departement: str
       the departement code (e.g. '75', '2A', etc...)

    Output:
    -------
    retunrs the zone climatique code.
    """
    found = False
    lines = read_data_file('zones_climatiques.txt')
    m = re.compile('(\d[\dAB]) (\D+) (H\d[abcd]?)')
    for line in lines:
        if not found:
            if line[0] != '#':
                for x in m.finditer(line):
                    if x.group(1) == departement:
                        found = True
                        zc = x.group(3)
    if not found:
        result = None
    else:
        result = zc
    return(zc)

def get_tbase(zone_climatique, altitude):
    """
    Implement the second table of section 18.1 of joe_20211014_0240_0034.pdf

    Parameters
    ----------
    zone_climatique: str
    altitude: float

    Returns Tbase, a float
    """
    if zone_climatique[1] == '1':
        if altitude < 400:
            tbase = -9.5
        elif altitude >= 800:
            tbase = -13.5
        else:
            tbase = -11.5
    elif zone_climatique[1] == '2':
        if altitude < 400:
            tbase = -6.5
        elif altitude >= 800:
            tbase = -10.5
        else:
            tbase = -8.5
    elif zone_climatique[1] == '3':
        if altitude < 400:
            tbase = -3.5
        elif altitude >= 800:
            tbase = -7.5
        else:
            tbase = -5.5
    else:
        raise ValueError('Invalid Zone_climatique: {}'.format(zc))
    return(tbase)

def get_E_pv(zone_climatique):
    """
    Implement first table of section 18.2
    """
    t = Table.read(os.path.join(DATA_DIR, 'e_pv.txt'), format='ascii',
                   header_start=1)
    return(t['Mois', zone_climatique])

def get_Text(zone_climatique, altitude):
    if altitude <= 400:
        filename = 'text_b400.txt'
    elif altitude > 800:
        filename = 'text_o800.txt'
    else:
        filename = 'text_b400_800.txt'
    t = Table.read(os.path.join(DATA_DIR, filename), format='ascii',
                   header_start=1)
    return(t['Mois', zone_climatique])

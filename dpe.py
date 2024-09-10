__author__ = 'haussel'
import os
import re
from astropy.table import Table

from .config import DPE_INSTALL_DIR, DEBUG
DATA_DIR = os.path.join(DPE_INSTALL_DIR, 'data/')

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
    if DEBUG:
        print("Reading file:{}".format(fullpath))
    with open(fullpath, 'r') as f:
        lines = f. readlines()
    return lines
        
def get_zone_climatique(departement):
    """
    find the zone climatique of a departement

    Parameter:
    ----------
    departement: str
       the departement code (e.g. '75', '2A', etc...)

    Output: str
    -------
    returns the zone climatique code.
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
    return result

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
        raise ValueError('Invalid Zone_climatique: {}'.format(zone_climatique))
    return tbase

def get_table(variable, altitude, zone_climatique, inertie_haute=False):
    """
    Read a table from section 18.2 and 18.3 of joe_20211014_0240_0034.pdf

    Parameters:
    -----------
    variable: str
        the name of the variable to read. This is the first part of the file name

    altitude: float
        the altitude

    zone_climatique: str
        the zone climatique to extract data for

    inertie_haute: bool
        If true, read the tables from sec 18.3 of buiding with high inertia, otherwize reads the tables from
        section 18.2

    Output: astropy.Table
    -------
        a table with 2 columns, 'Mois' and zone_climatique
    """
    filename = variable
    if inertie_haute:
        filename = 'hi_' + filename
    if (altitude <= 400):
        filename = filename + '_b400.txt'
    elif (altitude >= 800):
        filename = filename + '_a800.txt'
    else:
        filename = filename + '_a400_b800.txt'

    lines = read_data_file(filename)

    if len(lines) < 14:
        raise ValueError('Could not read correctly table {} with len(lines) = {}'.format(filename, len(lines)))
            
    bits = lines[1].split()
    icol = None
    for i, bit in enumerate(bits):
        if bit == zone_climatique:
            if icol is None:
                icol = i-1
            else:
                raise ValueError("Multiple occurences of {}".format(zone_climatique))
    if icol is None:
        raise ValueError("Zone climatique '{}' not found".format(zone_climatique))  
    mok = []
    vok = []
    for i in range(2, 14):
        bits = lines[i].split()
        if bits[icol] != '-':
            vok.append(float(bits[icol]))
            mok.append(bits[0])
    if len(vok) > 0:
        result = Table()
        result['Mois'] = mok
        result[zone_climatique] = vok
    else:
        result = None
        raise Warning('All data undefined for zone climatique {}'.format(zone_climatique))
    return result
    

def get_E_pv(zone_climatique):
    """
    Implement first table of section 18.2
    """
    t = Table.read(os.path.join(DATA_DIR, 'e_pv.txt'), format='ascii',
                   header_start=1)
    return t['Mois', zone_climatique]




def get_c1(zone_climatique, i_incl):
    '''
    Read the coefficients d’orientation et d’inclinaison des parois vitrées section 18.5

    Parameters
    ----------
    zone_climatique: str
    i_incl: int

    Returns:
    astropy.Table
    -------

    '''
    filename =  'coiv_' + zone_climatique.lower() + '.csv'
    lines = read_data_file(filename)

    m_vals = []
    s_vals = []
    o_vals = []
    n_vals = []
    e_vals = []
    for i, line in enumerate(lines):
        if i > 1:
            bits = line.split(',')
            m_vals.append(bits[0])
            s_vals.append(float(bits[i_incl+1]))
            o_vals.append(float(bits[i_incl+4]))
            n_vals.append(float(bits[i_incl+7]))
            e_vals.append(float(bits[i_incl+10]))
    result = Table()
    result['Mois'] = m_vals
    result['Sud'] = s_vals
    result['Ouest'] = o_vals
    result['Nord'] = n_vals
    result['Est'] = e_vals
    return result

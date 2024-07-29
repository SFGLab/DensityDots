#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import re

points = [(1.1, 2.3, 3.4),
          (0.1, 5.3, 4.2),
          (9.2, 4.3, 1.3)]


def pointReader(fname):
    """Read the points from PDB file format
    
        Args:
            fname (string) filename of single chromatine model in pdb file format
        
        Returns:
            (list) List of three floats tuples representing points in euclidean R^3
    """
    atoms = [i.strip() for i in open(fname) if re.search('^(ATOM|HETATM)', i)]
    points = []
    for i in atoms:
        x = float(i[30:38])
        y = float(i[38:46])
        z = float(i[46:54])
        points.append((x,y,z))
    return points


def savePointsAsXYZ(points, filename, fmt='chimera', **kwargs):
    """Przyjmuje liste krotek trzy elementowych i zapisuje je do pliku xyz o nazwie filename

        Args:
            points (list): three elements tuples
            filename (str): self-explanatory
            fmt (str): available formats:
                xyz         3 column tab separetd
                idxyz       4 column tab separated (first column is index)
                chimera     kwargs: molecule_name
    """
    prefix = ''
    atoms = ''
    sufix = ''
    n = len(points)
    if fmt == 'xyz':
        for i in range(n):
            x, y, z = points[i]
            atoms += ('{}\t{}\t{}\n'.format(x, y, z))
    elif fmt == 'idxyz':
        for i in range(n):
            x, y, z = points[i]
            atoms += ('{}\t{}\t{}\t{}\n'.format(i+1, x, y, z))
    elif fmt == 'chimera':
        if kwargs is not None and kwargs.has_key('molecule_name'):
            molecule_name = kwargs['molecule_name']
        else:
            molecule_name = ''
        prefix = '{}\n{}\n'.format(n, molecule_name)
        for i in range(n):
            x, y, z = points[i]
            atoms += ('C\t{}\t{}\t{}\n'.format(x, y, z))
        
    with open(filename, 'w') as f:
        f.write(prefix)
        f.write(atoms)
        f.write(sufix)
    #print "File {} saved...".format(filename)

def savePointsAsPdb(points, filename, verbose=True, connect=True):
    """Przyjmuje liste krotek trzy elementowych i zapisuje je do pliku PDB o nazwie filename"""
    atoms = ''
    n = len(points)
    for i in range(n):
        x = points[i][0]
        y = points[i][1]
        try:
            z = points[i][2]
        except IndexError:
            z = 0.0
        atoms += ('{0:6}{1:>5}  {2:3}{3:}{4:3} {5:}{6:>4}{7:}   {8:8.3f}{9:8.3f}{10:8.3f}{11:6.2f}{12:6.2f}{13:>12}\n'.format("ATOM",i+1,'B',' ','BEA','A', i+1, ' ', x, y, z, 0, 0, 'C'))
    
    connects = ''
    if connect:
        if n != 1:
            connects = 'CONECT    1    2\n'
            for i in range(2,n):
                connects += 'CONECT{:>5}{:>5}{:>5}\n'.format(i, i-1, i+1)
            connects += 'CONECT{:>5}{:>5}\n'.format(n,n-1)
        
    pdbFileContent = atoms + connects
    open(filename, 'w').write(pdbFileContent)
    if verbose:
        print( "File {} saved...".format(filename))
    return filename

def savePointsAsGro(points, filename, comment="komentarz"):
    n = len(points)
    x,y,z = zip(*points)
    d = max(x+y+z)
    l = ["{}\n".format(comment)]
    l.append(str(n)+'\n')
    for i in range(n):
        x = points[i][0]/10
        y = points[i][1]/10
        z = points[i][2]/10
        w = '{:5}{:5}{:5}{:5}{:8.3f}{:8.3f}{:8.3f}\n'.format(i,"BEA","B",i+1,x,y,z)
        l.append(w)
    l.append('{0:5f} {0:5f} {0:5f}'.format(d))
    filename = '{}'.format(filename)
    open(filename, 'w').writelines(l)
    print( "File {} saved...".format(filename))
    return filename

def main():
#    savePointsAsPdb(points, 'mojaStruktura.pdb')
#    savePointsAsGro(points, 'mojaStruktura.gro')
    import sys
    points = pointReader(sys.argv[1])
    savePointsAsXYZ(points, 'model_50kb_c2.pdb')
#    k = float(sys.argv[2])
#    p2 = []
#    for i in points:
#        p2.append((i[0]*k, i[1]*k, i[2]*k))
#    savePointsAsPdb(p2, sys.argv[1]+'.rescaled.pdb')

if __name__ == '__main__':
    main()

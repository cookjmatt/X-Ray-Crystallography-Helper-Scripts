#!/usr/bin/env python
from math import *
import os
from os import system
# Matthew Cook
# Last modified 03/02/2013
# Takes two peaklists in .xpk format and highlights an arbitrary top percentage
#  of shifts and intensities on a corresponding pdb structure

#Modify these values
s1 = 'bard1_ankl_free_200uM.xpk'                  # Original peaklist
s2 = 'bard1_ank_363_555_new.xpk'  # New peaklist (e.g. titration)
pdb_code = '3c5r'                                 # Corresponding pdb code for your structure
top_percent = 0.10                                # Top percent of shifts to highlight in pymol

pymol_path = '/Applications/MacPyMOl.app/Contents/MacOS/MacPyMOL' #Your PyMol path

###############################################################################
# Don't change anything past here
###############################################################################

#Calculate Euclidean shift between two peaks
def shift(h1,h2,n1,n2):
  return sqrt((((float(n1)-float(n2))/5)**2) + ((float(h1)-float(h2))**2))

#Calculate Intensity difference between two peaks
def intensity(i1, i2):
  return (float(i2)/float(i1))

#Calculate mean and std dev of a list
def meanstdv(l):
  n = len(l)
  #Calculate mean
  mean = 0.0
  for i in l:
    mean = (mean + i)
  mean = (mean / float(n))
  #Calculate standard deviation
  std = 0.0
  for i in l:
    std = (std + (i - mean)**2)
  std = sqrt(std / float(n))
  return (mean, std)

#Get peaklist data
with open (s1,'r') as f1:
  d1 = f1.readlines()
f1.closed
with open(s2,'r') as f2:
  d2 = f2.readlines()
f2.closed

#Dictionaries for 1H, 15N, and intensity values as well as residue names
#Lists for shifts and intensities
h1_dict = {}
h2_dict = {}
n1_dict = {}
n2_dict = {}
i1_dict = {}
i2_dict = {}
res_dict = {}
shift_dict = {}
reverse_shift_dict = {}
intensity_dict = {}
reverse_intensity_dict = {}
shift_list = []
top_intensity_list = []

#Get 1H, 15N, and intensity values for each peak in peaklist 1
for i in d1:
  t1 = i.split(' ')
  if (len(t1) == 20):
    h1_dict[t1[0]] = t1[2]  
    n1_dict[t1[0]] = t1[9]
    i1_dict[t1[0]] = t1[16]
    res_dict[t1[0]] = t1[1][1:-1].split('.')[0]

#Get 1H, 15N, and intensity values for each peak in peaklist 2
for i in d2:
  t2 = i.split(' ')
  if (len(t2) == 20):
    h2_dict[t2[0]] = t2[2]
    n2_dict[t2[0]] = t2[9]
    i2_dict[t2[0]] = t2[16]

#Make forward and reverse dictionaries for peak shifts
for i in (set(h1_dict.keys()) & set (h2_dict.keys())):
  shift_dict[i] = shift(h1_dict[i],h2_dict[i],n1_dict[i],n2_dict[i])
for i in shift_dict.keys():
  reverse_shift_dict[shift_dict[i]] = i

#Make forward and reverse dictionaries for peak intensity changes
for i in (set(i1_dict.keys()) & set(i2_dict.keys())):
  intensity_dict[i] = intensity(i1_dict[i],i2_dict[i])
for i in intensity_dict.keys():
  reverse_intensity_dict[intensity_dict[i]] = i

#Make list of peak intensity changes greater than 1 standard deviation from the mean
intensity_list = intensity_dict.values()
intensity_mean = meanstdv(intensity_list)[0]
intensity_stdv = meanstdv(intensity_list)[1]
for i in intensity_list:
  if ((i < (intensity_mean - 0.5*intensity_stdv)) or (i > (intensity_mean + 0.5*intensity_stdv))):
    top_intensity_list.append(i)

#Make string for PyMol command highlighting top intensity changes
pymol_intensity_string = 'cmd.select(\'top_intensities\', \'resi '
for i in top_intensity_list:
  pymol_intensity_string += res_dict[reverse_intensity_dict[i]]
  pymol_intensity_string += '+'
pymol_intensity_string = pymol_intensity_string[:-1]+'\')\n'

#Make sorted list of shifts from greatest to least and a list of top shifts
shift_list = shift_dict.values()
shift_list.sort()
shift_list.reverse()
top_shifts = int(len(shift_list) * top_percent)

#Make string for PyMol command highlighting top shifts
pymol_string = 'cmd.select(\'top_shifts\', \'resi '
for i in range(0,top_shifts):
  pymol_string += res_dict[reverse_shift_dict[shift_list[i]]]
  pymol_string += '+'
pymol_string = pymol_string[:-1]+'\')\n'

#Write pymol script and save as 'temp_script.txt'
with open('temp_script.txt','w') as out_file:
  out_file.write('from pymol import cmd\n')
  out_file.write(str('cmd.fetch(\''+pdb_code+'\')\n'))
  out_file.write(str(pymol_string[:-1]+'\n'))
  out_file.write(str('cmd.show(\'surface\', \''+pdb_code+'\')\n'))
  out_file.write(str('cmd.color(\'green\', \''+pdb_code+'\')\n'))
  out_file.write(str('cmd.color(\'red\', \'top_shifts\')\n')) 
  out_file.write(str('cmd.show(\'cartoon\', \''+pdb_code+'\')\n'))
  out_file.write(str('cmd.hide(\'lines\', \''+pdb_code+'\')\n'))  
  out_file.write(str('cmd.set(\'transparency\', \'0.4\')\n'))
  out_file.write(str('cmd.remove(\'solvent\')\n'))
  out_file.write(str('cmd.deselect()\n'))
  out_file.write(str(pymol_intensity_string))
  out_file.write(str('cmd.color(\'blue\', \'top_intensities\')\n'))
  out_file.write(str('cmd.deselect()'))
out_file.closed

#Open pymol with 'temp_script.txt'
os.system(str(pymol_path+' -r temp_script.txt'))

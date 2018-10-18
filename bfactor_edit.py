#!/usr/bin/ python

from sys import argv

#Read in PDB
with open(argv[1],'r') as in_file:
  data = in_file.readlines()
in_file.closed

#Read in fractional intensity data
with open(argv[2],'r') as in_file:
  int_data = in_file.readlines()
in_file.closed

#Make array of (Residue Number, Fractional Intensity)
int_list = []
for i in int_data:
  temp_array = i.split()
  int_list.append((int(temp_array[0]),temp_array[1]))

#Replace b-factors with fractional intensity data
with open(str('edited_'+str(argv[1])),'w') as out_file:
  for i in data:
    if not(i[:4] == 'ATOM'):
      out_file.write(i)
    else:
      temp_line = i
      residue_number = int(i[23:27])
      chain = i[21]
      if (chain == 'B'):
        residue_number = residue_number+200 
      fract_int = '1.000'
      for j in int_list:
        if (j[0] == residue_number):
          fract_int = j[1][:5]
      final_line = temp_line[:61]+fract_int+temp_line[67:] 
      out_file.write(final_line)
out_file.closed

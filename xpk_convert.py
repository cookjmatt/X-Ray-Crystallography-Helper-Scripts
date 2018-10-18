# here are where your input files are defined
chsqcfile = open('cryab_ponni_chsqc.xpk','w')
nhsqcfile = open('cryab_ponni_nhsqc.xpk','w')
cshfile = open('chsqc_cryab_acd.out', 'r')

# do not modify below this point (unless debugging/improving code)
peakref = {}

import re

#this fills the cshfile dictionary (key is atom pair, values are ppms)
for line in cshfile:
	linevalues = line.split()
	atomvalues = linevalues[0].split('.')
	if atomvalues[1] == "C":
		peakref[atomvalues[0]+atomvalues[1]] = float(linevalues[1])
	elif atomvalues[1] == "N":
		n_atom = atomvalues[1]
		n_ppm = float(linevalues[1])
	elif atomvalues[1] == "HN":
		peakref[atomvalues[0]+n_atom+atomvalues[1]] = [float(linevalues[1]), n_ppm]
	elif re.search(r'C',atomvalues[1]):
		c_atom = atomvalues[1]
		c_ppm = float(linevalues[1])
	elif re.search(r'N',atomvalues[1]):
		n_atom = atomvalues[1]
		n_ppm = float(linevalues[1])
	else:
		try:
			if n_atom[1] == atomvalues[1][1]:
				peakref[atomvalues[0]+n_atom+atomvalues[1]] = [float(linevalues[1]), n_ppm]
		except:
			peakref[atomvalues[0]+c_atom+atomvalues[1]] = [float(linevalues[1]), c_ppm]
cshfile.close()		

print peakref

#writing the xpk files
chsqcfile.write("label dataset sw sf\n")
chsqcfile.write("HC C\n")
chsqcfile.write("CHSQC.mat\n")
chsqcfile.write("6009.61523437 10060.3623047\n")
chsqcfile.write("500.131988525 125.763000488\n")
chsqcfile.write("HC.L HC.P HC.W HC.B HC.E HC.J HC.U C.L C.P C.W C.B C.E C.J C.U vol int stat comment flag0\n")
nhsqcfile.write("label dataset sw sf\n")
nhsqcfile.write("HN N\n")
nhsqcfile.write("NHSQC.mat\n")
nhsqcfile.write("3004.80761719 1216.39697266\n")
nhsqcfile.write("500.131988525 50.6839981079\n")
nhsqcfile.write("HN.L HN.P HN.W HN.B HN.E HN.J HN.U N.L N.P N.W N.B N.E N.J N.U vol int stat comment flag0\n")
ncount = 0
ccount = 0
for peak in peakref.keys():
	try:
		a = peakref[peak][0]
		if re.search(r'N', peak):
			nhsqcfile.write(str(ncount))
			nhsqcfile.write(" {")
			hn_flag = 0
			n_flag = 0
			
			#this writes the HN-label in the xpk file
			for char in peak:
				if char.isdigit() and n_flag == 0:
					nhsqcfile.write(str(char))
				elif char == "H":
					hn_flag = 1
					nhsqcfile.write(".")
					nhsqcfile.write(str(char).lower())
				elif hn_flag == 1:
					nhsqcfile.write(str(char).lower())
				else:
					n_flag = 1
			nhsqcfile.write("} ")
			
			#this writes the peak location in the HN-plane
			nhsqcfile.write(str(peakref[peak][0]))
			nhsqcfile.write(" 0.1 0.1 ++ {0.0} {} {")
			
			#this writes the N-label in the xpk file
			for char in peak:
				if char.isdigit():
					nhsqcfile.write(str(char))
				elif char == "N":
					nhsqcfile.write(".")
					nhsqcfile.write(str(char).lower())
				elif char == "H":
					break
				else:
					nhsqcfile.write(str(char).lower())
			nhsqcfile.write("} ")
					
			#this writes the peak location in the N-plane
			nhsqcfile.write(str(peakref[peak][1]))
			nhsqcfile.write(" 0.50 0.50 ++ {0.0} {} 0.0 1.0000 0 {} 0\n")
			ncount+=1
		else:
			chsqcfile.write(str(ccount))
			chsqcfile.write(" {")
			hc_flag = 0
			c_flag = 0
			
			#this writes the HC-label in the xpk file
			for char in peak:
				if char.isdigit() and c_flag == 0:
					chsqcfile.write(str(char))
				elif char == "H":
					hc_flag = 1
					chsqcfile.write(".")
					chsqcfile.write(str(char).lower())
				elif hc_flag == 1:
					chsqcfile.write(str(char).lower())
				else:
					c_flag = 1
			chsqcfile.write("} ")
			
			#this writes the peak location in the HC-plane
			chsqcfile.write(str(peakref[peak][0]))
			chsqcfile.write(" 0.1 0.1 ++ {0.0} {} {")
			
			#this writes the C-label in the xpk file
			for char in peak:
				if char.isdigit():
					chsqcfile.write(str(char))
				elif char == "C":
					chsqcfile.write(".")
					chsqcfile.write(str(char).lower())
				elif char == "H":
					break
				else:
					chsqcfile.write(str(char).lower())
			chsqcfile.write("} ")
			
			#this writes the the peak location in the C-plane
			chsqcfile.write(str(peakref[peak][1]))
			chsqcfile.write(" 0.50 0.50 ++ {0.0} {} 0.0 1.0000 0 {} 0\n")
			ccount+=1
	except:
		#because carbonyls only have C-assignments (1 value), any list references are errors
		print "Carbonyl ignored"
chsqcfile.close()
nhsqcfile.close()
		

#--------------------------------------------------------------------##
#		Start, end latex doc
#--------------------------------------------------------------------##
def StartLatexDoc(outfile):
	header0 = "\documentclass[10pt]{article} \n\\usepackage{booktabs} \n\\usepackage{geometry} \n\\geometry{verbose,letterpaper,lmargin=0.5in,rmargin=0.5in,tmargin=1in,bmargin=1in} \n\\begin{document}  \n" 
	print >>outfile, header0

def EndLatexDoc(outfile):
	footer = "\\end{document}"
	print >>outfile, footer
	outfile.close()
	
#--------------------------------------------------------------------##
#		Make latex table
#--------------------------------------------------------------------##
def MakeLatexFile(outfile, headers, datalines):
	"""
	When there are datalines that begin with a #, contain a single character
	as their second item, then that second item will be replaced
	by the third. This allows an easy conversion to latex specifications.	
	"""
	tablelines = list()
	printlines = list()
	longestitem = 1
	numberofcolumns = len(headers)+1
	translations = dict()
	translations["NULL"] = "\\emptyset"
	header1 = "\\begin{centering}\n"
	header2 = "\\begin{tabular}{" 
	header3 = "\\toprule "
	footer1 = "\\end{tabular}"
	footer2 = "\\end{centering}\n"
	
	for line in datalines:
		if line[0] == "#":
			if len(line) == 3 and len(line[1]) == 1:
				translations[line[1]] = line[2]
		else:
			linelist = list()
			if len(line) > numberofcolumns:
				numberofcolumns = len(line)
			for item in line:
				for a in item:
					if a in translations:
						item.replace(a,translations[a])
				if len(item) > longestitem:
					longestitem = len(item)
				linelist.append(item)
			tablelines.append(linelist)
		print (52, linelist)
	print (header1, file=outfile)
	print (header2,'l'*numberofcolumns, "}",  header3,file=outfile)

	# Calculate length of items in  the top header line:
	redone_words = list()
	thisline = list()
	thisline.append("")
	for word in headers:
		for a in word:
			if a in translations:
				word.replace(a,translations[a])
			if len(word) > longestitem:
				longestitem = len(word)
		redone_words.append(word)
		thisline.append(word)

	# if an item in a line is of the form "a:b", then it will generate \frac{a}{b} 
	for m in range(len(tablelines)):	
		thisline = list()
		line = tablelines[m]
		#print word in first column:
		thisline.append(redone_words[m]) 
		for n in range(len(line)): 
			field = line[n]
			if field == "@":
				thisline.append("")	
			elif len(field.split(":")) == 2:
				fraction = field.split(":")
				field = "$\\frac{" + fraction[0] + "}{" + fraction[1] + "}$"
				thisline.append(field)
			else:			
				thisline.append(field)
			if len(field) > longestitem:
				longestiem = len(field)
		printlines.append(thisline)
		for wordno in range(len(redone_words)):
			thisword = redone_words[wordno]
		print >>outfile, " & " + thisword + " "*(longestitem - len(thisword)) ,
	print ("\\\\ \\midrule",file=outfile)
				
	for line in printlines:
		for no in range(len(line)):
			item = line[no]
			print >>outfile, item, 
			if no < len(line) -1:
				print >>outfile, "&",
		print (  "\\\\",file=outfile)
			
	print ("\\bottomrule", "\n",file=outfile)
	print ( footer1,file=outfile)
	print ( footer2,file=outfile)
	print ("\\vspace{.4in}",file=outfile)

	

 
# ----------------------------------------------------------------------------------------------------------------------------#
def signatures_to_latex(signatures):
    outlist = list()
    header1 = "\\documentclass[10pt]{article}" 
    header2 = "\\usepackage{booktabs}" 
    header3 = "\\usepackage{geometry}" 
    header4 = "\\usepackage{longtable}" 
    header5 = "\\geometry{verbose,letterpaper,lmargin=0.5in,rmargin=0.5in,tmargin=1in,bmargin=1in}"
    header6 = "\\begin{document} "
    starttab = "\\begin{longtable}{lllllllllll}"
    endtab = "\\end{longtable}"

    print ("   Printing signature file in latex.")
    running_sum = 0.0
    outlist.append(header1) 
    outlist.append(header2) 
    outlist.append(header3) 
    outlist.append(header4)            
    outlist.append(header5)
    outlist.append("\n" + header6)
    outlist.append("\n" + starttab)
    outlist.append("Signature & Stem count & Robustness & Proportion of robustness\\\\ \\toprule")
 
    total_robustness = 0.0
    for sig in signatures:
    	total_robustness += sig.robustness
    colwidth = 20
    sigs = sorted(signatures, key = lambda x: x.robustness, reverse=True)
    count = 1
    for sig in sigs:
        # ADD EXAMPLE STEM, running total of robustness
        sig_string = sig.affix_string
        sig_length = len(sig_string)
        stem_count = sig.stem_count
        running_sum += sig.robustness
        rob_prop = float(sig.robustness) / total_robustness
        running_sum_proportion = running_sum / total_robustness
        string1 =  str(count) + ": " +  sig_string + " "*(colwidth-sig_length) + "&"  
        string2 =  str(stem_count()) + "&" +  str( sig.robustness) + "&"
        string3 =  "{0:2.3f}".format(rob_prop) + "\\\\"
        outlist.append( string1  +  string2 + string3)
        count += 1
    outlist.append(endtab)

    number_of_stems_per_line = 6
    stemlist = []
    outlist.append("\n")
    for sig in sigs:
        outlist.append(starttab)
        outlist.append(sig.affix_string + "\\\\ \\hline")
        n = 0
        stemlist = list(sig.stems)
        stemlist.sort()
        numberofstems = len(stemlist)
        column_width = max([len(w) for w in stemlist])
        for stem in stemlist:
            n += 1
            outlist.append(stem + " "*(column_width-len(stem)) + " & ")
            if n % number_of_stems_per_line == 0:
                outlist.append("\\\\")
        outlist.append(endtab +  "\n\n\n\n")
        outlist.append("\n")    
    outlist.append("\\end{document}")	
    return outlist


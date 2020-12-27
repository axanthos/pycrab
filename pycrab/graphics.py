

import math

def start_an_html_file(outlist):
        outlist.append("<!DOCTYPE html>")
        outlist.append("<html>")
        outlist.append("<head>")
        outlist.append("<link rel=\"stylesheet\" href=\"style.css\">")
        outlist.append("</head>")
        outlist.append("<body>")

def     end_an_html_file(outlist):
        outlist.append("</body>")
        outlist.append("</html>")

 

        
def start_an_html_table(outfile):
        outlist.append("<table>")

def end_an_html_table(outfile):
        outlist.append("</table>")

def start_an_html_table_row(outfile):
        outlist.append("<tr>")

def end_an_html_table_row(outfile):
        outlist.append("</tr>")

def start_an_html_div(outlist, class_type=""):
   outlist.append("\n\n<div class=\""+ class_type + "\">")

def end_an_html_div(outlist):
   outlist.append("\n</div>")

def add_an_html_table_entry(outlist,item):
   outlist.append("<td>{0:1s}</td>".format(item))

def add_an_html_header_entry(outlist,item):
   outfile.append("<th>{0:1s}</th>".format(item))

def stemcount(sig):
    return len(sig.stems)

def import_to_page_then_display_signatures_as_svg (signature_list):  
    this_page = Page()
    this_page.import_signatures_to_page(signature_list)
    return (this_page.display_signatures_as_svg())

 
class Page:
    """ A class for creating svg-based html files for graphic 
    representations of signature lattices.

    Points on the screen can be identified either as coordinates
    in the usual sense, or else as (row, col) coordinates in the
    signature lattice. 

    The keys of self.row are dicts, with keys the row-numbers.
    Each self.row[row-number] is a dict, whose key is a column-number.
    Each self.row[row-number][column-number] is a signature.

    """
    def __init__(self):

        self.my_height=2000
        self.my_width=20000
        self.my_column_width = 250
        self.my_row_height = 200
        self.row = dict() # key is row number, value is dict; the latter's values are signatures.

## Note that many of these ** do not need to be members of this class **
#    def start_an_html_file(self, outlist):
    def start_an_svg_file(self, outlist):
        string1 = "<svg width=\"{0:2d}\" height=\"{1:2d}\">\n"
        outlist.append(string1.format(self.my_width,self.my_height))

    def end_an_svg_file(self,outlist):
        outlist.append ("</svg>")

    def print_signature (self,outlist,sigstring, rowno, colno,stem_count  ):
        outlist.append( self.print_circle(outlist, rowno,colno,stem_count) )
        outlist.append( self.print_text(outlist,sigstring ,rowno, colno, sigstring) )

    def import_signatures_to_page (self,signature_list):    
        outlist = list()
        #print (84, len(signature_list))
        signature_list.sort(key=lambda sig:sig.stem_count(), reverse=True) # was: key = stemcount
        for sig in signature_list:
                #print (87, sig.affix_string)
                row_no= sig.affix_count()
                col_no = 0
                if row_no not in self.row:
                    self.row[row_no] = dict()
                else:
                    col_no = len(self.row[row_no])
                self.row[row_no][col_no] = sig
                #print ("row no", row_no, "\n\tcol_no", col_no, sig.affix_string)
        return outlist

    def display_signatures_as_svg (self):    
        outlist = list()
        start_an_html_file(outlist)
        self.start_an_svg_file(outlist)
        maxrow = max(list(self.row.keys()))
        print (103, "max row", maxrow)
        for row_no in range(maxrow):
            if row_no not in self.row:
                continue
            for col_no in range(len(self.row[row_no])):
                this_sig = self.row[row_no][col_no]
                sigstring = this_sig.affix_string
                stem_count = len(this_sig.stems)
                robustness = this_sig.robustness
                outlist.append(self.print_signature (outlist, sigstring, row_no, col_no, stem_count))
                #print (114, "Row: ", row_no, "\nCol number:", col_no, sigstring,)                
        self.end_an_svg_file(outlist)
        end_an_html_file(outlist)
        print (111,)
        return outlist
 
    def print_text(self,outlist, sigstring, rowno,colno,text):
        (x,y) = self.coor_from_row_col(rowno,colno)
        row_factor = 0.10
        y += self.my_row_height * row_factor + 10
        number_of_affixes = 0
        outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">"
        outstring2 = "</text>\n"
        sig_list = list()
        if len(text) < 15:
            outlist.append(outstring1.format(x,y) + text + outstring2)
        else:
            text_height = self.my_row_height * row_factor
            sig_list = sigstring.split("=")
            number_of_affixes = len(sig_list)
            if  len(text)<30:
                    half = int(number_of_affixes / 2)
                    first_line_list = sig_list[0:half]
                    second_line_list = sig_list[half:number_of_affixes]
                    outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">\n"
                    outstring2 = "</text>\n"
                    outlist.append(outstring1.format(x,y) + "=".join(first_line_list) + outstring2)
                    outlist.append(outstring1.format(x,y + text_height) + "=".join(second_line_list) + outstring2)
            else:
            	    third = int(number_of_affixes/3)
            	    first_line_list = sig_list[0:third]
            	    second_line_list = sig_list[third:2 * third]
            	    third_line_list = sig_list[2*third:number_of_affixes]
            	    outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">\n"
            	    outstring2 = "</text>\n"
            	    outlist.append(outstring1.format(x,y) + "=".join(first_line_list) + outstring2)
            	    outlist.append(outstring1.format(x,y + text_height) + "=".join(second_line_list) +outstring2)
            	    outlist.append(outstring1.format(x,y + 2* text_height) + "=".join(third_line_list) + outstring2)

    def coor_from_row_col (self, rowno, colno):
        LEFT_MARGIN = 100
        x = self.my_column_width * (colno) + LEFT_MARGIN
        y = self.my_height - self.my_row_height * (rowno)
        return (x,y)

    def print_circle (self, outlist, rowno,colno, stem_count = 10):
        outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">"
        outstring2 = "</text>\n"
        (xcoord,ycoord) = self.coor_from_row_col (rowno, colno)
        if stem_count == 1:
          circle_string =  "<circle cx=\"{0:3d}\" cy=\"{1:3d}\" r=\"{2:1d}\"  stroke=\"black\" stroke-width=\"3\" fill=\"red\" />\n"
          radius=1
          outlist.append( circle_string.format(xcoord,ycoord,radius) )
        else:
          circle_string =  "<circle cx=\"{0:3d}\" cy=\"{1:3d}\" r=\"{2:1f}\"  stroke=\"black\" stroke-width=\"3\" fill=\"red\" />\n"
          radius=10 * math.log(stem_count)
          outlist.append( circle_string.format(xcoord,ycoord,radius) )
        outlist.append(outstring1.format(xcoord,ycoord) + str(stem_count) + outstring2)


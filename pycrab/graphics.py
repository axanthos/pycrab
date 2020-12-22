import math

def start_an_html_file(outlist):
        outlist.append("<!DOCTYPE html>\n")
        outlist.append("<html>\n")
        outlist.append("<head>\n")
        outlist.append("<link rel=\"stylesheet\" href=\"style.css\">\n")
        outlist.append("</head>\n")
        outlist.append("<body>\n")


def     end_an_html_file(outlist):
        outlist.append("</body>\n")
        outlist.append("</html>\n")
        

def start_an_html_table(outfile):
        outlist.append("<table>\n")

def end_an_html_table(outfile):
        outlist.append("</table>")

def start_an_html_table_row(outfile):
        outlist.append("<tr>\n")

def end_an_html_table_row(outfile):
        outlist.append("</tr>\n")


def start_an_html_div(outlist, class_type=""):
   outlist.append("\n\n<div class=\""+ class_type + "\">\n")

def end_an_html_div(outlist):
   outlist.append("\n</div>\n")

def add_an_html_table_entry(outlist,item):
   outlist.append("<td>{0:1s}</td>\n".format(item))

def add_an_html_header_entry(outlist,item):
   outfile.append("<th>{0:1s}</th>\n".format(item))



def stemcount(sig):
    return len(sig.stems)

def display_signatures_as_svg (signature_list):    
    this_page = Page()
    outlist = list()
    signature_list = sorted(signature_list, key=stemcount, reverse=True)
    this_page.start_an_html_file(outlist)
    column_counts = dict();
    for signo in range(len(signature_list)):
            this_sig = signature_list[signo]
            sigstring = this_sig.affix_string
            stem_count = len(this_sig.stems)
            robustness = this_sig.robustness
            row_no= this_sig.count("=")+1
            if row_no not in column_counts:
                column_counts[row_no] = 1
            else:
                column_counts[row_no] += 1
            col_no = column_counts[row_no]
            radius_guide = stem_count * row_no
            outlist.append(this_page.print_signature (outlist, sigstring,   row_no, col_no, stem_count))
    this_page.end_an_svg_file(outlist)
    end_an_html_file(outlist)
    return outlist
 
class Page:
    """ A class for creating svg-based html files for graphic 
    representations of signature lattices.

    Points on the screen can be identified either as coordinates
    in the usual sense, or else as (row, col) coordinates in the
    signature lattice. 

    """
    def __init__(self):

        self.my_height=2000
        self.my_width=20000
        self.my_column_width = 250
        self.my_row_height = 200

    def start_an_html_file(self, outlist):
        start_an_html_file(outlist)
        string1 = "<svg width=\"{0:2d}\" height=\"{1:2d}\">\n"
        outlist.append(string1.format(self.my_width,self.my_height))
        #return outlist

    def end_an_svg_file(self,outlist):
        outlist.append ("</svg>\n")
        #return outlist 

    def print_signature (self,outlist,sigstring, rowno, colno,stem_count  ):
        outlist.append( self.print_circle(outlist, rowno,colno,stem_count) )
        outlist.append( self.print_text(outlist,sigstring ,rowno, colno, sigstring) )

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
        x = self.my_column_width * (colno)
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
          radius=5 * math.log(stem_count)
          outlist.append( circle_string.format(xcoord,ycoord,radius) )
        outlist.append(outstring1.format(xcoord,ycoord) + str(stem_count) + outstring2)


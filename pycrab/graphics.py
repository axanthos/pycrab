def display_signatures_as_svg (signature_list):    
    this_page = Page()
    signature_list = sorted(signature_list, lambda x, y: cmp(x[2], y[2]), reverse=True)
    this_page.start_an_html_file(outfile_html)
    column_counts = dict();
    for signo in range(len(signature_list)):
            this_sig = signature_list[signo]
            sig = this.sig.__str__
            stem_count = len(this_sig.stems)
            robustness = this_sig.get_robustness
            row_no= sig.count("=")+1
            if row_no not in column_counts:
                column_counts[row_no] = 1
            else:
                column_counts[row_no] += 1
            col_no = column_counts[row_no]
            radius_guide = stem_count * row_no
            this_page.print_signature (outfile_html, sig, radius_guide, row_no, col_no, stem_count)
    this_page.end_an_html_file(outfile_html)
    outfile_html.close()


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
        #self.Node_dict = dict()
        #self.Arrow_dict = dict()

    def add_arrow(self, outfile, from_node, to_node):
        from_row, from_column = self.Node_dict[from_node]
        to_row, to_column     = self.Node_dict[to_node]
        arrow_code = "<line x1=\"" + {0:d} + "\ y1 = \"" + {1:d} + "\" x2=\"" + {2:d} + "\"y2 = \"" +{3:d} + "\" style=\"strike:rgb(255,0,0); stroke-width:2\" />"
        outfile.write(arrow_code)

    def start_an_html_file(self, outfile):
        start_an_html_file(outfile)
        string1 = "<svg width=\"{0:2d}\" height=\"{1:2d}\">\n"
        outfile.write(string1.format(self.my_width,self.my_height))
        return outfile

    def end_an_html_file(self,outfile):
        outfile.write("</svg>\n")
        end_an_html_file(outfile)

    def print_text(self,outfile,rowno,colno,text):
        (x,y) = self.coor_from_row_col(rowno,colno)
        row_factor = 0.10
        y += self.my_row_height * row_factor + 10
        outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">"
        outstring2 = "</text>\n"
        if len(text) < 15:
            outfile.write(outstring1.format(x,y) + text + outstring2)
        else:
    	    text_height = self.my_row_height * row_factor
    	    sig_list = text.split("=")
    	    number_of_affixes = len(sig_list)
        if  len(text)<30:
                half = number_of_affixes / 2
                first_line_list = sig_list[0:half]
                second_line_list = sig_list[half:number_of_affixes]
                outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">\n"
                outstring2 = "</text>\n"
                outfile.write(outstring1.format(x,y) + "=".join(first_line_list) + outstring2)
                outfile.write(outstring1.format(x,y + text_height) + "=".join(second_line_list) + outstring2)
        else:
        	    third = number_of_affixes/3
        	    first_line_list = sig_list[0:third]
        	    second_line_list = sig_list[third:2 * third]
        	    third_line_list = sig_list[2*third:number_of_affixes]
        	    outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">\n"
        	    outstring2 = "</text>\n"
        	    outfile.write(outstring1.format(x,y) + "=".join(first_line_list) + outstring2)
        	    outfile.write(outstring1.format(x,y + text_height) + "=".join(second_line_list) +outstring2)
        	    outfile.write(outstring1.format(x,y + 2* text_height) + "=".join(third_line_list) + outstring2)

    def coor_from_row_col (self, rowno, colno):
        x = self.my_column_width * (colno)
        y = self.my_height - self.my_row_height * (rowno)
        return (x,y)

    def print_circle (self, outfile, rowno,colno, count = 10,stem_count = 10):
        outstring1 = "<text x=\"{}\" y=\"{}\" font-family=\"Verdana\" text-anchor=\"middle\" font-size=\"20\">"
        outstring2 = "</text>\n"
        (xcoord,ycoord) = self.coor_from_row_col (rowno, colno)
        if count == 1:
          circle_string =  "<circle cx=\"{0:3d}\" cy=\"{1:3d}\" r=\"{2:1d}\"  stroke=\"black\" stroke-width=\"3\" fill=\"red\" />\n"
          radius=1
          outfile.write( circle_string.format(xcoord,ycoord,radius) )
        else:
          circle_string =  "<circle cx=\"{0:3d}\" cy=\"{1:3d}\" r=\"{2:1f}\"  stroke=\"black\" stroke-width=\"3\" fill=\"red\" />\n"
          radius=5 * math.log(count)
          outfile.write( circle_string.format(xcoord,ycoord,radius) )
        outfile.write(outstring1.format(xcoord,ycoord) + str(stem_count) + outstring2)

    def print_signature (self,outfile,text, count, rowno, colno,stem_count  ):
        self.print_circle(outfile, rowno,colno,count,stem_count)
        self.print_text(outfile,rowno, colno, text)
 
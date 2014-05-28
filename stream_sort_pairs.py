from optparse import OptionParser
import pysam
import pdb

def fetch_all(b):
    for l in b.fetch(until_eof=True):
        yield l
        
class pairing_window(object):

    def __init__(self,wnd_size=100000):
        self.curr_contig = None
        self.wnd_size = wnd_size
        self.wnd_start = None
        self.wnd_end = None
        self.reads_by_pos = {}
        self.reads_by_name = {}
    
    def clean_up_all(self):
        del self.reads_by_pos
        del self.reads_by_name
        self.reads_by_pos = {}
        self.reads_by_name = {}
        
    def update_wnd(self, e_pos):
        self.wnd_end = e_pos
        while self.wnd_end - self.wnd_start >self.wnd_size:
            if self.wnd_start in self.reads_by_pos:
                for read in self.reads_by_pos[self.wnd_start]:
                    del self.reads_by_name[read.qname]
                del self.reads_by_pos[self.wnd_start]
            self.wnd_start+=1
        
    def add_read(self, read):
        """
        reset 
        """
        if read.rname != self.curr_contig:
            self.clean_up_all()
            self.curr_contig = read.rname
            self.wnd_start = read.pos
            self.wnd_end = read.pos+self.wnd_size
        
        if read.qname in self.reads_by_name:
            """
            ouput read
            """
            print self.reads_by_name[read.qname]
            print read
            #del self.reads_by_name[read.qname]
        else:
            """
            add read 
            """
            self.reads_by_name[read.qname] = read
            if not read.pos in self.reads_by_pos:
                self.reads_by_pos[read.pos] = []
            self.reads_by_pos[read.pos].append(read)
        
        if read.pos > self.wnd_end:
            self.update_wnd(read.pos)


if __name__=="__main__":

    opts = OptionParser()
    opts.add_option('','--input_bam',dest='fn_bam')
    opts.add_option('','--window',dest='window', default=1000, type = int)
    (o, args) = opts.parse_args()

    b = pysam.Samfile(o.fn_bam,'rb')
    
    pairing_obj = pairing_window() 
    for read in fetch_all(b):
        pairing_obj.add_read(read)



#!/usr/bin/env python

"""
Processes merged sequencing data from Illumina MiSeq

Created 15 July 2013
Updated 30 August 2013

Copyright 2013 Michael Ting
https://github.com/michaelting
Released under the BSD 2-clause license. See LICENSE.
http://opensource.org/licenses/BSD-2-Clause

Merged data was produced using SeqPrep on the forward and reverse
reads from Illumina MiSeq. Reads are merged together into single
reads for greater accuracy and are stripped of adapter sequences.
"""

import parse_fastq
import ASCIIcodons
import os, re, errno, gzip, time

class Counter(dict):
    """
    Counts the number of items placed into dictionary buckets.
    Values are initialized to 0.
    Counter class adapted from Pacman AI projects at UC Berkeley, CS188
    """
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)
        
    def argMax(self):
        """
        Returns the key with the highest value
        """
        if len(self.keys()) == 0:
            return None
        allitems = self.items()
        values = [v[1] for v in allitems]
        maxIndex = values.index(max(values))
        return allitems[maxIndex][0]
        
    def sortedKeys(self):
        """
        Returns a list of keys sorted by their values. 
        Keys with the highest values appear first.
        """
        sortedItems = self.items()
        compare = lambda x,y: sign(y[1] - x[1])
        sortedItems.sort(cmp=compare)
        return [x[0] for x in sortedItems]
        
    def totalCount(self):
        """
        Returns the sum of the counts for all keys.
        """
        return sum(self.values())
        
    def copy(self):
        """
        Returns a copy of the counter
        """
        return Counter(dict.copy(self))
        
def sign(x):
    """
    Returns 1 or -1 depending on the sign of x
    """
    if(x >= 0):
        return 1
    else:
        return -1
        
"""
def sort_oligos(parser, tfunc, treepath):
    
    #Creates a directory tree with oligos sorted by person ID and oligo ID numbers
    #in the given treepath
    
    
    TAGLEN = 28  
    
    # try creating directories, if they already exist ignore the error
    try:
        os.makedirs(treepath)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    
    badcharpattern  = re.compile('[^ACGT]')
    tagpattern      = re.compile('TGTC[ACGT]{8}TGAT[ACGT]{12}')
    tagformat       = re.compile('#\d{2}\$\d{3}')
    
    # look at each read in the sequencing file
    for rec in parser:
        
        seqhead     = rec[0].strip()    # header
        seqdna      = rec[1].strip()    # dna sequence
        
        # if sequence contains non-ATGC characters, skip it
        findbadchars = badcharpattern.search(seqdna)
        
        if findbadchars:
            continue
        
        # search for starting point of information
        findtag = tagpattern.search(seqdna)

        # exclue bad tags
        if not findtag:
            continue
        
        # check that tag is translated into correct format
        tagcheck = tfunc(findtag.group())
        checkformat = tagformat.match(tagcheck)
        # exclude bad tags found in translation
        if not checkformat:
            continue
        infostart = findtag.start()
        
        # correct the reading frame
        seqdna = seqdna[infostart:]

        # cap maximum length
        if len(seqdna) > 104:
            seqdna = seqdna[:104]
        
        # if length is not divisible by 4, throw it out
        # occurs for sequences shorter than maximum length
        if (len(seqdna) % 4) != 0:
            continue
        
        # check the tag of the sequence       
        tagdna  = seqdna[:TAGLEN]
        msgdna  = seqdna[TAGLEN:]
        person  = tagdna[4:12]
        oligo   = tagdna[16:28]        
        
        pid     = tfunc(person)
        oid     = tfunc(oligo)

        # create storage for person if person not found
        persondir = treepath + "/" + pid
                
        try:
            os.makedirs(persondir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # create base consensus dict for oligo if oligo not found
        oligodir = persondir + "/" + oid + ".txt"

        try:
            newfile = open(oligodir, "a")
            newfile.write(msgdna+"\n")      # write only the message
            newfile.close()
        except:
            raise
"""

def ram_sort(parser, tfunc):
    
    TAGLEN = 28
    
    badcharpattern  = re.compile('[^ACGT]')
    tagpattern      = re.compile('TGTC[ACGT]{8}TGAT[ACGT]{12}')
    tagformat       = re.compile('#\d{2}\$\d{3}')
    
    #initialize RAM storage

    ramdict = {}
    
    # look at each read in the sequencing file
    for rec in parser:
        
        seqhead     = rec[0].strip()    # header
        seqdna      = rec[1].strip()    # dna sequence
        
        # if sequence contains non-ATGC characters, skip it
        findbadchars = badcharpattern.search(seqdna)
        
        if findbadchars:
            continue
        
        # search for starting point of information
        findtag = tagpattern.search(seqdna)

        # exclue bad tags
        if not findtag:
            continue
        
        # check that tag is translated into correct format
        tagcheck = tfunc(findtag.group())
        checkformat = tagformat.match(tagcheck)
        # exclude bad tags found in translation
        if not checkformat:
            continue
        infostart = findtag.start()
        
        # correct the reading frame
        seqdna = seqdna[infostart:]

        # cap maximum length
        if len(seqdna) > 104:
            seqdna = seqdna[:104]
        
        # if length is not divisible by 4, throw it out
        # occurs for sequences shorter than maximum length
        if (len(seqdna) % 4) != 0:
            continue
        
        # check the tag of the sequence       
        tagdna  = seqdna[:TAGLEN]
        msgdna  = seqdna[TAGLEN:]
        person  = tagdna[4:12]
        oligo   = tagdna[16:28]        
        
        pid     = tfunc(person)
        oid     = tfunc(oligo)

        # create storage for person if person not found
     
        # check if person has been listed
        if pid not in ramdict:
            ramdict[pid] = {}
        # check if oligo has been listed for person
        if oid not in ramdict[pid]:
            ramdict[pid][oid] = []
        
        for baseindex in range(len(msgdna)):
            
            base = msgdna[baseindex]
            # counter not yet initialized for that position
            if baseindex >= len(ramdict[pid][oid]):
                ramdict[pid][oid].insert(baseindex, Counter())  # Counter object holds counts of A,C,G,T
                
            ramdict[pid][oid][baseindex][base] += 1

    return ramdict
        
"""
def get_consensus(treepath):
    
    #Modifies files in sorted oligo treepath to obtain consensus sequences
    
    # loop through each (person) in the treepath 
    for root, dirs, filenames in os.walk(treepath):
        for fname in filenames:
            filepath = root + "/" + fname
            # read oligos from one file
            oligolist = []            
            with open(filepath, "r") as currfile:
                for line in currfile:
                    oligolist.append(line.strip())
                    
            # count base occurrences at each position
            counts = []
            for oligo in oligolist:
                for index in range(len(oligo)):
                    
                    base = oligo[index]
                    # counter not yet initialized
                    if index >= len(counts):
                        counts.insert(index, Counter())
                    # increase the count of the base
                    counts[index][base] += 1
                    
            # determine the consensus sequence
            consensus = ""
            for poscounter in counts:
                consensus += poscounter.argMax()
            with open(filepath, "w") as consensusfile:
                consensusfile.write(consensus+"\n")
"""

def ram_consensus(ramdict):
    
    for pid in ramdict:
        for oid in ramdict[pid]:
            # determine the consensus sequence of a particular pid, oid
            consensus = ""
            for poscounter in ramdict[pid][oid]:
                consensus += poscounter.argMax()
            ramdict[pid][oid] = consensus
            
    return ramdict

"""
def condense(treepath, tfunc):

    #Condenses oligos into a single file and translates the result.
    #Correct results are order dependent; Python's list sorting function
    #will return the correct order:
    #>>> ['012.txt','134.txt','179.txt','000.txt'].sort()
    #['000.txt','012.txt','134.txt','179.txt']
    
    for root, dirs, filenames in os.walk(treepath):

        # skip directories with no files
        if not filenames:
            continue
        
        # sort files to ensure that condensed and translated files
        # contain information in the correct order
        filenames.sort()           
        
        # create condensed file which contains all oligos concatenated together
        condensedfile = root + "/condensed.txt"
        with open(condensedfile,"w") as condfile:
            for fname in filenames:
                filepath = root + "/" + fname
                with open(filepath, "r") as currfile:
                    for line in currfile:
                        condfile.write(line.strip())
                        
        # translate condensed file into readable text
        translatedfile = root + "/translated.txt"
        with open(translatedfile, "w") as endfile:
            with open(condensedfile,"r") as basefile:
                for line in basefile:
                    dna = line.strip()
                    text = tfunc(dna)
                    endfile.write(text+"\n")
"""

def ram_condense(ramdict, tfunc, outdir):    
    
    try:
        os.makedirs(outdir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise 
    
    for pid in ramdict:

        fullseq = ""        
        condensedfile = outdir + "/" + pid + "_condensed.txt"
        translatedfile = outdir + "/" + pid + "_translated.txt"
        
        old_oid = "000"        
        
        for oid in sorted(ramdict[pid]):
            fullseq += ramdict[pid][oid]
    
            curr = int(oid)
            old  = int(old_oid)
            if (curr - old) > 1:
                break
            old_oid = oid
            
        # write to condensed file and translate
        with open(condensedfile, "w") as condfile:
            condfile.write(fullseq)
        
        with open(translatedfile, "w") as endfile:
            with open(condensedfile, "r") as basefile:
                for line in basefile:
                    dna = line.strip()
                    text = tfunc(dna)
                    endfile.write(text+"\n")

def main():
    
    fqfile = gzip.open("merged.fastq.gz")   
    parser = parse_fastq.readFastq(fqfile)
    
    translator = ASCIIcodons.DNAToText()
    translate_dna = translator.dna_to_text
    
    treepath = "ramtestdna"

    print "Now sorting oligos..."
    sort_start = time.time()
    rd = ram_sort(parser, translate_dna)
    #sort_oligos(parser, translate_dna, treepath)
    sort_end = time.time()
    
    print "Retrieving consensus DNA sequences..."
    comb_start = time.time()
    rd = ram_consensus(rd)
    #get_consensus(treepath)
    comb_end = time.time()
    
    print "Condensing DNA sequences and translating DNA to readable text..."
    cond_start = time.time()
    ram_condense(rd, translate_dna, treepath)
    #condense(treepath, translate_dna)
    cond_end = time.time()
    print "Run complete. See /###_condensed.txt and /###_translated.txt in /%s for results." % treepath
    
    print "Elapsed time to sort was %g seconds" % (sort_end - sort_start)
    print "Elapsed time to combine was %g seconds" % (comb_end - comb_start)
    print "Elapsed time to condense was %g seconds" % (cond_end - cond_start)
            
if __name__ == "__main__":
    main()
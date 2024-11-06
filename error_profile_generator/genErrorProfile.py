import pdb
pdb.set_trace()
import gzip
from collections import defaultdict
import re
#import pickle
import os
import argparse

def process_ref(ref_fa,chr_num):
    cur_chr = ">" + chr_num
    f = open(ref_fa,"r")
    flag = 0
    ref = ""
    curr = 0
    for line in f:
       # print(curr)
       # curr += 1
        if line.rstrip() == cur_chr:
            flag = 1
            continue
        if flag == 1:
            if line[0] != ">":
                ref = ref + line.rstrip()
            else:
                break

    #pickle.dump(ref, open("reference.p", "wb"))
    print("finished generating reference for " + chr_num)
    return ref

def convert_bam_to_sam(bam_file):
    if bam_file[-3:] == "bam":
        os.system('samtools view ' + bam_file + ' > new.sam')
    elif bam_file[-3:] == "sam":
        os.system('cp ' + bam_file + ' new.sam')
    else:
        print("wrong file type, need bam or sam file!")


def process_bam(ref_fa,bam_file,chr_num):
    convert_bam_to_sam(bam_file)
    error_profile = defaultdict(int)
    pos_phred = defaultdict(list)
    #try:
       # ref = pickle.load(open("reference.p","rb"))
    # except:
    ref = process_ref(ref_fa,chr_num)

    f = open("new.sam", "r")
    curr = 0
    for line in f:
       # print(curr)
       # curr += 1
        data = line.rsplit()
        #chr_num = data[2]
        start_p = int(data[3])
        cigar_raw = data[5]
        read = data[9]
        qual = data[10]
        cigar = set("".join(re.findall("[a-zA-Z]+",cigar_raw)))
        if cigar == set(["M"]) or cigar == set(["M","S"]) or cigar == set(["S","M"]):
            #print(cigar_raw)
            for pos in range(len(read)):
                one_ref = ref[start_p+pos-1]
                one_qual = qual[pos]
                one_str = read[pos]
                subst = one_ref + "->" + one_str
                error_profile[(pos,one_qual,subst)] += 1
                if one_qual not in pos_phred[pos]:
                    pos_phred[pos].append(one_qual)
       # else:
           # print(cigar_raw)
    #pickle.dump(error_profile, open("error_profile.p", "wb"))
    #pickle.dump(pos_phred, open("pos_phred.p", "wb"))
    print("finished processing bam/sam file")
    return (error_profile,pos_phred)

    
def gen_error_profile_reads_txt(ref_fa,bam_file,chr_num):
    #try:
       # error_profile = pickle.load(open("error_profile.p", "rb"))
       # pos_phred = pickle.load(open("pos_phred.p", "rb"))
    #except:
    error_profile, pos_phred = process_bam(ref_fa,bam_file,chr_num)

    fw = open("error_profile_reads_2.txt","w")
    fw.writelines("#Pos" + "\t" + "Phred" + "\t" + "A->A" + "\t" + "A->C" + "\t"+ "A->G" + "\t"+ "A->T" + "\t" + "A->N" +"\t" + "C->A" + "\t" + "C->C" + "\t"+ "C->G" + "\t"+ "C->T" + "\t" + "C->N" + "\t" + "G->A" + "\t" + "G->C" + "\t"+ "G->G" + "\t"+ "G->T" + "\t" + "G->N"+ "\t" + "T->A" + "\t" + "T->C" + "\t"+ "T->G" + "\t"+ "T->T" + "\t" + "T->N" + "\n")
    for pos in pos_phred.keys():
        for phred in pos_phred[pos]:
            fw.writelines(str(pos) +"\t"+ str(phred) + "\t")
            for one_code in ["A->A","A->C","A->G","A->T","A->N","C->A","C->C","C->G","C->T","C->N","G->A","G->C","G->G","G->T","G->N","T->A","T->C","T->G","T->T","T->N"]:
                try:
                    count = error_profile[(pos,phred,one_code)]
                    if one_code == "T->N":
                        fw.writelines(str(count))
                    else:
                        fw.writelines(str(count) + "\t")
                except:
                    count = 0 
                    fw.writelines(str(count) + "\t")

            fw.writelines("\n")


def process_10xfastq(fastq_file):
    error_profile = defaultdict(int)
    pos_phred = defaultdict(list)
    f = open(fastq_file,"r")
    #f = gzip.open(fastq_file,"r")
    read_num = "header"
    curr = 0
    for line in f:
        #print(curr)
       # curr += 1
        data = line.rsplit()
        if read_num == "header":
            if data[1]=="1:N:0:0":
                read_num = "1_str"
                continue
            elif data[1] == "3:N:0:0":
                read_num = "3_str"
                continue

        if read_num == "3_str":
            read_num = "3+"
            continue

        if read_num == "3+":
            read_num = "3_qual"
            continue

        if read_num == "3_qual":
            read_num = "header"
            continue

        if read_num == "+":
            if data[0]== "+":
                read_num = "1_qual"
                continue

        if read_num == "1_qual":
            barcode_qual = data[0][:16]
            read_num = "header"
           
            for pos in range(len(barcode)):
                one_code = barcode[pos]
                #one_phred =ord(barcode_qual[pos]) - 33
                one_phred = barcode_qual[pos]
                if one_phred not in pos_phred[pos]:
                    pos_phred[pos].append(one_phred)
                error_profile[(pos,one_phred,one_code)] += 1 ### key: (position, phred score, barcode base); value: count

            continue

        if read_num == "1_str":
            barcode = data[0][:16] ### first 16 bases in seq (read1) are barcode
            read_num = "+"
            continue

    print("finished processing fastq file")  
    return (error_profile,pos_phred)

def gen_error_profile_barcode_txt(fastq_file):
    error_profile, pos_phred = process_10xfastq(fastq_file)
    fw = open("error_profile_barcode.txt","w")
    fw.writelines("#Pos" + "\t" + "Phred" + "\t" + "A" + "\t" + "C" + "\t"+ "G" + "\t"+ "T" + "\t" + "N" + "\n")
    for pos in pos_phred.keys():
        for phred in pos_phred[pos]:
            fw.writelines(str(pos) +"\t"+ str(phred) + "\t")
            for one_code in ["A","C","G","T","N"]:
                try:
                    count = error_profile[(pos,phred,one_code)]
                    if one_code == "N":
                        fw.writelines(str(count))
                    else:
                        fw.writelines(str(count) + "\t")
                except:
                    count = 0 
                    fw.writelines(str(count) + "\t")

            fw.writelines("\n")


if __name__ == "__main__":
   #gen_error_profile_barcode_txt("read-RA_si-ACTGTGGC_lane-001-chunk-0002.fastq")
   #gen_error_profile_reads_txt("genome.fa","NA12878.chr19.bam","chr19")
   gen_error_profile_reads_txt("genome.fa","test.sam","chr19")
   os.system('rm new.sam')
   print("finished error profile txt file")
















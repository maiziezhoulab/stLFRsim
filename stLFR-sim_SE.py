#!/usr/bin/env python
import sys
import multiprocessing
import numpy as np
import os
import gzip
from collections import defaultdict

# Parameter defination
large_droplet = 40000000
large_template = 1000000000


class Molecule(object):
    def __init__(self, length, start, end, index):
        self.seqidx = index
        self.length = length
        self.index_droplet = 0
        self.barcode = ["Null", "Null", "Null"]
        self.shortreads = 0
        self.start = start
        self.end = end


class Qual_Substitute(object):
    def __init__(self, phred, change):
        self.phred = phred
        self.substitute = change


class Short_reads_SE(object):
    def __init__(self, seq2, qual2, start2, end2):
        # self.seq1 = seq1
        # self.qual1 = qual1
        # self.start1 = start1
        # self.end1 = end1
        self.seq2 = seq2
        self.qual2 = qual2
        self.start2 = start2
        self.end2 = end2


class Short_reads(object):
    def __init__(self, seq, qual):
        self.seq = seq
        self.qual = qual


class parameter(object):
    def __init__(self):
        self.CF = 0
        self.CR = 0
        self.N_FP = 0
        self.Mu_F = 0
        self.SR = 0
        self.Mu_IS = 0
        self.Std_IS = 0
        self.Fastahap1 = "N"
        self.Fastahap2 = "N"
        self.barcodepool = "N"
        self.hap = 1
        self.Seq_error = "N"
        self.Seq_qual = "N"
        self.Barcode_qual = "N"
        self.Fast_mode = "Y"
        self.Error_rate = 0
        self.processor = 1
        self.redundance = "N"
        self.Barcode_Length = 42


# read parameters from file
def input_parameter(argv, parameter_struc):
    deter = 1
    f = open(argv, "r")
    for line in f:
        Par = line.split("=")
        if len(Par) == 2:
            if Par[0] == "Path_Fastahap1":
                parameter_struc.Fastahap1 = Par[1].strip("\n")
            elif Par[0] == "Path_Fastahap2":
                parameter_struc.Fastahap2 = Par[1].strip("\n")
            elif Par[0] == "Path_adundance":
                parameter_struc.redundance = Par[1].strip("\n")
            elif Par[0] == "Fast_mode":
                parameter_struc.Fast_mode = Par[1].strip("\n")
            elif Par[0] == "processors":
                parameter_struc.processor = Par[1].strip("\n")
            elif Par[0] == "Seq_error":
                parameter_struc.Seq_error = Par[1].strip("\n")
            elif Par[0] == "Error_rate":
                parameter_struc.Error_rate = float(Par[1].strip("\n"))
            elif Par[0] == "Path_Seq_qual":
                parameter_struc.Seq_qual = Par[1].strip("\n")
            elif Par[0] == "Path_Barcode_qual":
                parameter_struc.Barcode_qual = Par[1].strip("\n")
            elif Par[0] == "CF":
                parameter_struc.CF = float(Par[1].strip("\n"))
            elif Par[0] == "Mu_IS":
                parameter_struc.Mu_IS = float(Par[1].strip("\n"))
            elif Par[0] == "Std_IS":
                parameter_struc.Std_IS = float(Par[1].strip("\n"))
            elif Par[0] == "CR":
                parameter_struc.CR = float(Par[1].strip("\n"))
            elif Par[0] == "N_FP":
                parameter_struc.N_FP = int(Par[1].strip("\n"))
            elif Par[0] == "Mu_F":
                parameter_struc.Mu_F = float(Par[1].strip("\n"))
            elif Par[0] == "SR":
                parameter_struc.SR = int(Par[1].strip("\n"))
            elif Par[0] == "Path_barcodepool":
                parameter_struc.barcodepool = Par[1].strip("\n")
            elif Par[0] == "Hap":
                parameter_struc.hap = int(Par[1].strip("\n"))
            elif Par[0] == "Barcode_Length":
                parameter_struc.Barcode_Length = int(Par[1].strip("\n"))
    if parameter_struc.Barcode_Length != int(
        parameter_struc.Barcode_qual[
            parameter_struc.Barcode_qual.rfind("_")
            + 1 : parameter_struc.Barcode_qual.rfind(".")
        ]
    ):
        print(
            "The Barcode_Length {} and Path_Barcode_qual {} are not consistent!".format(
                parameter_struc.Barcode_Length, parameter_struc.Barcode_qual
            )
        )
        exit(1)
    f.close()

    if parameter_struc.hap == 1:
        # print(os.path.isfile(parameter_struc.Fastahap1))
        if os.path.isfile(parameter_struc.Fastahap1) == False:
            deter = 0
            print("template fasta file (Fasta) does not exist")
        if parameter_struc.Fastahap1 == "N":
            deter = 0
            print("Missing template fasta file (Fasta)")
    if parameter_struc.hap == 2:
        if os.path.isfile(parameter_struc.Fastahap1) == False:
            deter = 0
            print("template haplotype1 fasta file (Fasta) does not exist")
        if os.path.isfile(parameter_struc.Fastahap2) == False:
            deter = 0
            print("template haplotype2 fasta file (Fasta) does not exist")
        if parameter_struc.Fastahap1 == "N":
            deter = 0
            print("Missing template haplotype1 fasta file (Fasta)")
        if parameter_struc.Fastahap2 == "N":
            deter = 0
            print("Missing template haplotype2 fasta file (Fasta)")
    if parameter_struc.CF == 0:
        deter = 0
        print("Missing coverage for long fragment (CF)")
    if parameter_struc.CR == 0:
        deter = 0
        print("Missing coverage of short reads for long fragment (CR)")
    if parameter_struc.N_FP == 0:
        deter = 0
        print("Missing the average number of molecules for eachh droplet (N_FP)")
    if parameter_struc.Mu_F == 0:
        deter = 0
        print("Missing the average length for long fragment (Kb) (Mu_F)")
    if parameter_struc.SR == 0:
        deter = 0
        print("Missing length of short reads (bp) (SR)")
    if parameter_struc.Mu_IS == 0:
        deter = 0
        print("Missing mean of insert size of short reads (bp) (Mu_IS)")
    if parameter_struc.Std_IS == 0:
        deter = 0
        print(
            "Missing standard deviation of insert size of short fragment (bp) (Std_IS)"
        )
    if parameter_struc.barcodepool == "N":
        deter = 0
        print("Missing barcode list (barcodepool)")
    if os.path.isfile(parameter_struc.barcodepool) == False:
        deter = 0
        print("barcode list does not exist")
    if parameter_struc.hap == 2:
        parameter_struc.CF = parameter_struc.CF / 2
    return deter


# read template sequence
def input_seq_zip(in_path):
    reflist = []
    reftitle = []
    sequence = ""
    f = gzip.open(in_path, "r")
    index = 0
    for line in f:
        if line.decode()[0] == ">":
            title = line.decode().strip("\n").split(" ")[0]
            reftitle.append(title[1:])
            if index == 0:
                index += 1
            else:
                reflist.append(sequence)
                sequence = ""
        else:
            sequence += line.decode().strip("\n")
    reflist.append(sequence)
    f.close()
    return reflist, reftitle


def input_seq(in_path):
    reflist = []
    reftitle = []
    sequence = ""
    f = open(in_path, "r")
    index = 0
    for line in f:
        if line[0] == ">":
            title = line.strip("\n").split(" ")[0]
            reftitle.append(title[1:])
            if index == 0:
                index += 1
            else:
                reflist.append(sequence)
                sequence = ""
        else:
            sequence += line.strip("\n")
    reflist.append(sequence)
    f.close()
    return reflist, reftitle


# sapmpling long fragments from empirical distribution
def read_abundance(Par):
    inputfile = open(Par.redundance, "r")
    abun_dict = defaultdict(float)
    for line in inputfile:
        info = line.strip("\n").split("\t")
        abun_dict[info[0]] = float(info[1])
    inputfile.close()
    return abun_dict


def randomlong(Par, reflist, reftitle):
    abun_dict = {}
    global N_frag
    N_frag = 0
    frag_list = []
    MolSet = []
    For_hist = []
    index = 0
    T_frag = 0
    T_frag_eff = 0
    ref_total_len = 0
    ref_effective_len = 0
    if Par.redundance != "N":
        abun_dict = read_abundance(Par)
    for seq in reflist:
        # calculate required number of molecule
        lensingle = len(seq)
        if Par.redundance == "N":
            N_frag = int(lensingle * Par.CF / (Par.Mu_F * 1000))
        else:
            N_frag = int(
                abun_dict[reftitle[index]]
                * lensingle
                * len(reflist)
                * Par.CF
                / (Par.Mu_F * 1000)
            )
        # randome simulate molecules
        for i in range(N_frag):
            start = int(np.random.uniform(low=0, high=lensingle))
            length = int(np.random.exponential(scale=Par.Mu_F * 1000))
            end = start + length - 1
            if length == 0:
                continue
            if end > lensingle:
                Molseq = seq[start:lensingle]
                lengthnew = lensingle - start
                NewMol = Molecule(lengthnew, start, lensingle, index)
                MolSet.append(NewMol)
            else:
                Molseq = seq[start:end]
                NewMol = Molecule(length - 1, start, end, index)
                MolSet.append(NewMol)
        index += 1
    N_frag = len(MolSet)
    return MolSet


# assign long fragments to droplet
def deternumdroplet(N_frag, N_FP):
    # frag_drop = np.random.poisson(N_FP, large_droplet)
    frag_drop = [ N_FP ] * large_droplet
    assign_drop = []
    totalfrag = 0
    for i in range(large_droplet):
        totalfrag = totalfrag + frag_drop[i]
        if totalfrag <= N_frag:
            assign_drop.append(frag_drop[i])
            Figure_len_molecule.append(frag_drop[i])
        else:
            last = N_frag - (totalfrag - frag_drop[i])
            assign_drop.append(last)
            Figure_len_molecule.append(last)
            break
    return assign_drop


# assign barcode to each fragment
def selectbarcode(pool, assign_drop, MolSet, droplet_container):
    # permute index of long fragment for random sampling
    permutnum = np.random.permutation(N_frag)
    # include barcode in the list
    all_barcodes = []
    N_droplet = len(assign_drop)

    f = open(pool, "r")
    for line in f:
        all_barcodes.append(line.strip("\n"))
    f.close()

    barcode_set = set()
    start = 0
    for i in range(N_droplet):
        bc1, bc2, bc3 = "", "", ""
        while True:
            bc1, bc2, bc3 = np.random.choice(all_barcodes, 3)
            if (bc1, bc2, bc3) not in barcode_set:
                barcode_set.add((bc1, bc2, bc3))
                break
        num_molecule_per_partition = assign_drop[i]
        index_molecule = permutnum[start : start + num_molecule_per_partition]
        totalseqlen = 0
        temp = []
        start = start + num_molecule_per_partition
        for j in range(num_molecule_per_partition):
            index = index_molecule[j]
            temp.append(index)
            MolSet[index].index_droplet = i
            MolSet[index].barcode[0] = bc1
            MolSet[index].barcode[1] = bc2
            MolSet[index].barcode[2] = bc3
            totalseqlen = totalseqlen + MolSet[index].length
        droplet_container.append(temp)
    return MolSet


def child_initialize(_MolSet, _reflist):
    global MolSet
    global reflist
    MolSet = _MolSet
    reflist = _reflist


def haploid(Par, lib):
    global Figure_len_molecule
    global Figure_num_molecule
    global MolSet
    global reflist
    Figure_len_molecule = []
    Figure_num_molecule = []
    droplet_container = []
    reftitle = []
    if Par.hap == 1:
        if ".gz" in Par.Fastahap1:
            reflist, reftitle = input_seq_zip(Par.Fastahap1)
        else:
            reflist, reftitle = input_seq(Par.Fastahap1)
    if Par.hap == 2:
        if ".gz" in Par.Fastahap1:
            reflist, reftitle = input_seq_zip(Par.Fastahap1)
        else:
            reflist, reftitle = input_seq(Par.Fastahap1)
        if ".gz" in Par.Fastahap2:
            reflist2, reftitle2 = input_seq_zip(Par.Fastahap2)
        else:
            reflist2, reftitle2 = input_seq(Par.Fastahap2)
        reflist.extend(reflist2)
        reftitle.extend(reftitle2)
    # recode cut position of long fragment
    print("read template finished (library " + lib + ")")
    MolSet = randomlong(Par, reflist, reftitle)
    print("generate molecule finished (library " + lib + ")")
    # calculate number of droplet
    assign_drop = deternumdroplet(N_frag, Par.N_FP)
    print("assign molecule to droplet finished (library " + lib + ")")
    MolSet = selectbarcode(Par.barcodepool, assign_drop, MolSet, droplet_container)
    print("assign barcode to molecule finished (library " + lib + ")")
    print("begin to simulate short reads, please wait...")
    pool = multiprocessing.Pool(
        int(Par.processor),
        initializer=child_initialize,
        initargs=(
            MolSet,
            reflist,
        ),
    )
    Mol_process = []
    maxprocessor = int(len(MolSet) / int(Par.processor))
    t = 0
    while t < len(MolSet):
        Mol_process.append(t)
        t = t + maxprocessor
    Mol_process.append(len(MolSet) - 1)
    for m in range(len(Mol_process) - 1):
        pool.apply_async(
            SIMSR,
            (
                Mol_process[m],
                Mol_process[m + 1],
                Par,
                lib,
                m,
            ),
        )
    pool.close()
    pool.join()


    # for m in range(len(Mol_process) - 1):
    #     SIMSR(
    #             Mol_process[m],
    #             Mol_process[m + 1],
    #             Par,
    #             lib,
    #             m,
    #         )





    # os.system("touch " + lib + "_S1_L001_R1_001.fastq.gz")
    os.system("touch " + lib + "_S1_L001_R2_001.fastq.gz")
    for m in range(len(Mol_process) - 1):
        # os.system(
        #     "cat "
        #     + lib
        #     + "_S1_L001_id"
        #     + str(m)
        #     + "_R1_001.fastq.gz >> "
        #     + lib
        #     + "_S1_L001_R1_001.fastq.gz"
        # )
        os.system(
            "cat "
            + lib
            + "_S1_L001_id"
            + str(m)
            + "_R2_001.fastq.gz >> "
            + lib
            + "_S1_L001_R2_001.fastq.gz"
        )
        # os.system("rm " + lib + "_S1_L001_id" + str(m) + "_R1_001.fastq.gz")
        os.system("rm " + lib + "_S1_L001_id" + str(m) + "_R2_001.fastq.gz")
    # os.system("mv " + lib + "_S1_L001_R1_001.fastq.gz " + sys.argv[1] + "/lib_" + lib)
    os.system("mv " + lib + "_S1_L001_R2_001.fastq.gz " + sys.argv[1] + "/lib_" + lib)
    # plt.hist(Figure_len_molecule)
    # plt.xlabel('Molecule length')
    # plt.ylabel('Number of molecules')
    # plt.title('Histogram of molecule length (total '+str(len(Figure_len_molecule))+' molecules)')
    # plt.show()
    # plt.savefig('Len_Molecule_hist_lib'+lib+'.png')
    # plt.close()
    # plt.hist(Figure_num_molecule)
    # plt.xlabel('Number of molecules in droplets')
    # plt.ylabel('Number of molecules')
    # plt.title('Histogram of the number of molecules in droplets (total '+str(len(Figure_num_molecule))+' droplet)')
    # plt.show()
    # plt.savefig('Num_Molecule_hist_lib'+lib+'.png')
    # plt.close()
    # os.system('mv Num_Molecule_hist_lib'+lib+'.png '+sys.argv[1]+'/lib'+lib)
    # os.system('mv Len_Molecule_hist_lib'+lib+'.png '+sys.argv[1]+'/lib'+lib)
    print("Library " + lib + " simulation completed!")
    return None


def reverseq(seq):
    complementary = ""
    rev_complementary = ""
    for i in range(len(seq)):
        if seq[i] == "A":
            complementary += "T"
        elif seq[i] == "T":
            complementary += "A"
        elif seq[i] == "C":
            complementary += "G"
        elif seq[i] == "G":
            complementary += "C"
        elif seq[i] == "N":
            complementary += "N"
    rev_complementary = complementary[::-1]
    return rev_complementary


def Input_BarcodeQual(Par):
    f = open(Par.Barcode_qual, "r")
    line_index = 0
    position = 0
    Qual_dict = defaultdict(list)
    Prob_dict = defaultdict(list)
    for line in f:
        if line_index > 0:
            linequal = line.strip("\t,\n")
            qualarray = linequal.split("\t")
            Qual_dict[qualarray[0]].append(ord(qualarray[1]))
            Prob_dict[qualarray[0]].append(float(qualarray[2]))
        line_index = line_index + 1
    f.close()
    return Qual_dict, Prob_dict


def Input_SeqQual(Par):
    f = open(Par.Seq_qual, "r")
    line_index = 0
    position = 0
    Qual_dict = defaultdict(list)
    Prob_dict = defaultdict(list)
    Substitute_dict = defaultdict(list)
    for line in f:
        if line_index > 0:
            change = []
            linequal = line.strip("\t,\n")
            qualarray = linequal.split("\t")
            Qual_dict[qualarray[0]].append(ord(qualarray[1]))
            Prob_dict[qualarray[0]].append(float(qualarray[2]))
            Substitute_dict[(qualarray[0], ord(qualarray[1]))] = list(
                map(float, qualarray[3:])
            )
        line_index = line_index + 1
    f.close()
    return Qual_dict, Prob_dict, Substitute_dict


def SIMSR(start, end, Par, lib, jobid):
    MolSet_cand = MolSet[start:end]
    # f_reads1 = gzip.open(lib + "_S1_L001_id" + str(jobid) + "_R1_001.fastq.gz", "wb")
    f_reads2 = gzip.open(lib + "_S1_L001_id" + str(jobid) + "_R2_001.fastq.gz", "wb")
    [SeqQual_dict, SeqProb_dict, SeqSubstitute_dict] = Input_SeqQual(Par)
    [BarcodeQual_dict, BarcodeProb_dict] = Input_BarcodeQual(Par)
    last_reads = 0
    for i in range(len(MolSet_cand)):
        seq = reflist[MolSet_cand[i].seqidx]
        Seq_rand_qual = []
        Barcode_rand_qual = []
        # num_reads = int(int(MolSet_cand[i].length / (Par.SR * 2)) * Par.CR)  # for pair end reads
        num_reads = int(int(MolSet_cand[i].length / (Par.SR )) * Par.CR) # for single end reads
        if num_reads == 0:
            continue
        All_forward = seq[MolSet_cand[i].start : MolSet_cand[i].end].upper()
        # All_reverse = reverseq(All_forward)
        # insert_size = np.random.normal(loc=Par.Mu_IS, scale=Par.Std_IS, size=num_reads)
        Totalreads = []
        new_reads = last_reads + num_reads
        # Seq_new_qual = np.zeros((num_reads * 2, Par.SR), dtype=int)
        Seq_new_qual = np.zeros((num_reads , Par.SR), dtype=int)
        Barcode_new_qual = np.zeros((num_reads, Par.Barcode_Length), dtype=int)
        for m in range(Par.Barcode_Length):
            Barcode_coll_phred = BarcodeQual_dict[str(m)]
            Barcode_coll_prob = BarcodeProb_dict[str(m)]
            Barcode_new_qual[:, m] = np.random.choice(
                Barcode_coll_phred, p=Barcode_coll_prob, size=(num_reads)
            )
        for m in range(Par.SR):
            Seq_coll_phred = SeqQual_dict[str(m)]
            Seq_coll_prob = SeqProb_dict[str(m)]
            Seq_new_qual[:, m] = np.random.choice(
                Seq_coll_phred, p=Seq_coll_prob, size=num_reads 
            )
        Seq_new_qual2 = Seq_new_qual[0:num_reads, :]
        # Seq_new_qual2 = Seq_new_qual[num_reads : 2 * num_reads, :]
        for j in range(num_reads):
            SE_read = single_end(
                Par,
                MolSet_cand[i],
                Barcode_new_qual,
                Seq_new_qual2,
                All_forward,
                j,
                SeqSubstitute_dict,
            )
            Totalreads.append(SE_read)
        for j in range(len(Totalreads)):
            # read1seq = Totalreads[j].seq1
            # read1qual = Totalreads[j].qual1
            read2seq = Totalreads[j].seq2
            read2qual = Totalreads[j].qual2
            read2N = read2seq[0 : Par.SR]
            if read2N.count("N") > Par.SR * 0.1:
                continue
            readname = (
                "@ST-K00126:"
                + str(i + 1)
                + ":H5W53BBXX:"
                + str(MolSet_cand[i].start)
                + ":"
                + str(MolSet_cand[i].end)
                + ":"
                + str(Totalreads[j].start2)
                + ":"
                + str(Totalreads[j].end2)
            )
            # f_reads1.write((readname + " 1:N:0\n").encode("utf-8"))
            # f_reads1.write((read1seq + "\n").encode("utf-8"))
            # f_reads1.write(("+\n").encode("utf-8"))
            # f_reads1.write((read1qual + "\n").encode("utf-8"))
            # f_reads1.write(b'\n')
            f_reads2.write((readname + " 3:N:0\n").encode("utf-8"))
            f_reads2.write((read2seq + "\n").encode("utf-8"))
            f_reads2.write(("+\n").encode("utf-8"))
            f_reads2.write((read2qual + "\n").encode("utf-8"))
    # f_reads1.close()
    f_reads2.close()
    return None


def single_end(
    Par,
    MolSetX,
    Barcode_rand_qual,
    Seq_rand_qual2,
    All_forward,
    index,
    SeqSubstitute_dict,
):
    # is_read = int(np.absolute(insert_size[index]))
    start_for = int(np.random.uniform(low=1, high=MolSetX.length - Par.SR - 1))
    end_for = start_for + int(Par.SR)
    assert end_for < MolSetX.length
    forward_seq = All_forward[start_for:end_for]
    # start_rev = MolSetX.length - end_for
    # end_rev = start_rev + int(is_read)
    # reverse_seq = All_reverse[start_rev:end_rev]
    # read1 = forward_seq[0 : Par.SR]
    read2 = forward_seq[0 : Par.SR]
    # read1seq = ""
    read2seq = ""
    # read1qual = ""
    read2qual = ""
    if Par.Fast_mode == "N":
        if Par.Seq_error == "N":
            # read1seq = read1
            read2seq = (
                read2
                + MolSetX.barcode[0]
                + "N" * int((Par.Barcode_Length - 30) / 2)
                + MolSetX.barcode[1]
                + "N" * int((Par.Barcode_Length - 30) / 2)
                + MolSetX.barcode[2]
            )

        if Par.Seq_error == "Y":
            # readerror1 = np.random.choice(
            #     [0, 1], p=[1 - Par.Error_rate, Par.Error_rate], size=(Par.SR)
            # )
            readerror2 = np.random.choice(
                [0, 1], p=[1 - Par.Error_rate, Par.Error_rate], size=(Par.SR)
            )
            # error1 = readerror1[0 : Par.SR].nonzero()
            error2 = readerror2[0 : Par.SR].nonzero()
            # read1new = list(read1)
            read2new = list(read2)
            # for i in error1[0]:
            #     rand_nuc = None
            #     if read1[i] == "A":
            #         rand_nuc = np.random.choice(
            #             ["C", "G", "T", "N"],
            #             1,
            #             p=np.asarray(
            #                 SeqSubstitute_dict[(str(i), Seq_rand_qual1[index, i])][0:4]
            #             ),
            #         )
            #     elif read1[i] == "C":
            #         rand_nuc = np.random.choice(
            #             ["A", "G", "T", "N"],
            #             1,
            #             p=np.asarray(
            #                 SeqSubstitute_dict[(str(i), Seq_rand_qual1[index, i])][4:8]
            #             ),
            #         )
            #     elif read1[i] == "G":
            #         rand_nuc = np.random.choice(
            #             ["A", "C", "T", "N"],
            #             1,
            #             p=np.asarray(
            #                 SeqSubstitute_dict[(str(i), Seq_rand_qual1[index, i])][8:12]
            #             ),
            #         )
            #     elif read1[i] == "T":
            #         rand_nuc = np.random.choice(
            #             ["A", "C", "G", "N"],
            #             1,
            #             p=np.asarray(
            #                 SeqSubstitute_dict[(str(i), Seq_rand_qual1[index, i])][
            #                     12:16
            #                 ]
            #             ),
            #         )
            #     elif read1[i] == "N":
            #         rand_nuc = np.random.choice(
            #             ["A", "C", "G", "T"], 1, p=np.asarray([0.25, 0.25, 0.25, 0.25])
            #         )
            #     read1new[i] = rand_nuc[0]

            for i in error2[0]:
                rand_nuc = None
                if read2[i] == "A":
                    rand_nuc = np.random.choice(
                        ["C", "G", "T", "N"],
                        1,
                        p=np.asarray(
                            SeqSubstitute_dict[(str(i), Seq_rand_qual2[index, i])][0:4]
                        ),
                    )
                elif read2[i] == "C":
                    rand_nuc = np.random.choice(
                        ["A", "G", "T", "N"],
                        1,
                        p=np.asarray(
                            SeqSubstitute_dict[(str(i), Seq_rand_qual2[index, i])][4:8]
                        ),
                    )
                elif read2[i] == "G":
                    rand_nuc = np.random.choice(
                        ["A", "C", "T", "N"],
                        1,
                        p=np.asarray(
                            SeqSubstitute_dict[(str(i), Seq_rand_qual2[index, i])][8:12]
                        ),
                    )
                elif read2[i] == "T":
                    rand_nuc = np.random.choice(
                        ["A", "C", "G", "N"],
                        1,
                        p=np.asarray(
                            SeqSubstitute_dict[(str(i), Seq_rand_qual2[index, i])][
                                12:16
                            ]
                        ),
                    )
                elif read2[i] == "N":
                    rand_nuc = np.random.choice(
                        ["A", "C", "G", "T"], 1, p=np.asarray([0.25, 0.25, 0.25, 0.25])
                    )
                read2new[i] = rand_nuc[0]
            # read1seq = "".join(read1new)
            read2seq = (
                "".join(read2new)
                + MolSetX.barcode[0]
                + "N" * int((Par.Barcode_Length - 30) / 2)
                + MolSetX.barcode[1]
                + "N" * int((Par.Barcode_Length - 30) / 2)
                + MolSetX.barcode[2]
            )

        # read1qual = "".join(map(chr, Seq_rand_qual1[index, :]))
        read2qual = (
            "".join(map(chr, Seq_rand_qual2[index, :]))
            + "".join(map(chr, Barcode_rand_qual[index, 0:10]))
            + "K" * int((Par.Barcode_Length - 30) / 2)
            + "".join(
                map(
                    chr,
                    Barcode_rand_qual[
                        index,
                        int(Par.Barcode_Length / 2)
                        - 5 : int(Par.Barcode_Length / 2)
                        + 5,
                    ],
                )
            )
            + "K" * int((Par.Barcode_Length - 30) / 2)
            + "".join(
                map(
                    chr,
                    Barcode_rand_qual[
                        index, Par.Barcode_Length - 10 : Par.Barcode_Length
                    ],
                )
            )
        )
    else:
        # read1seq = read1
        read2seq = (
            read2
            + MolSetX.barcode[0]
            + "N" * int((Par.Barcode_Length - 30) / 2)
            + MolSetX.barcode[1]
            + "N" * int((Par.Barcode_Length - 30) / 2)
            + MolSetX.barcode[2]
        )
        # read1qual = "K" * Par.SR
        read2qual = "K" * (Par.SR + Par.Barcode_Length)
    return Short_reads_SE(
        read2seq, read2qual, start_for, end_for
    )


def helpinfo():
    helpinfo = """
        LRTK-SIM: Linked reads simulator for 10X Chromium System.
        Version: 1.0.0
        Dependents: Python (>=3.0)
        Last Updated Date: 2017-07-22
        Contact: zhanglu2@stanford.edu

        Usage: python LRTK-SIM.py <path to configuration files>

        Example: python LRTK-SIM.py ./diploid_config (for diploid)\
                 
                 python LRTK-SIM.py ./meta_config (for metagenomics)
    """
    print(helpinfo)


def main():
    if len(sys.argv) < 2:
        helpinfo()
        sys.exit(-1)
    #os.system("rm -rf " + sys.argv[1] + "/lib*")
    #list = os.listdir(sys.argv[1])
    list = [ filename for filename in  os.listdir(sys.argv[1]) if '.txt' in filename]
    list.sort()
    Par = parameter()
    for i in range(len(list)):
        libname = list[i].split(".")
        print("processing library " + str(i + 1) + " for " + libname[0])
        os.system("mkdir " + sys.argv[1] + "/lib_" + libname[0])
        deter = input_parameter(sys.argv[1] + "/" + list[i], Par)
        if deter == 1:
            haploid(Par, libname[0])
    return None


if __name__ == "__main__":
    main()

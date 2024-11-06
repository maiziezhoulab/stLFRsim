from collections import defaultdict 

import numpy as np

def Input_SeqQual(seq_qual):
    f = open(Seq_qual, "r")
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
            if line_index == 7250:
                print(qualarray)
            
            Qual_dict[qualarray[0]].append(ord(qualarray[1]))

            Prob_dict[qualarray[0]].append(float(qualarray[2]))
            Substitute_dict[(qualarray[0], ord(qualarray[1]))] = list(
                map(float, qualarray[3:])
            )

        line_index = line_index + 1
    f.close()
    print(0,Qual_dict['0'], Qual_dict['906'])
    return Qual_dict, Prob_dict, Substitute_dict


Seq_qual = "/data/maiziezhou_lab/CanLuo/Software/LRTK-SIM-stlfr/resource/error_profile_reads.txt"
[SeqQual_dict, SeqProb_dict, SeqSubstitute_dict] = Input_SeqQual(Seq_qual)

sr=1000
num_reads = int(10e3 / sr * 0.8)
Seq_new_qual = np.zeros((num_reads , sr), dtype=int)

for m in range(sr):
    try:
        Seq_coll_phred = SeqQual_dict[str(m)]
        Seq_coll_prob = SeqProb_dict[str(m)]
        Seq_new_qual[:, m] = np.random.choice(
            Seq_coll_phred, p=Seq_coll_prob, size=num_reads 
        )
    except:
        print(m)
        print(Seq_coll_phred)
        break


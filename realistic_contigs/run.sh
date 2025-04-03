
ref=REF
seq=ASM_FASTA
outbam=BAM

#NOTE: the minimap2 command was from HiCanu paper assemblies to ref alignment, it was also used in PAV pipeline
# Paper: https://genome.cshlp.org/content/30/9/1291.full.pdf
# Section: Commands for identifying contig ends
minimap2 --secondary=no -a --eqx -Y -x asm20 -s 200000 -z 10000,50 -r 50000 --end-bonus=100 -O 5,56 -E 4,1 -B 5 ${ref} ${seq} | samtools sort -o ${outbam}
samtools index ${outbam}

samtools view -b ${outbam} chr6 | samtools fasta > ${outbam%%.bam}_chr6.fa
samtools view -b ${outbam} chr1 | samtools fasta > ${outbam%%.bam}_chr1.fa
samtools view -b ${outbam} chr10 | samtools fasta > ${outbam%%.bam}_chr10.fa
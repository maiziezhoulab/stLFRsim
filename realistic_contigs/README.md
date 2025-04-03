# Diploid Assemblies

HG002.alt.pat.GCA_018852605.fasta.gz and HG002.pri.mat.GCA_018852615.fasta.gz

NCBI:

PAT: curl -OJX GET "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/GCA_018852605.1/download?include_annotation_type=GENOME_FASTA,GENOME_GFF,RNA_FASTA,CDS_FASTA,PROT_FASTA,SEQUENCE_REPORT&filename=GCA_018852605.1.zip" -H "Accept: application/zip"

MAT: curl -OJX GET "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/GCA_018852615.1/download?include_annotation_type=GENOME_FASTA,GENOME_GFF,RNA_FASTA,CDS_FASTA,PROT_FASTA,SEQUENCE_REPORT&filename=GCA_018852615.1.zip" -H "Accept: application/zip"

S3 bucket:

PAT: wget https://s3-us-west-2.amazonaws.com/human-pangenomics/working/HPRC_PLUS/HG002/assemblies/year1_f1_assembly_v2_genbank/HG002.paternal.f1_assembly_v2_genbank.fa.gz

MAT: wget https://s3-us-west-2.amazonaws.com/human-pangenomics/working/HPRC_PLUS/HG002/assemblies/year1_f1_assembly_v2_genbank/HG002.maternal.f1_assembly_v2_genbank.fa.gz

# CHM3-T2T reference

https://www.ncbi.nlm.nih.gov/assembly/GCA_009914755.4

# Get realistic contigs for simulation:

Replace REF and ASM_FASTA in run.sh with corresponding assembly and reference to get contigs for downstream simulation. Run separatly for PAT and MAT assembly. 
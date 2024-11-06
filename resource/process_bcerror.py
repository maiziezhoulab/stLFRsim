import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="barcode error raw file")
args = parser.parse_args()

error_barcode = open(args.input, "r")
error_processed = open(
    "error_profile_barcode_{}.txt".format(args.input[args.input.rfind("_") + 1 :]), "w"
)
pos = 0
content = []
for line in error_barcode:
    line = line.strip("\t\n").split("\t")
    if line[0] == "#Pos":
        line.insert(2, "prob")
        error_processed.write("\t".join(line) + "\n")
        continue
    if line[0] != str(pos):
        sum_num = 0
        for li in content:
            sum_num = sum_num + li[2]
        for li in content:
            li[2] = str(li[2] / sum_num)
        for li in content:
            error_processed.write("\t".join(li) + "\n")
        pos = pos + 1
        content = []
    line[1] = chr(int(line[1]) + 33)
    line.insert(
        2, int(line[2]) + int(line[3]) + int(line[4]) + int(line[5]) + int(line[6])
    )
    content.append(line)
sum_num = 0
for li in content:
    sum_num = sum_num + li[2]
for li in content:
    li[2] = str(li[2] / sum_num)
for li in content:
    error_processed.write("\t".join(li) + "\n")
error_barcode.close()
error_processed.close()
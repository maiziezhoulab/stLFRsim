with open("error_profile_reads_151.txt",'r') as f:
	with open("error_profile_reads_151_6.txt",'w') as fw:
		header = []
		body = []
		for line in f:
			if line[0]=='#':
				header.append(line)
			else:
				body.append(line)
		all_body = []

		for i in range(6):
			all_body.extend(body)

		for i in range(len(all_body)):
			line = all_body[i].split()
			idx = i//8
			line[0] = str(idx)
			all_body[i] = '\t'.join(line)+'\n'

		fw.writelines(header + all_body)

awk -v OFS='\t' '{$1 = $1 + 94; print}'  seqqual > seqqual_new

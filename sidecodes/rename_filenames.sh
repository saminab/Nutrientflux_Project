#!/bin/bash
for data in `ls -d *nc*`; do
    # Extract the date part from the filename (20230301 in this case)
    date=$(echo "$data" | grep -o -E '[0-9]{8}')
	# Extract the last 6 characters of the filename
    suffix=${data: -7}

    # Rename the file with the prefix, date, and original filename
    mv "$data" "Fvcome_houron_estuary_${date}.${suffix}"
done
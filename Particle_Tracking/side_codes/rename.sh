#!/bin/bash
for data in `ls -d *nc*`;do
	mv  $data fvcome_houron_estuary_$data
	done

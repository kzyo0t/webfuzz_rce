#!/bin/bash
input="seeds.txt"
while IFS= read -r line;
do
	wfuzz -v --req-delay 10 --ss "www-data" -p 127.0.0.1:8180 -w fuzzing_ga.txt $line
done < $input




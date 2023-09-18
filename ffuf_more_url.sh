#!/bin/bash
input="seeds_ffuf.txt"
while IFS= read -r line;
do
	ffuf -x http://127.0.0.1:8180 -w fuzzing_ga.txt $line
done < $input




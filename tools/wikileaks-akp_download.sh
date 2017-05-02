#!/bin/bash

# curl -OJL https://wikileaks.org/dnc-emails//get/<id-here>
# IDs range from [1, 407637]

OUTPUT_FILE="akpdownload.log"
RETRY_TIMEOUT=1
RETRY_COUNT=0

rm -rf eml output $OUTPUT_FILE

exec {FD}>$OUTPUT_FILE

FD_PATH="/dev/fd/$FD"

mkdir eml output
cd eml
mkdir tmp
cd tmp

i=0
r=$RETRY_COUNT

while ((i <= 407637)); do
	let i=i+1
	echo "Downloading $i..." | tee -a $FD_PATH
	curl -OJL "https://wikileaks.org/akp-emails//get/$i" > "../../output/$i.stdout" 2> "../../output/$i.stderr"
	CURLRET=$?

	if [ $CURLRET -ne 0 ]; then
		rm -rf *
		echo " * Failed to download: cURL returned $CURLRET. See output/$i.stderr for more information." | tee -a $FD_PATH
		continue
	fi

	EMLFILE=`ls -1 | head -1`

	EXT=${EMLFILE,,}
	EXT=${EXT##*.}

	r=$RETRY_COUNT
	sleep $RETRY_TIMEOUT

	OUTFILE=`printf "%05d" $i`_$EMLFILE
	mv -- "$EMLFILE" "../$OUTFILE"
done

cd ..
rm -rf tmp

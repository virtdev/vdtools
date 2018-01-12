#!/bin/bash
CWD=`readlink -f $0`
DIR=`dirname $CWD`
HOME=`dirname $DIR`
BIN=$HOME/bin
CMD_CREATE=$BIN/create

echo "Creating devices..."
DRIVERS=('Blob')
for i in ${DRIVERS[*]}; do
    device=`$CMD_CREATE -t $i`
    echo "device=$device"
    echo "$i passed"
done

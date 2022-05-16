#!/bin/sh
MONITORDIR="/home/pi/Results"

inotifywait -m -r -e create --format '%w%f' "${MONITORDIR}" | while read NEWFILE
do
    es=$(date +'%s')
    case "$NEWFILE" in
    *.hs)
    if [[ ${fileMap[$NEWFILE]} != $es ]];then
       sdiff = $((es-$fileMap[$NEWFILE]:-0}))
       fileMap[$NEWFILE]=$es
       ((sdiff < 3)) && continue
       ghc -fno-code $NEWFILE
       echo File directory is $NEWFILE
       python3 /home/pi/Scripts/test.py "${NEWFILE// /_}";
    fi
    ;;
    esac
    #xdotool key shift+F12
    #xdotool key shift+F10
done

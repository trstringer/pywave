#!/bin/bash

CACHE_FILE="/home/trstringer/.pywavecache"
CACHE_OUTPUT="/home/trstringer/.pywaveout"

if [[ ! -f "$CACHE_FILE" || ! -f "$CACHE_OUTPUT" ]]; then
    date +%s > "$CACHE_FILE"
    OUTPUT=$(pywave -s 44098 -w IOSN3 -p)
    echo "$OUTPUT" > "$CACHE_OUTPUT"
    echo "$OUTPUT"
else
    CURRENT_DATE="$(date +%s)"
    PREVIOUS_DATE="$(cat $CACHE_FILE)"
    PREVIOUS_ADJUSTED=$(( $PREVIOUS_DATE + 300 ))
    DATE_DIFF=$(( $CURRENT_DATE - $PREVIOUS_ADJUSTED ))
    if [[ $DATE_DIFF -gt 0 ]]; then
        date +%s > "$CACHE_FILE"
        OUTPUT=$(pywave -s 44098 -w IOSN3 -p)
        echo "$OUTPUT" > "$CACHE_OUTPUT"
        echo "$OUTPUT"
    else
        cat "$CACHE_OUTPUT"
    fi
fi


#!/bin/bash -x
KEEPERS='(19 JAN|16 FEB|15 MAR|20 APR|18 MAY|15 JUN)'

JUNK=$(influx query  < get-all-exps.flux  | tail -n +5 | grep -vE "$KEEPERS")

IFS=$'\n'
for j in $JUNK; do
  TRIMMED=$(echo "$j" | xargs)
  influx delete --bucket main \
    --start '1970-01-01T00:00:00Z' \
    --stop $(date +"%Y-%m-%dT%H:%M:%SZ") \
    --predicate '_measurement="options" AND exp='\"$TRIMMED\"''
done

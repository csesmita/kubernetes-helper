#!/bin/bash
declare -a arr=("caelum-105" "caelum-213" "caelum-208" "caelum-205" "caelum-204" "caelum-307" "caelum-306" "caelum-305" "caelum-304" "caelum-303" "caelum-302" "caelum-413" "caelum-513" "caelum-508" "caelum-507" "caelum-506" "caelum-505" "caelum-504" "caelum-503" "caelum-502" "caelum-608")
for node in "${arr[@]}"
do
    yes | ssh $node "/bin/sh -s" < worker-reset.sh
done

#!/bin/bash
for f in * 
do
    newfname=nodup/$f
    sort $f | uniq > $newfname
done

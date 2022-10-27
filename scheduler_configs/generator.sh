#!/bin/bash
for i in {103..150}
do
    filename=scheduler$i.yaml
    sed "s/scheduler2/scheduler$i/g" scheduler2.yaml  > $filename
done

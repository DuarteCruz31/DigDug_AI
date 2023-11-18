#!/bin/bash

# apaga ficheiro antigo se existir
rm -f scores.txt

while true; do
    python3 andre.py
    python3 media.py
done

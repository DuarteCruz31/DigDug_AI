#!/bin/bash

# apaga ficheiro antigo se existir
rm -f scores.txt

while true; do
    python andre.py
    python media.py
done

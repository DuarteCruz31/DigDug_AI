#!/bin/bash

# apaga ficheiro antigo se existir
rm -f ./coisas/scores.txt

while true; do
    python3 student.py
    python3 ./coisas/media.py
done

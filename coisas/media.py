# abrir fichero txt
f = open("scores.txt", "r")
# calcular media de pontos
total = 0
count = 0
for line in f:
    total += int(line.split()[1])
    count += 1
print(total / count)
f.close()
# abrir fichero txt
f = open("./coisas/scores.txt", "r")
# calcular media de pontos
total = 0
count = 0
for line in f:
    total += int(line.split()[1])
    count += 1
print("Média:", total / count)
print("------------------")
f.close()

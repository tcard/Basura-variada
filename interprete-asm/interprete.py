# -*- coding: UTF-8 -*-

import sys

mem = {}
reg = {	"$0":0x00,
				"$1":0x00,
				"$2":0x00,
				"$3":0x00,
				"$4":0x00,
				"$5":0x00,
				"$6":0x00,
				"$7":0x00,
			}
busio = 0x00

archivo = open(sys.argv[1])

debug = False
try:
	debug = sys.argv[2]
	if debug == "--debug":
		debug = True
except:
	pass
	
flags = {}

PC = 0xA0 # El programa se almacena en la segunda mitad de la memoria
for fila in archivo: # Preprocesador
	fila = fila.strip()
	try:
		if fila[-1] == ':': # Flag
			flags[fila[0:-1]] = PC
		elif fila[0] == '.': # Guardar en memoria
			i = fila.split()
			if(i[0]) == "BUSIO":
				busio = i[3]
			else:
				mem[int(i[1], 16)] = i[3]
		elif fila == "\n":
			pass
		elif fila[0:2] == "--":
			pass
		else:
			mem[PC] = fila
			PC = PC + 1
	except IndexError:
		pass
	
mem[PC] = "STOP"
PC = 0xA0
	
while (mem[PC] != "STOP"):
	if debug:
		print mem[PC]
		
	i = mem[PC].split()
		
	if i[0] == "J":
		try:
			PC = flags[i[1]]
		except:
			PC = i[1]
			
	elif i[0] == "JGT":
		if int(reg[i[1][0:-1]]) > int(reg[i[2][0:-1]]):
			try:
				PC = flags[i[3]]
			except:
				PC = PC + 1 + int(i[3], 16)
		else:
			PC = PC + 1
			
	elif i[0] == "ADDi":
		reg[i[1][0:-1]] = int(reg[i[1][0:-1]]) + int(i[2], 16)
		PC = PC + 1
		
	elif i[0] == "SUBi":
		reg[i[1][0:-1]] = int(reg[i[1][0:-1]]) - int(i[2], 16)
		PC = PC + 1
		
	elif i[0] == "ADDd":
		reg[i[1][0:-1]] = int(reg[i[1][0:-1]]) + int(reg[i[2]])
		PC = PC + 1
		
	elif i[0] == "SUBd":
		reg[i[1][0:-1]] = int(reg[i[1][0:-1]]) - int(reg[i[2]])
		PC = PC + 1
		
	elif i[0] == "ADDn":
		reg[i[1][0:-1]] = int(reg[i[1][0:-1]]) + int(mem[int(mem[int(i[2], 16)],16)])
		PC = PC + 1
		
	elif i[0] == "SUBn":
		reg[i[1][0:-1]] = int(reg[i[1][0:-1]]) - int(mem[int(mem[int(i[2], 16)],16)])
		PC = PC + 1
		
	elif i[0] == "RSH":
		reg[i[1]] = int(reg[i[1]]) >> 1
		PC = PC + 1
	
	elif i[0] == "LSH":
		reg[i[1]] = int(reg[i[1]]) << 1
		PC = PC + 1
		
	elif i[0] == "LD":
		reg[i[1][0:-1]] = int(mem[int(i[2], 16)], 16)
		PC = PC + 1
		
	elif i[0] == "ST":
		mem[int(i[2], 16)] = hex(reg[i[1][0:-1]])
		PC = PC + 1
		
	elif i[0] == "IN":
		reg[i[1]] = busio
		PC = PC + 1
		
	elif i[0] == "OUT":
		busio = reg[i[1]]
		PC = PC + 1
		
	else:
		raise Exception("No se reconoció la instrucción: " + i[0])
	
	if debug:
			print "MEMORIA:\n"
			for k,v in mem.items():
				print repr(hex(int(k)).upper()).rjust(2), "=".rjust(3), repr(v).rjust(4)

			print "\nREGISTROS:\n"
			for k,v in reg.items():
				print repr(k).rjust(2), "=".rjust(3),
				print repr(v).rjust(4), repr(hex(v).upper()).rjust(4)

			print "\nBUSIO: " + repr(busio)
			
			raw_input("Siguiente: [ENTER]")
			
if not debug:
	print "MEMORIA:\n"
	for k,v in mem.items():
		print repr(hex(int(k)).upper()).rjust(2), "=".rjust(3), repr(v).rjust(4)

	print "\nREGISTROS:\n"
	for k,v in reg.items():
		print repr(k).rjust(2), "=".rjust(3), repr(v).rjust(4), repr(hex(v).upper()).rjust(4)

	print "\nBUSIO: " + repr(busio)
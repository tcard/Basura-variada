# -*- coding: UTF-8 -*-

import sys
import re

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
			elif int(i[1], 16) > 255:
				raise Exception("Dirección de memoria inválida: " + i[1])
			else:
				mem[int(i[1], 16)] = i[3]
		elif fila == "\n":
			pass
		elif fila[0:2] == "--":
			pass
		else:
			mem[PC] = fila.split('--')[0]
			PC = PC + 1
	except IndexError:
		pass
	
mem[PC] = "STOP"
PC = 0xA0
	
while (mem[PC] != "STOP"):
	if debug:
		print mem[PC]
	
	match = re.match("^J ([a-zA-Z0-9]+)\s*$", mem[PC])
	if match:
		print mem[PC]
		try:
			PC = flags[match.group(1)]
		except:
			PC = match.group(1)
	
	elif re.match("^JGT (\$[1-7]), ?(\$[0-7]), ?([a-zA-Z0-9]+)\s*$", mem[PC]):
		match = re.match("^JGT (\$[1-7]), ?(\$[0-7]), ?([a-zA-Z0-9]+)\s*$", mem[PC])
		if int(reg[match.group(1)]) > int(reg[match.group(2)]):
			try:
				PC = flags[match.group(3)]
			except:
				PC = PC + 1 + int(match.group(3), 16)
		else:
			PC = PC + 1
			
	elif re.match("^ADDi (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC]):
		match = re.match("^ADDi (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) + int(match.group(2), 16)
		PC = PC + 1
		
	elif re.match("^SUBi (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC]):
		match = re.match("^SUBi (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) - int(match.group(2), 16)
		PC = PC + 1
	
	elif re.match("^ADDd (\$[1-7]), ?(\$[0-7])\s*$", mem[PC]):
		match = re.match("^ADDd (\$[1-7]), ?(\$[0-7])\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) + int(int(reg[match.group(2)]))
		PC = PC + 1
		
	elif re.match("^SUBd (\$[1-7]), ?(\$[0-7])\s*$", mem[PC]):
		match = re.match("^SUBd (\$[1-7]), ?(\$[0-7])\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) - int(int(reg[match.group(2)]))
		PC = PC + 1
		
	elif re.match("^ADDn (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC]):
		match = re.match("^ADDn (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) + int(mem[int(mem[int(match.group(2), 16)],16)])
		PC = PC + 1
		
	elif re.match("^SUBn (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC]):
		match = re.match("^SUBn (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) - int(mem[int(mem[int(match.group(2), 16)],16)])
		PC = PC + 1
	
	elif re.match("^RSH (\$[1-7])\s*$", mem[PC]):
		match = re.match("^RSH (\$[1-7])\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) >> 1
		PC = PC + 1
		
	elif re.match("^LSH (\$[1-7])\s*$", mem[PC]):
		match = re.match("^RSH (\$[1-7])\s*$", mem[PC])
		reg[match.group(1)] = int(reg[match.group(1)]) << 1
		PC = PC + 1
	
	elif re.match("^LD (\$[0-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC]):
		match = re.match("^LD (\$[0-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC])
		reg[match.group(1)] = int(mem[int(match.group(2), 16)], 16)
		PC = PC + 1
		
	elif re.match("^ST (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC]):
		match = re.match("^ST (\$[1-7]), ?([0-9a-fA-F]{1,2})\s*$", mem[PC])
		if (int(match.group(2), 16) < 64 or int(match.group(2), 16) > 255):
			raise Exception("Dirección de memoria inválida: " + match.group(2))
		mem[int(match.group(2), 16)] = hex(reg[match.group(1)])
		PC = PC + 1
	
	elif re.match("^IN (\$[1-7])\s*$", mem[PC]):
		match = re.match("^IN (\$[1-7])\s*$", mem[PC])
		reg[match.group(1)] = busio
		PC = PC + 1
		
	elif re.match("^OUT (\$[0-7])\s*$", mem[PC]):
		match = re.match("^OUT (\$[0-7])\s*$", mem[PC])
		busio = reg[match.group(1)]
		PC = PC + 1
		
	else:
		raise Exception("No se reconoció la instrucción: " + mem[PC])
	
	if debug:
			print "MEMORIA:\n"
			for k,v in mem.items():
				print repr(hex(int(k))).rjust(2), "=".rjust(3), repr(v).rjust(4)

			print "\nREGISTROS:\n"
			for k,v in reg.items():
				print repr(k).rjust(2), "=".rjust(3),
				print repr(v).rjust(4), repr(hex(v)).rjust(4)

			print "\nBUSIO: " + repr(busio)
			
			raw_input("Siguiente: [ENTER]")
			
			
if not debug:
	print "MEMORIA:\n"
	for k,v in mem.items():
		print repr(hex(int(k))).rjust(2), "=".rjust(3), repr(v).rjust(4)

	print "\nREGISTROS:\n"
	for k,v in reg.items():
		print repr(k).rjust(2), "=".rjust(3), repr(v).rjust(4), repr(hex(v)).rjust(4)

	print "\nBUSIO: " + repr(busio)
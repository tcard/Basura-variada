# -*- coding: UTF-8 -*-

import sys
import os
import re

mem = {}
reg = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
ops = {
	'J':	0b11100,
	'JGT':	0b11101,
	'ADDi':	0b00000,
	'SUBi':	0b00001,
	'ADDd':	0b01000,
	'SUBd':	0b01001,
	'ADDn':	0b10000,
	'SUBn':	0b10001,
	'RSH':	0b00101,
	'LSH':	0b00100,
	'LD':	0b11000,
	'ST':	0b11001,
	'IN':	0b11010,
	'OUT':	0b11011,
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
resolveFlags = []

PC = 0xA0 # El programa se almacena en la segunda mitad de la memoria
for fila in archivo: # Preprocesador
	fila = fila.strip()
	try:
		if fila[-1] == ':': # Flag
			flags[fila[0:-1]] = PC
		elif fila[0] == '.': # Guardar en memoria
			i = fila.split()
			if int(i[1], 16) > 255:
				raise Exception("Dirección de memoria inválida: " + i[1])
			else:
				mem[int(i[1], 16)] = int(i[3], 16)
		elif fila == "\n":
			pass
		elif fila[0:2] == "--":
			pass
		else:
			ins = fila.split('--')[0]
			
			match = re.match("^J ([a-zA-Z0-9]+)\s*$", ins)
			if match:
				mem[PC] = ops['J'] << 11
				resolveFlags.append((PC, match.group(1)))

			elif re.match("^JGT \$([1-7]), ?\$([0-7]), ?([a-zA-Z0-9]+)\s*$", ins):
				match = re.match("^JGT \$([1-7]), ?\$([0-7]), ?([a-zA-Z0-9]+)\s*$", ins)
				mem[PC] = ops['JGT'] << 11 | \
					(int(match.group(1)) & 0b111) << 8 | \
					(int(match.group(2)) & 0b111) << 5
				PC = PC + 1
				try:
					mem[PC] = int(match.group(3), 16)
				except:
					resolveFlags.append((PC, match.group(3), (lambda myPC: lambda addr: addr-myPC)(PC)))
					
			elif re.match("^ADDi \$([1-7]), ?([0-9a-fA-F]{1,4})\s*$", ins):
				match = re.match("^ADDi \$([1-7]), ?([0-9a-fA-F]{1,4})\s*$", ins)
				mem[PC] = ops['ADDi'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				PC = PC + 1
				mem[PC] = int(match.group(2), 16)
				
			elif re.match("^SUBi \$([1-7]), ?([0-9a-fA-F]{1,4})\s*$", ins):
				match = re.match("^SUBi \$([1-7]), ?([0-9a-fA-F]{1,4})\s*$", ins)
				mem[PC] = ops['SUBi'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				PC = PC + 1
				mem[PC] = int(match.group(2), 16)

			elif re.match("^ADDd \$([1-7]), ?\$([0-7])\s*$", ins):
				match = re.match("^ADDd \$([1-7]), ?\$([0-7])\s*$", ins)
				mem[PC] = ops['ADDd'] << 11 | \
					(int(match.group(1)) & 0b111) << 8 | \
					(int(match.group(2)) & 0b111) << 5
				
			elif re.match("^SUBd \$([1-7]), ?\$([0-7])\s*$", ins):
				match = re.match("^SUBd \$([1-7]), ?\$([0-7])\s*$", ins)
				mem[PC] = ops['SUBd'] << 11 | \
					(int(match.group(1)) & 0b111) << 8 | \
					(int(match.group(2)) & 0b111) << 5
				
			elif re.match("^ADDn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins):
				match = re.match("^ADDn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins)
				mem[PC] = ops['ADDn'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				resolveFlags.append((PC, match.group(2)))
				
			elif re.match("^SUBn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins):
				match = re.match("^SUBn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins)
				mem[PC] = ops['SUBn'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				resolveFlags.append((PC, match.group(2)))

			elif re.match("^RSH \$([1-7])\s*$", ins):
				match = re.match("^RSH \$([1-7])\s*$", ins)
				mem[PC] = ops['RSH'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				
			elif re.match("^LSH \$([1-7])\s*$", ins):
				match = re.match("^RSH \$([1-7])\s*$", ins)
				mem[PC] = ops['LSH'] << 11 | \
					(int(match.group(1)) & 0b111) << 8

			elif re.match("^LD \$([0-7]), ?([a-zA-Z0-9]+)\s*$", ins):
				match = re.match("^LD \$([0-7]), ?([0-9a-fA-F]{1,2})\s*$", ins)
				mem[PC] = ops['LD'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				resolveFlags.append((PC, match.group(2)))
				
			elif re.match("^ST \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins):
				match = re.match("^ST \$([1-7]), ?([0-9a-fA-F]{1,2})\s*$", ins)
				mem[PC] = ops['ST'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				resolveFlags.append((PC, match.group(2)))

			elif re.match("^IN \$([1-7])\s*$", ins):
				match = re.match("^IN \$([1-7])\s*$", ins)
				mem[PC] = ops['IN'] << 11 | \
					(int(match.group(1)) & 0b111) << 8
				
			elif re.match("^OUT \$([0-7])\s*$", ins):
				match = re.match("^OUT \$([0-7])\s*$", ins)
				mem[PC] = ops['OUT'] << 11 | \
					(int(match.group(1)) & 0b111) << 8

			PC = PC + 1
	except IndexError:
		pass

for rf in resolveFlags:
	to, fl = rf[0], rf[1]
	res = 0
	try:
		res = int(fl, 16)
	except:
		try:
			res = flags[fl]
		except:
			raise Exception("No existe flag: "+fl)
	if not to in mem:
		mem[to] = 0
	antes = mem[to]
	if len(rf) > 2:
		mem[to] = mem[to] | (rf[2](res & 0xFF) & 0xFF)
		print "resolved", hex(rf[2](res & 0xFF) & 0xFF), "for flag", fl, "into", hex(to)
	else:
		mem[to] = mem[to] | (res & 0xFF)
		if debug:
			print "resolved", hex(res & 0xFF), "for flag", fl, "into", hex(to)
	despues = mem[to]

STOP = 0xFFFF
mem[PC] = STOP
PC = 0xA0

print 

def print_memoria(dir=None, omitEmpty=False):
	if dir is None:
		dir = range(0, 256)
	else:
		dir = [dir]
	for i in dir:
		if not i in mem:
			if not omitEmpty:
				print hex(i)[2:].upper(), "(no)"
			continue
		s = "%016d" % int(bin(mem[i])[2:])
		op = mem[i] >> 11
		print hex(i)[2:].upper(), ':', s[:5], s[5:8], s[8:11], s[11:], mem[i], \
			chr(mem[i]) if mem[i] < 256 else '.', reduce(lambda x, y: y if ops[y] == op else x, ops.keys(), ''), \
			reduce(lambda x, y: y if flags[y] == i else x, flags.keys(), '')

if debug:
	print_memoria()
print

while (mem[PC] != STOP):
	op = mem[PC] >> 11
	reg1 = mem[PC] >> 8 & 0b111
	reg2 = mem[PC] >> 5 & 0b111
	dirl = mem[PC] & 0xFF

	if debug:
		print_memoria(PC)

	if op == ops['J']:
		PC = dirl

	elif op == ops['JGT']:
		if debug:
			print 'mayor', reg1, reg[reg1], reg2, reg[reg2], reg[reg1] > reg[reg2], hex(PC + 1 + mem[PC+1])
		if reg[reg1] > reg[reg2]:
			PC = PC + 1 + mem[PC+1]
		else:
			PC = PC + 2

	elif op == ops['ADDi']:
		reg[reg1] = reg[reg1] + mem[PC + 1]
		PC = PC + 2

	elif op == ops['SUBi']:
		reg[reg1] = reg[reg1] - mem[PC + 1]
		PC = PC + 2

	elif op == ops['ADDd']:
		reg[reg1] = reg[reg1] + reg[reg2]
		PC = PC + 1

	elif op == ops['SUBd']:
		reg[reg1] = reg[reg1] - reg[reg2]
		PC = PC + 1
		
	elif op == ops['ADDn']:
		reg[reg1] = reg[reg1] + mem[mem[dirl]]
		PC = PC + 1

	elif op == ops['SUBn']:
		reg[reg1] = reg[reg1] - mem[mem[dirl]]
		PC = PC + 1

	elif op == ops['LSH']:
		reg[reg1] = reg[reg1] << 1
		PC = PC + 1
	
	elif op == ops['RSH']:
		reg[reg1] = reg[reg1] >> 1
		PC = PC + 1

	elif op == ops['LD']:
		reg[reg1] = mem[dirl]
		PC = PC + 1

	elif op == ops['ST']:
		if (dirl < 64 or dirl > 255):
			raise Exception("Dirección de memoria inválida: " + match.group(2))
		mem[dirl] = reg[reg1]
		PC = PC + 1
	
	elif op == ops['IN']:
		b = os.sys.stdin.read(1)
		if b != '':
			busio = ord(b)
			reg[reg1] = busio
		PC = PC + 1

	elif op == ops['OUT']:
		busio = reg[reg1]
		print os.sys.stdout.write(chr(busio))
		PC = PC + 1
		
	else:
		raise Exception("No se reconoció la instrucción: " + mem[PC])
	
	if debug:
		print "MEMORIA:\n"
		print_memoria(omitEmpty=True)

		print "\nREGISTROS:\n"
		k = 0
		for v in reg:
			print repr(k).rjust(2), "=".rjust(3), repr(v).rjust(4), repr(hex(v)).rjust(4)
			k += 1

		print "\nBUSIO: " + repr(busio)
		
		raw_input("Siguiente: [ENTER]")
			
			
if not debug:
	print "MEMORIA:\n"
	print_memoria(omitEmpty=True)

	print "\nREGISTROS:\n"
	k = 0
	for v in reg:
		print repr(k).rjust(2), "=".rjust(3), repr(v).rjust(4), repr(hex(v)).rjust(4)
		k += 1

	print "\nBUSIO: " + repr(busio)
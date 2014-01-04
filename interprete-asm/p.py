# -*- coding: UTF-8 -*-

import re
mem = {}
PC = 0
flags = {'test': 0xAA}
op = {
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

ins = "LD $3, 3F"
match = re.match("^J ([a-zA-Z0-9]+)\s*$", ins)
if match:
	mem[PC] = op['J'] << 11 | \
	(flags[match.group(1)] if match.group(1) in flags else int(match.group(1), 16))

elif re.match("^JGT \$([1-7]), ?\$([0-7]), ?([a-zA-Z0-9]+)\s*$", ins):
	match = re.match("^JGT \$([1-7]), ?\$([0-7]), ?([a-zA-Z0-9]+)\s*$", ins)
	mem[PC] = op['JGT'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(int(match.group(2)) & 0b111) << 5
	PC = PC + 1
	mem[PC] = (flags[match.group(3)] if match.group(3) in flags else int(match.group(3), 16))
		
elif re.match("^ADDi \$([1-7]), ?([0-9a-fA-F]{1,2})\s*$", ins):
	match = re.match("^ADDi \$([1-7]), ?([0-9a-fA-F]{1,2})\s*$", ins)
	mem[PC] = op['ADDi'] << 11 | \
		(int(match.group(1)) & 0b111) << 8
	PC = PC + 1
	mem[PC] = int(match.group(2), 16)
	
elif re.match("^SUBi \$([1-7]), ?([0-9a-fA-F]{1,2})\s*$", ins):
	match = re.match("^SUBi \$([1-7]), ?([0-9a-fA-F]{1,2})\s*$", ins)
	mem[PC] = op['SUBi'] << 11 | \
		(int(match.group(1)) & 0b111) << 8
	PC = PC + 1
	mem[PC] = int(match.group(2), 16)

elif re.match("^ADDd \$([1-7]), ?\$([0-7])\s*$", ins):
	match = re.match("^ADDd \$([1-7]), ?\$([0-7])\s*$", ins)
	mem[PC] = op['ADDd'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(int(match.group(2)) & 0b111) << 5
	
elif re.match("^SUBd \$([1-7]), ?\$([0-7])\s*$", ins):
	match = re.match("^SUBd \$([1-7]), ?\$([0-7])\s*$", ins)
	mem[PC] = op['SUBd'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(int(match.group(2)) & 0b111) << 5
	
elif re.match("^ADDn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins):
	match = re.match("^ADDn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins)
	mem[PC] = op['ADDn'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(flags[match.group(2)] if match.group(2) in flags else int(match.group(2), 16))
	
elif re.match("^SUBn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins):
	match = re.match("^SUBn \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins)
	mem[PC] = op['SUBn'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(flags[match.group(2)] if match.group(2) in flags else int(match.group(2), 16))

elif re.match("^RSH \$([1-7])\s*$", ins):
	match = re.match("^RSH \$([1-7])\s*$", ins)
	mem[PC] = op['RSH'] << 11 | \
		(int(match.group(1)) & 0b111) << 8
	
elif re.match("^LSH \$([1-7])\s*$", ins):
	match = re.match("^RSH \$([1-7])\s*$", ins)
	mem[PC] = op['LSH'] << 11 | \
		(int(match.group(1)) & 0b111) << 8

elif re.match("^LD \$([0-7]), ?([a-zA-Z0-9]+)\s*$", ins):
	match = re.match("^LD \$([0-7]), ?([0-9a-fA-F]{1,2})\s*$", ins)
	mem[PC] = op['LD'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(flags[match.group(2)] if match.group(2) in flags else int(match.group(2), 16))
	
elif re.match("^ST \$([1-7]), ?([a-zA-Z0-9]+)\s*$", ins):
	match = re.match("^ST \$([1-7]), ?([0-9a-fA-F]{1,2})\s*$", ins)
	mem[PC] = op['ST'] << 11 | \
		(int(match.group(1)) & 0b111) << 8 | \
		(flags[match.group(2)] if match.group(2) in flags else int(match.group(2), 16))

elif re.match("^IN \$([1-7])\s*$", ins):
	match = re.match("^IN \$([1-7])\s*$", ins)
	mem[PC] = op['IN'] << 11 | \
		(int(match.group(1)) & 0b111) << 8
	
elif re.match("^OUT \$([0-7])\s*$", ins):
	match = re.match("^OUT \$([0-7])\s*$", ins)
	mem[PC] = op['OUT'] << 11 | \
		(int(match.group(1)) & 0b111) << 8

PC = PC + 1

print ins
for k, v in mem.items():
	s = "%016d" % int(bin(v)[2:])
	print k, s[:5], s[5:8], s[8:11], s[11:]
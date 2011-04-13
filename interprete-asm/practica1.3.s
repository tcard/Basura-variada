. 3E = 50
. 3F = 05
-- A
. 50 = 01
. 51 = 02
. 52 = 03
. 53 = 06
. 54 = 02
-- B
. 55 = 02
. 56 = 01
. 57 = 05
. 58 = 04
. 59 = 07

LD $3, 3F			-- $3 = longitud de los vectores
LD $1, 3E 			-- $1 = *A[0]
LD $2, 3E		
ADDd $2, $3			-- $2 = *B[0]
SUBd $6, $6			-- $6 = 0

comprobarCondicion:

JGT $3, $0, bucle
J despuesDeBucle

bucle:

SUBd $4, $4
ST $1, 5A 
ADDn $4, 5A 		-- $4 = A[i]
SUBd $5, $5
ST $2, 5A
ADDn $5, 5A			-- $5 = B[i]

JGT $4, $5, AmayorqueB
SUBd $5, $4			-- $5 = |A[i] - B[i]|
SUBd $4, $4
ADDd $4, $5			-- $4 = $5
J despues

AmayorqueB:
SUBd $4, $5			-- $4 = |A[i] - B[i]|

despues:
ADDd $6, $4			-- $6 += $4
SUBi $3, 01
ADDi $1, 01
ADDi $2, 01

J comprobarCondicion

despuesDeBucle:
ST $6, 40
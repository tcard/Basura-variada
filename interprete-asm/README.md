Un sencillo intérprete para el ensamblador que nos han dado en clase.

`python interprete.py archivo` Interpreta el archivo `archivo`, devolviendo al final el estado de la memoria, de los registros y de BUSIO.

`python interprete.py archivo --debug` Interpreta cada instrucción paso a paso, mostrando el estado interno en cada paso.

Me he tomado algunas libertades:

- Soporte para flags. `J flag` y `JGT ra, rb, flag` saltarán a `flag:`, aunque no esté así especificado en el guión de la práctica.
- Comentarios: empiezan por `--`.
- Los registros van del $0 al $7. La memoria es infinita, se expresa con un número hexadecimal de dos cifras (ej. 3F). El programa generado se guarda también en memoria, a partir de la posición A0, así que mejor no usarla a partir de ahí. Todo se puede leer y escribir, así que cuidado.
- Para tener un estado inicial de memoria antes de ejecutar el programa, hay que declararla de esta forma: `. DIR = Valor`. DIR es una dirección hexadecimal, Valor puede ser cualquier cosa.
- Si una posición de memoria no está inicializada, bien con la sintaxis anterior, bien con ST, intentar leerla provocará un error. 

# Estrategias

Boletos de 6. Un caso es `v` números, garantía `t` si salen `m`. La tabla es la de Lotoideas para Primitiva, Bonoloto, Lototurf y Eurodreams, columnas de 6 y de 5. `python records.py` las prueba de menos sorteos a más.

## Grupos

Parte los `v` números en grupos iguales de `s`. `s` divide a 6 y a `v`. Cada apuesta junta `r = 6/s` grupos enteros. Vale cuando, en cualquier reparto de `m` bolas, los `r` grupos más llenos suman al menos `t`.

12 al 4 si 6: cuatro grupos de 3, y las seis parejas. En un sorteo de 6, los dos grupos más llenos suman al menos 4. Son 6 apuestas, el récord, y el programa recorre los 924 sorteos.

## Corte

Parte `v` en `a + b`. Ninguna apuesta mezcla los dos lados. Si en `a` caen al menos `j`, responde la reducida de `a` (garantía `t` si `j`). Si no, en `b` caen al menos `m - j + 1`.

Sirve para 3 si 6 (`j = 3`: un lado al 3 si 3 y el otro al 3 si 4) y para 3 si 5 (dos lados al 3 si 3). No sirve para 4 si 6 ni para 5 si 6: un 3+3 deja los dos lados por debajo de la garantía.

49 al 3 si 6 es el corte 22+27: 77+86 = 163.

## Steiner

22 números, 3 si 3, 77 apuestas. Cada trío está en una sola. Sale del código de Golay (el diseño de Witt). 77×20 = 1540, así que no cabe en menos.

## Patrón 27

27 números, 3 si 4, 86 apuestas. Cada cuarteto corta alguna en 3 o más. Es la pieza que, con el Steiner, da el 163. El salto desde las 165 de hace años está aquí: el 22 ya era justo.

## Patrón 24

24 números, 4 si 6, 143 apuestas. No es un corte. El programa las pasa por los 134596 sorteos.

## Avaro

En un caso pequeño, se toma la apuesta que tapa más sorteos aún descubiertos, y se repite. Solo se queda si sale más corta que grupos o corte.

## Ventana

Fuerza bruta es el recocido. Estrategia, en la ventana, son los grupos y después el sorteo suelto. Ambas hace las dos. El corte, el Steiner y los dos patrones los construye `records.py`.

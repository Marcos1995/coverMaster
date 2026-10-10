# Lotto Optimizer V3.10

Lectura de `LottoOptimizerV3_10.py` (un solo fichero). El programa no se parte en módulos.

## Qué hace

Construye una lista de apuestas de `k` números elegidos entre `1..v` y la retoca hasta que cubra la mayor parte posible de una muestra de sorteos. Un sorteo de la muestra (`m` números) cuenta como cubierto si alguna apuesta comparte con él al menos `t` números.

Ctrl+C durante la optimización escribe un único `.txt` con la lista que logró la cobertura más alta de la sesión, no con la lista que había en ese momento.

La cobertura es un porcentaje sobre esa muestra. No es una garantía matemática sobre todos los sorteos posibles de la lotería.

## Qué pide por teclado

`main` (línea 708), en este orden:

1. `v`, `k`, `t`, `m`. Si un dato no vale, lo vuelve a pedir. `v >= 1`, `k` y `m` entre 1 y `v`, `t` entre 1 y `min(k, m)`. Un texto que no es un entero también se repite.
2. ¿Grupos? Si `s`, cuántos (al menos uno) y, por cada uno, números entre 1 y `v`, mínimo y máximo. El mínimo va de 0 a `k` y no puede superar al máximo. Un grupo vacío o con números fuera de rango se repite.
3. Cuántas apuestas generar (al menos 1).
4. Tras guardar: ¿sustituir `1..v` por números reales?

Ctrl+C durante un `input` no lo atrapa el `except` de `main`. Ctrl+C durante la generación o la optimización sí está capturado dentro de esos métodos.

## Parámetros que no salen en el menú

`Configuracion` (línea 79):

| Campo | Valor | Uso |
|---|---|---|
| `universo_size` | 50 000 | Tamaño de la muestra de sorteos. |
| `condiciones_grupos` | lista vacía | Tope de aciertos por grupo, si el usuario define grupos. |

## Representación en bits

Cada número `n` es el bit `n - 1`. Una apuesta es un entero con esos bits puestos.

`BitUtils` (línea 88):

- `lista_a_bits` suma `1 << (n - 1)`. Cachea por la tupla ordenada, hasta 100 000 entradas.
- `bits_a_lista` devuelve los números cuyo bit está puesto. Misma caché, y devuelve una copia si ya estaba guardada.
- `contar_coincidencias` es el `bit_count` del AND.

Ejemplo: `{1, 2, 3}` → `0b111` = 7.

## Muestra de sorteos

Al crear `LottoOptimizerV3` (línea 137) se fabrican 50 000 sorteos: cada uno es `random.sample` de `m` números en `1..v`, pasado a bits. No hay semilla. Dos ejecuciones con los mismos datos no repiten la muestra ni la cobertura.

Cada sorteo es sin repetición por dentro. Entre los 50 000, el mismo sorteo puede salir más de una vez. `total_sorteos` es 50 000, no el número de combinaciones distintas.

A la vez se construye `por_numero[n]`: la lista de posiciones de la muestra que contienen el número `n`. Una mutación solo mira los sorteos del número que sale y del que entra. El resto no puede cambiar de intersección.

El espacio real de sorteos es C(v, m). Con v=49 y m=6 son 13 983 816 combinaciones. Subir la cobertura de la muestra no demuestra la misma cobertura fuera de ella.

`conteos[i]` es cuántas apuestas cubren el sorteo `i`. `cubiertos` es cuántos tienen `conteos[i] > 0`. Se actualiza solo cuando un conteo cruza de 0 a 1 o de 1 a 0.

## Cobertura

```text
cobertura = cubiertos / 50_000 * 100
```

Una apuesta extra que cubre un sorteo ya cubierto no la sube. Perder la única apuesta que cubría un sorteo sí la baja.

`t` no puede ser 0 ni mayor que `min(k, m)`, así que no se da el caso de cubrirlo todo por definición ni el de no poder cubrir nada.

## Generación

`generar_aleatorias` (línea 201) pide `cantidad` apuestas:

1. Saca `k` números al azar.
2. Si cumple todos los grupos, la añade y actualiza `conteos` y `cubiertos`.
3. Como mucho `cantidad * 2000` intentos.
4. Si no llegan, se queda con las válidas que haya. No mete apuestas que fallen un grupo.
5. Ctrl+C corta y sigue hacia la optimización con las que ya hay.

Cada apuesta aceptada recorre solo los sorteos que comparten algún número con ella. Con `t >= 1`, un sorteo sin números en común no puede quedar cubierto.

## Grupos

`CondicionGrupo` (línea 68) guarda números, mínimo, máximo y la máscara de bits de esos números.

`es_apuesta_valida_por_grupos` (línea 167) exige, en cada grupo, `min_aciertos <= aciertos <= max_aciertos`. Sin grupos, toda apuesta vale.

Se usa al generar y en cada mutación. Una mutación que se sale del mínimo o del máximo se rechaza siempre, sin la regla de Metropolis. La temperatura sí baja en ese ciclo, igual que cuando una mutación válida se rechaza.

## Optimización

`optimizar` (línea 275) no hace nada si no hay apuestas. Si las hay, copia la lista actual como récord y entra en un bucle hasta Ctrl+C. Cada vuelta es `_paso` (línea 256):

1. Elige una apuesta al azar.
2. La muta: quita un número y mete otro que no estuviera (`MotorMutaciones.mutar`, línea 125). Si `k == v` no hay hueco y devuelve la misma máscara; ese ciclo no cambia la lista.
3. Si la máscara nueva no cumple los grupos, no se evalúa.
4. Si los cumple, calcula la ganancia sobre los sorteos afectados.
5. La acepta si la ganancia es positiva, o si la temperatura sigue por encima de 0.0001 y un aleatorio cae bajo la curva de Metropolis.
6. Si la cobertura nueva supera el récord (estricto), guarda una copia de la lista de máscaras.
7. Multiplica la temperatura por 0.9995. También cuando la mutación se rechaza.

La condición exacta es:

```text
ganancia > 0
o (temperatura > 0.0001 y random() < exp(ganancia / temperatura))
```

- Ganancia positiva: se acepta siempre.
- Ganancia 0: `exp(0) = 1`, así que se acepta siempre mientras la temperatura supere 0.0001. El algoritmo pasea en meseta.
- Ganancia negativa: se acepta con probabilidad `exp(ganancia / temperatura)`. Con temperatura 1, una pérdida de 1 sorteo se acepta cerca del 37 % de las veces.

La temperatura nace en 1.0. Tras 18 417 ciclos baja de 0.0001. Desde el ciclo 18 418 solo entra una mutación con ganancia positiva. La temperatura se sigue imprimiendo, pero ya no interviene.

La línea de ciclos se redibuja cada 100 ciclos y también en el ciclo que bate el récord.

Ctrl+C no deshace la última mutación aceptada. El fichero sale del récord, que puede ser una lista anterior.

## Ganancia

`calcular_ganancia` (línea 225) cuenta sorteos de la muestra que pasan de cubierto a descubierto o al revés, y solo cuando la apuesta que se cambia es la única responsable.

Los sorteos que no contienen ni el número quitado ni el número puesto no se miran: su intersección no cambia.

Para cada sorteo afectado:

- La apuesta vieja lo cubría, la nueva no, y `conteos` era 1 → ganancia −1.
- La vieja no lo cubría, la nueva sí, y `conteos` era 0 → ganancia +1.
- Si otras apuestas ya lo cubrían, perder o repetir esa cobertura suma 0.

`aplicar_mutacion` (línea 244) resta la cobertura de la máscara vieja y suma la de la nueva, y sustituye la apuesta. El cambio de `cubiertos` en esa operación es exactamente la ganancia. No hay caché de ganancias: el resultado depende de `conteos`, y `conteos` cambia en cada aceptación.

## Récord y fichero

El récord es `mejor_cobertura` más `mejor_apuestas_bits`. Solo se sustituye cuando la cobertura sube.

`guardar_mejor_record` (línea 293):

- Si el récord está vacío y hay apuestas, copia las actuales.
- El porcentaje del nombre es el récord, o la cobertura actual si el récord sigue en 0.
- Nombre: `LOTTO_v{v}_k{k}_t{t}_{cobertura con 4 decimales}pct_{YYYYmmdd_HHMMSS}.txt`
- `m` no entra en el nombre.
- Cada línea es una apuesta, números a dos dígitos, ordenados. Las líneas van ordenadas entre sí.
- Se escribe en el directorio de trabajo, en UTF-8.

Ejemplo de línea: `01 07 12 23 35 41`

## Números reales

Paso opcional al final de `main`. `analizar_entrada_numeros` (línea 18) parte por espacios o comas, entiende un rango `inicio-fin` sin espacios (`1-12`), ignora tokens rotos y devuelve la lista ordenada y sin duplicados.

Si hay exactamente `v` números, el número abstracto `x` se sustituye por el elemento `x - 1` de esa lista ya ordenada. El 1 abstracto pasa a ser el menor número real introducido. El resultado es el mismo nombre con `_PERSONALIZADO` antes de `.txt`. Si el recuento no es `v`, no escribe nada.

`5, 10, 3` con `v = 3` queda `[3, 5, 10]`. Una apuesta `01 02` se guarda como `03 05`.

## Reducida récord de Lotoideas

`REDUCIDAS_LOTOIDEAS` guarda el enlace al zip, no las apuestas. La clave es `(v, k, t, m)`. En esa tabla `k` es 6, y «t si m» es la garantía publicada: si `m` números del sorteo caen dentro de los `v`, alguna apuesta comparte al menos `t`.

Si no hay grupos y la clave existe, el programa enseña el enlace y pregunta:

- `u` — descarga el zip y guarda esa lista tal cual. El archivo lleva `lotoideas` en el nombre.
- `m` — parte de esa lista e intenta subir la cobertura de la muestra. El récord solo se sustituye si la cobertura sube. Si no, el archivo es la lista de Lotoideas.

Con grupos no se usa el zip: la reducida publicada no conoce esos topes.

La ventana (`python LottoOptimizerV3_10.py --gui` o `dist\LottoOptimizerV3_10.exe`) pide los mismos datos. **Parar** guarda el mejor récord. El ejecutable lleva el mismo Python dentro: cada ciclo tarda lo mismo que la consola.

## Recorrido de una sesión

```text
main
  leer v, k, t, m  (repite si no valen)
  grupos opcionales
  si hay zip de Lotoideas y no hay grupos:
      u → guardar esa lista
      m → cargar esa lista y optimizar
           si la cobertura no sube, sigue siendo la de Lotoideas
  si no:
      LottoOptimizerV3
          50 000 sorteos al azar
          índice por número
      generar_aleatorias
      optimizar hasta Ctrl+C
      guardar_mejor_record
  mapeo opcional → _PERSONALIZADO.txt
  ENTER para salir
```

## Índice

| Símbolo | Línea | Papel |
|---|---|---|
| `analizar_entrada_numeros` | 18 | Grupos y números reales |
| `limpiar_pantalla` | 32 | Arranque y justo antes de optimizar |
| `leer_entero` | 36 | Entero, y lo repite si el texto no vale |
| `escribir_apuestas` | 53 | Escribe el `.txt` ordenado |
| `CondicionGrupo` | 68 | Máscara y topes del grupo |
| `Configuracion` | 79 | `v, k, t, m`, tamaño de muestra y grupos |
| `BitUtils` | 88 | Máscaras y popcount |
| `MotorMutaciones.mutar` | 125 | Quita un número y pone otro |
| `LottoOptimizerV3` | 136 | Muestra, índice, apuestas, conteos, récord |
| `cobertura` / `num_apuestas` | 158 / 164 | Porcentaje, a partir de `cubiertos`, y tamaño de la lista |
| `es_apuesta_valida_por_grupos` | 167 | Mínimo y máximo, en generación y en cada mutación |
| `generar_aleatorias` | 201 | Lista inicial, si no hay zip |
| `calcular_ganancia` | 225 | Sorteos que se ganan o se pierden |
| `aplicar_mutacion` | 244 | Actualiza conteos y la apuesta |
| `_paso` | 256 | Un ciclo de recocido |
| `optimizar` | 275 | Bucle hasta Ctrl+C |
| `guardar_mejor_record` | 293 | El `.txt` del mejor récord de la muestra |
| `cargar_lista` | 302 | Mete la reducida de Lotoideas y actualiza la muestra |
| `REDUCIDAS_LOTOIDEAS` | 364 | Enlace al zip de cada `(v, k, t, m)` público |
| `descargar_reducida_lotoideas` | 661 | Baja el zip y lee las apuestas |
| `main` | 708 | Menú, récord, mapeo, errores |

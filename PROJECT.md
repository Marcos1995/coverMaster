<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Contexto del proyecto

## Produccion
- URL: https://github.com/Marcos1995/coverMaster
- Vista: https://marcos1995.github.io/coverMaster/ (repo público; Chrome)
- Vista local: `index.html`

## Estado
- `LottoOptimizerV3_10.py` no se toca: consola y ventana simple, un solo fichero.
- `LottoOptimizerV3_11.py` sigue en un solo fichero: rejilla, filtros, escrutinio, garantías, análisis, validar, estadísticas, sistemas propios y el mismo recocido. La ventana es `index.html` (Stitch) dentro de pywebview. La barra verde dice qué hace en cada momento. Filtros y revisar van cerrados.
- `LottoOptimizerV3_12.c` es el mismo programa en C (código máquina). La ventana es el mismo `index.html`. El recocido, los filtros, el escrutinio y las reducidas de Lotoideas hacen lo mismo; la muestra sigue siendo de 50 000 sorteos.
- `LottoOptimizerV3_13.c` es el mismo programa que el 12. La ventana es `v13.html`, buscada junto al exe aunque la carpeta no sea ASCII. Si falta, la ventana lo dice en vez de un error de Chrome. La temperatura es la del 10. El 12 no cambia.
- `LottoOptimizerV3_14.c` es el 13 con la misma pantalla guardada dentro del exe. La ventana se llama Loto 3.14. La cobertura cuenta todos los sorteos de la base. En el recuadro verde, las apuestas van a la izquierda y el registro a la derecha. El registro solo salta al final si ya estabas abajo. Si eliges el récord, Calcular solo descarga esa lista, la pasa a los números marcados y la guarda, sin ciclos. Cada descarga va a su carpeta: la segunda no relee el fichero de la primera, y el recuadro verde muestra esas apuestas. Al 90 % o al 80 % calcula lo pedido. Mejorar récord sí busca. 24 números al 4 si 6 son 143. Si no hay récord, en bases pequeñas sube la cobertura cambiando dos números. Basta `LottoOptimizerV3_14.exe`. El 13 no cambia.
- `LottoOptimizerV3_15.c` es el 14. Al guardar, si la lista cuenta todos los sorteos, quita la apuesta que no baja esa cuenta. En 12 números al 4 si 6, 20 apuestas al 100 % quedan en menos. El 14 no cambia. La ventana se llama Loto 3.15. Basta `LottoOptimizerV3_15.exe`.
- `LottoOptimizerV3_16.c` es el 15, con una sola vía: o apuestas (fijas el número y sale la cobertura) o cobertura (fijas el porcentaje y salen las apuestas mínimas). El récord automático solo se ofrece en cobertura al 100 %. Análisis y Estadísticas dicen el porcentaje al 6, al 5, al 4, al 3, al 2 y al 1. El 15 no cambia. La ventana se llama Loto 3.16. Basta `LottoOptimizerV3_16.exe`.
- `LottoOptimizerV3_17.c` es el 16. En apuestas partes de ese número: si llegas al 100 %, los ciclos prueban con menos y se quedan en el mínimo que sigue al 100 %. Si no llegas, te quedas con las que pusiste. El 16 no cambia. La ventana se llama Loto 3.17. Basta `LottoOptimizerV3_17.exe`.
- `LottoOptimizerV3_18.c` es el 17, con tres vías: fuerza bruta, estrategia o ambas. La estrategia junta grupos de números cuando esa cuenta ya cubre; si no, cada sorteo descubierto entra como apuesta. El 17 no cambia. La ventana se llama Loto 3.18. Basta `LottoOptimizerV3_18.exe`.
- `LottoOptimizerV3_19.c` es el 18. Apuestas y cobertura no van a la vez: la que no usas queda en blanco. Al 100 % de cobertura se mira el récord; con un número de apuestas, no. Al cambiar la base se marcan los números del 1 a ese. Fuerza bruta, estrategia y ambas van al principio de la fila. El 18 no cambia. La ventana se llama Loto 3.19. Basta `LottoOptimizerV3_19.exe`.
- `LottoOptimizerV3_20.c` es el 19. Por apuestas o por cobertura se ve en dos botones con una o en medio. Al cargar un TXT marca los números del fichero, pone la base (cuántos distintos) y k (números por fila). La garantía la eliges tú. Estadísticas (ya no hay Análisis aparte) pinta en el panel derecho una tabla fija: aciertos del 6 al 0, sorteos, porcentaje, cobertura al menos esos aciertos, el total de sorteos, y cada número de la base. Validar, garantías y escrutar usan esa lista, también al cargar otro archivo. El 19 no cambia. La ventana se llama Loto 3.20. Basta `LottoOptimizerV3_20.exe`.
- Lotto Master es el programa oficial, sin número. El fuente sigue siendo `PuntoX.c` y la pantalla `puntox.html`. La ventana se llama Lotto Master. El fichero que se entrega se llama `LottoMaster.exe`. Los numerados del 10 al 20 no se siguen. Cada cambio de este repo adjunta ese exe en el chat de Telegram. Estadísticas abre un aviso con las combinaciones totales, la cobertura de la garantía y una tabla al k, al k−1, … y al 1. No hay registro: la línea verde dice qué pasa, y guardar, validar y escrutar salen en un aviso corto. El fichero solo se escribe al pulsar Guardar. Los números del 1 al 49 son celdas fijas, y la ventana abre a 1040×680: la rejilla a la izquierda, los filtros en la mitad y las apuestas en la otra mitad, una bajo otra, fondo oscuro y texto verde. Marcar o quitar un número pone Base al total marcado. La garantía incluye 6 si 6, junto a 5 si 6 y 4 si 6. Guardar apuestas va en la misma fila que Mejorar récord, en verde: pregunta dos cifras (01) o una (1), espacio o coma, y texto, CSV o los dos; el fichero solo lleva las apuestas. El último número no salta de línea. La línea verde no repite la palabra ahora. Distancias va en una línea: 25 es el máximo del primero al último, y 3-7;4-6;… es el mínimo y el máximo de cada hueco (con seis números, cinco huecos).
- `cuatro_grupos.py` prueba el reparto en cuatro grupos. En 24 al 4 si 6 cubre el 100 % con 277 y no baja de 143: cada pareja pide 25 y las seis no se mezclan.
- `records.py` guarda las estrategias (grupos, corte, Steiner, patrón 27, patrón 24, avaro) y las pasa de menos sorteos a más. 12 al 4 si 6 son 6 apuestas de grupos, 0 fallos en 924. 49 al 3 si 6 es 77+86=163. 24 al 4 si 6 son 143. Detalle en `docs/ESTRATEGIAS.md`.
- Lectura del algoritmo: `docs/LottoOptimizerV3_10.md`. El 11 usa esa lógica.
- Si `(v, k, t, m)` tiene zip público en Lotoideas, se ofrece esa lista o intentar mejorarla. Si no sube la cobertura, se guarda la de Lotoideas.
- Kit de agentes en `.cursor/` (skills, rules, agents) más `AGENTS.md`.

## Stack
- Python 3. El 10 es consola. El 11 abre pywebview (WebView2) con `index.html`. El exe del 11 es PyInstaller, misma velocidad.
- El 12 es C. `LottoOptimizerV3_12.exe` abre el mismo `index.html` en una ventana de Edge. El cálculo va en código máquina.
- El 13 es el mismo C. `LottoOptimizerV3_13.exe` abre `v13.html`. Vista: https://marcos1995.github.io/coverMaster/v13.html
- El 14 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_14.exe`. Vista: https://marcos1995.github.io/coverMaster/v14.html
- El 15 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_15.exe`. Vista: https://marcos1995.github.io/coverMaster/v15.html
- El 16 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_16.exe`. Vista: https://marcos1995.github.io/coverMaster/v16.html
- El 17 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_17.exe`. Vista: https://marcos1995.github.io/coverMaster/v17.html
- El 18 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_18.exe`. Vista: https://marcos1995.github.io/coverMaster/v18.html
- El 19 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_19.exe`. Vista: https://marcos1995.github.io/coverMaster/v19.html
- El 20 es el mismo C. La pantalla va dentro de `LottoOptimizerV3_20.exe`. Vista: https://marcos1995.github.io/coverMaster/v20.html
- Lotto Master es el oficial, sin número. `LottoMaster.exe` lleva `puntox.html` dentro. En Telegram va adjunto, solo en este repo.

## Comandos utiles
- Instalar:
- Test:
- Consola: `python LottoOptimizerV3_10.py`
- Ventana: `python -m pip install pywebview` y `python LottoOptimizerV3_11.py`
- Consola del 11: `python LottoOptimizerV3_11.py --consola`
- Exe del 11: `dist\LottoOptimizerV3_11.exe`
- Exe del 12 (código máquina): `LottoOptimizerV3_12.exe`
- Exe del 13 (misma lógica, pantalla nueva): `LottoOptimizerV3_13.exe`
- Exe del 14 (un solo fichero, la pantalla va dentro): `LottoOptimizerV3_14.exe`
- Exe del 15 (igual, y al guardar quita apuestas que sobran): `LottoOptimizerV3_15.exe`
- Exe del 16 (o apuestas o cobertura): `LottoOptimizerV3_16.exe`
- Exe del 17 (en apuestas, al 100 % baja el número): `LottoOptimizerV3_17.exe`
- Exe del 18 (fuerza bruta, estrategia o ambas): `LottoOptimizerV3_18.exe`
- Exe del 19 (cobertura o apuestas, la otra en blanco): `LottoOptimizerV3_19.exe`
- Exe del 20 (se ve por apuestas o por cobertura): `LottoOptimizerV3_20.exe`
- Exe oficial, sin número: `LottoMaster.exe`
- Cuatro grupos: `python cuatro_grupos.py`
- Los récords, de menos sorteos a más: `python records.py`
- Recompilar el 12: `zig cc -O2 -std=c11 -o LottoOptimizerV3_12.exe LottoOptimizerV3_12.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 13: `zig cc -O2 -std=c11 -o LottoOptimizerV3_13.exe LottoOptimizerV3_13.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 14: `zig cc -O2 -std=c11 -o LottoOptimizerV3_14.exe LottoOptimizerV3_14.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 15: `zig cc -O2 -std=c11 -o LottoOptimizerV3_15.exe LottoOptimizerV3_15.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 16: `zig cc -O2 -std=c11 -o LottoOptimizerV3_16.exe LottoOptimizerV3_16.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 17: `zig cc -O2 -std=c11 -o LottoOptimizerV3_17.exe LottoOptimizerV3_17.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 18: `zig cc -O2 -std=c11 -o LottoOptimizerV3_18.exe LottoOptimizerV3_18.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 19: `zig cc -O2 -std=c11 -o LottoOptimizerV3_19.exe LottoOptimizerV3_19.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 20: `zig cc -O2 -std=c11 -o LottoOptimizerV3_20.exe LottoOptimizerV3_20.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar Lotto Master: `zig cc -O2 -std=c11 -o LottoMaster.exe PuntoX.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Grafo: `graphify update .` (paquete `graphifyy`; ejecutable en `%USERPROFILE%\.local\bin`)

## Notas para el agente
- Ni el 10 ni el 11 se parten en módulos. El 10 no se edita. El 12, el 13, el 14, el 15, el 16, el 17, el 18, el 19 y el 20 son otros ficheros, en C, y ya no se siguen. El que se edita es `PuntoX.c`.
- Lean kit (ver AGENTS.md)

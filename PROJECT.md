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
- `LottoOptimizerV3_13.c` es el mismo programa que el 12. La ventana es `v13.html` (otra pantalla de Stitch, más clara). El 12 no cambia de aspecto.
- Lectura del algoritmo: `docs/LottoOptimizerV3_10.md`. El 11 usa esa lógica.
- Si `(v, k, t, m)` tiene zip público en Lotoideas, se ofrece esa lista o intentar mejorarla. Si no sube la cobertura, se guarda la de Lotoideas.
- Kit de agentes en `.cursor/` (skills, rules, agents) más `AGENTS.md`.

## Stack
- Python 3. El 10 es consola. El 11 abre pywebview (WebView2) con `index.html`. El exe del 11 es PyInstaller, misma velocidad.
- El 12 es C. `LottoOptimizerV3_12.exe` abre el mismo `index.html` en una ventana de Edge. El cálculo va en código máquina.
- El 13 es el mismo C. `LottoOptimizerV3_13.exe` abre `v13.html`. Vista: https://marcos1995.github.io/coverMaster/v13.html

## Comandos utiles
- Instalar:
- Test:
- Consola: `python LottoOptimizerV3_10.py`
- Ventana: `python -m pip install pywebview` y `python LottoOptimizerV3_11.py`
- Consola del 11: `python LottoOptimizerV3_11.py --consola`
- Exe del 11: `dist\LottoOptimizerV3_11.exe`
- Exe del 12 (código máquina): `LottoOptimizerV3_12.exe`
- Exe del 13 (misma lógica, pantalla nueva): `LottoOptimizerV3_13.exe`
- Recompilar el 12: `zig cc -O2 -std=c11 -o LottoOptimizerV3_12.exe LottoOptimizerV3_12.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Recompilar el 13: `zig cc -O2 -std=c11 -o LottoOptimizerV3_13.exe LottoOptimizerV3_13.c -lwinhttp -lws2_32 -lcomdlg32 -lgdi32 -luser32 -lshell32`
- Grafo: `graphify update .` (paquete `graphifyy`; ejecutable en `%USERPROFILE%\.local\bin`)

## Notas para el agente
- Ni el 10 ni el 11 se parten en módulos. El 10 no se edita. El 12 y el 13 son otros ficheros, en C.
- Lean kit (ver AGENTS.md)

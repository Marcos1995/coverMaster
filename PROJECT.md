<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Contexto del proyecto

## Produccion
- URL: https://github.com/Marcos1995/coverMaster
- Vista: https://marcos1995.github.io/coverMaster/ (repo público; Chrome)
- Vista local: `index.html`

## Estado
- `LottoOptimizerV3_10.py` no se toca: consola y ventana simple, un solo fichero.
- `LottoOptimizerV3_11.py` sigue en un solo fichero: rejilla, filtros, escrutinio, garantías, análisis, validar, estadísticas, sistemas propios y el mismo recocido. La ventana es `index.html` (Stitch) dentro de pywebview. La barra verde dice qué hace en cada momento. Filtros y revisar van cerrados.
- Lectura del algoritmo: `docs/LottoOptimizerV3_10.md`. El 11 usa esa lógica.
- Si `(v, k, t, m)` tiene zip público en Lotoideas, se ofrece esa lista o intentar mejorarla. Si no sube la cobertura, se guarda la de Lotoideas.
- Kit de agentes en `.cursor/` (skills, rules, agents) más `AGENTS.md`.

## Stack
- Python 3. El 10 es consola. El 11 abre pywebview (WebView2) con `index.html`. El exe es PyInstaller, misma velocidad.

## Comandos utiles
- Instalar:
- Test:
- Consola: `python LottoOptimizerV3_10.py`
- Ventana: `python -m pip install pywebview` y `python LottoOptimizerV3_11.py`
- Consola del 11: `python LottoOptimizerV3_11.py --consola`
- Exe: `dist\LottoOptimizerV3_11.exe`
- Grafo: `graphify update .` (paquete `graphifyy`; ejecutable en `%USERPROFILE%\.local\bin`)

## Notas para el agente
- Ni el 10 ni el 11 se parten en módulos. El 10 no se edita.
- Lean kit (ver AGENTS.md)

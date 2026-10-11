# Graph Report - coverMaster  (2026-10-11)

## Corpus Check
- 25 files · ~98,698 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: .exe 4, .pdb 3, .mdc 2)

## Summary
- 600 nodes · 1537 edges · 31 communities (21 shown, 10 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `caedaf67`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LottoOptimizerV3_11.py
- LottoOptimizerV3
- Lotto Optimizer V3.10
- Debug
- main_gui
- Contexto del proyecto
- Dashboard brief (for the Stitch prompt)
- Verify (UI)
- Web design
- Agent rules
- Build judgments with Laya
- Laya
- Review
- Project
- tablas/SKILL.md
- LottoOptimizerV3_13.c
- DECISIONES.md
- LottoOptimizerV3
- LottoOptimizerV3_14.c
- LottoOptimizerV3_12.c
- datos_desde_ui
- estado
- DESIGN.md
- LottoOptimizerV3_15.c
- BitUtils
- BitUtils
- Configuracion
- apuesta_pasa_filtros

## God Nodes (most connected - your core abstractions)
1. `api_dispatch()` - 26 edges
2. `api_dispatch()` - 26 edges
3. `api_dispatch()` - 24 edges
4. `main_gui()` - 23 edges
5. `api_dispatch()` - 21 edges
6. `LottoOptimizerV3` - 18 edges
7. `LottoOptimizerV3` - 18 edges
8. `hilo()` - 18 edges
9. `hilo()` - 18 edges
10. `Lotto Optimizer V3.10` - 16 edges

## Surprising Connections (you probably didn't know these)
- `leer_grupos()` --calls--> `analizar_entrada_numeros()`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 22 → community 0_
- `main()` --calls--> `escribir_apuestas()`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 4 → community 0_
- `_filtros_desde_ui()` --calls--> `Filtros`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 30 → community 22_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 29 → community 0_
- `_trabajo()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 29 → community 4_

## Import Cycles
- None detected.

## Communities (31 total, 10 thin omitted)

### Community 0 - "LottoOptimizerV3_11.py"
Cohesion: 0.17
Nodes (20): dataclasses, datetime, io, LOTTO OPTIMIZER V3.10 - Pantalla limpia y guardado exclusivo del MEJOR récord…, configurar_consola(), leer_entero(), leer_grupos(), leer_parametros() (+12 more)

### Community 1 - "LottoOptimizerV3"
Cohesion: 0.07
Nodes (24): analizar_entrada_numeros(), CondicionGrupo, Configuracion, configurar_consola(), descargar_reducida_lotoideas(), escribir_apuestas(), _grupos_desde_texto(), leer_entero() (+16 more)

### Community 2 - "Lotto Optimizer V3.10"
Cohesion: 0.12
Nodes (16): Cobertura, Ganancia, Generación, Grupos, Lotto Optimizer V3.10, Muestra de sorteos, Números reales, Optimización (+8 more)

### Community 3 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 4 - "main_gui"
Cohesion: 0.14
Nodes (21): descargar_reducida_lotoideas(), escribir_apuestas(), main_gui(), analizar(), _anotar(), calcular(), _con_apuestas(), estadisticas() (+13 more)

### Community 5 - "Contexto del proyecto"
Cohesion: 0.29
Nodes (6): Comandos utiles, Contexto del proyecto, Estado, Notas para el agente, Produccion, Stack

### Community 6 - "Dashboard brief (for the Stitch prompt)"
Cohesion: 0.33
Nodes (5): Anatomy (always), Charts without libraries (inline SVG, no CDN), CSS, Dashboard brief (for the Stitch prompt), Data honesty (non-negotiable)

### Community 7 - "Verify (UI)"
Cohesion: 0.40
Nodes (4): 1. Screenshots, 2. Look, 3. Fix and repeat, Verify (UI)

### Community 8 - "Web design"
Cohesion: 0.40
Nodes (4): Before HECHO, Steps, Style = `DESIGN.md`, Web design

### Community 9 - "Agent rules"
Cohesion: 0.50
Nodes (3): Agent rules, Flujo, Think → Simple → Surgical → Verify (Karpathy)

### Community 10 - "Build judgments with Laya"
Cohesion: 0.50
Nodes (3): Build judgments with Laya, Call, Design

### Community 11 - "Laya"
Cohesion: 0.50
Nodes (3): Laya, Reply (decision-only requests), Steps

### Community 12 - "Review"
Cohesion: 0.50
Nodes (3): Check, Do, Review

### Community 13 - "Project"
Cohesion: 0.50
Nodes (3): Docs, Project, Setup

### Community 17 - "LottoOptimizerV3_13.c"
Cohesion: 0.07
Nodes (82): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), atender() (+74 more)

### Community 20 - "LottoOptimizerV3_14.c"
Cohesion: 0.06
Nodes (99): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+91 more)

### Community 21 - "LottoOptimizerV3_12.c"
Cohesion: 0.06
Nodes (88): commdlg, ctype, limits, abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar() (+80 more)

### Community 22 - "datos_desde_ui"
Cohesion: 0.20
Nodes (12): analizar_entrada_numeros(), CondicionGrupo, datos_desde_ui(), _entero_ui(), escrutar_apuestas(), _filtros_desde_ui(), _grupos_desde_texto(), grupos_traducidos() (+4 more)

### Community 24 - "estado"
Cohesion: 0.50
Nodes (4): estado(), _volcar(), _palabra(), _porcentaje()

### Community 26 - "LottoOptimizerV3_15.c"
Cohesion: 0.06
Nodes (100): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+92 more)

### Community 30 - "apuesta_pasa_filtros"
Cohesion: 1.00
Nodes (3): apuesta_pasa_filtros(), Filtros, texto_validacion()

## Knowledge Gaps
- **48 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 115 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main_gui()` connect `main_gui` to `LottoOptimizerV3_11.py`, `estado`, `datos_desde_ui`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`, `main_gui`, `Configuracion`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LottoOptimizerV3` be split into smaller, more focused modules?**
  _Cohesion score 0.07149758454106281 - nodes in this community are weakly interconnected._
- **Should `Lotto Optimizer V3.10` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `main_gui` be split into smaller, more focused modules?**
  _Cohesion score 0.14333333333333334 - nodes in this community are weakly interconnected._
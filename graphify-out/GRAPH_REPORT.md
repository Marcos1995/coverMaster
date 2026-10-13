# Graph Report - coverMaster  (2026-10-14)

## Corpus Check
- 40 files · ~255,475 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 25 file(s) not represented in the graph (top: .exe 10, .pdb 10, .mdc 3)

## Summary
- 1352 nodes · 4242 edges · 40 communities (28 shown, 12 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7acb362b`
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
- main
- LottoOptimizerV3_16.c
- DESIGN.md
- LottoOptimizerV3_15.c
- BitUtils
- BitUtils
- Configuracion
- apuesta_pasa_filtros
- main_gui
- LottoOptimizerV3_17.c
- Configuracion
- LottoOptimizerV3_18.c
- LottoOptimizerV3_19.c
- LottoOptimizerV3_20.c
- records.py
- Estrategias
- PuntoX.c

## God Nodes (most connected - your core abstractions)
1. `api_dispatch()` - 29 edges
2. `api_dispatch()` - 28 edges
3. `api_dispatch()` - 27 edges
4. `api_dispatch()` - 27 edges
5. `api_dispatch()` - 27 edges
6. `api_dispatch()` - 27 edges
7. `api_dispatch()` - 26 edges
8. `api_dispatch()` - 26 edges
9. `api_dispatch()` - 24 edges
10. `main_gui()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `main_gui()` --indirect_call--> `mapear()`  [INFERRED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 31 → community 0_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 33 → community 0_
- `trabajo()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 33 → community 31_
- `main()` --calls--> `LottoOptimizerV3`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 0_
- `trabajo()` --calls--> `LottoOptimizerV3`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 31_

## Import Cycles
- None detected.

## Communities (40 total, 12 thin omitted)

### Community 0 - "LottoOptimizerV3_11.py"
Cohesion: 0.13
Nodes (25): dataclasses, datetime, io, analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), _grupos_desde_texto(), leer_entero() (+17 more)

### Community 2 - "Lotto Optimizer V3.10"
Cohesion: 0.12
Nodes (16): Cobertura, Ganancia, Generación, Grupos, Lotto Optimizer V3.10, Muestra de sorteos, Números reales, Optimización (+8 more)

### Community 3 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 4 - "main_gui"
Cohesion: 0.11
Nodes (26): descargar_reducida_lotoideas(), escribir_apuestas(), main_gui(), analizar(), _anotar(), calcular(), cargar(), _con_apuestas() (+18 more)

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
Cohesion: 0.05
Nodes (94): commdlg, ctype, limits, abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar() (+86 more)

### Community 20 - "LottoOptimizerV3_14.c"
Cohesion: 0.06
Nodes (99): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+91 more)

### Community 21 - "LottoOptimizerV3_12.c"
Cohesion: 0.07
Nodes (76): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), atender() (+68 more)

### Community 22 - "main"
Cohesion: 0.16
Nodes (17): analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), datos_desde_ui(), _entero_ui(), escrutar_apuestas(), _filtros_desde_ui(), _grupos_desde_texto() (+9 more)

### Community 24 - "LottoOptimizerV3_16.c"
Cohesion: 0.06
Nodes (107): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), anotar_niveles(), api_dispatch(), aplicar() (+99 more)

### Community 26 - "LottoOptimizerV3_15.c"
Cohesion: 0.06
Nodes (100): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+92 more)

### Community 30 - "apuesta_pasa_filtros"
Cohesion: 1.00
Nodes (3): apuesta_pasa_filtros(), Filtros, texto_validacion()

### Community 31 - "main_gui"
Cohesion: 0.18
Nodes (9): descargar_reducida_lotoideas(), escribir_apuestas(), _leer_enteros_gui(), main_gui(), aviso_record(), lanzar(), trabajo(), ocupado() (+1 more)

### Community 32 - "LottoOptimizerV3_17.c"
Cohesion: 0.06
Nodes (108): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), anotar_niveles(), api_dispatch(), aplicar() (+100 more)

### Community 34 - "LottoOptimizerV3_18.c"
Cohesion: 0.06
Nodes (115): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), anotar_niveles(), api_dispatch(), aplicar() (+107 more)

### Community 35 - "LottoOptimizerV3_19.c"
Cohesion: 0.06
Nodes (115): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), anotar_niveles(), api_dispatch(), aplicar() (+107 more)

### Community 36 - "LottoOptimizerV3_20.c"
Cohesion: 0.06
Nodes (116): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+108 more)

### Community 37 - "records.py"
Cohesion: 0.08
Nodes (42): construir(), cubre(), cubrir_pares(), demostrar_repartos(), diseno_2_y_2(), diseno_3_y_3(), fallos(), main() (+34 more)

### Community 38 - "Estrategias"
Cohesion: 0.22
Nodes (8): Avaro, Corte, Estrategias, Grupos, Patrón 24, Patrón 27, Steiner, Ventana

### Community 39 - "PuntoX.c"
Cohesion: 0.06
Nodes (114): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+106 more)

## Knowledge Gaps
- **55 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 169 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`, `Configuracion`, `main_gui`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `main_gui()` connect `main_gui` to `LottoOptimizerV3_11.py`, `main`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `BitUtils` connect `BitUtils` to `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _55 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LottoOptimizerV3_11.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1349206349206349 - nodes in this community are weakly interconnected._
- **Should `Lotto Optimizer V3.10` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `main_gui` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._
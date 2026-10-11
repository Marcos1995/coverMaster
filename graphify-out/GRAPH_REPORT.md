# Graph Report - coverMaster  (2026-10-11)

## Corpus Check
- 23 files · ~75,644 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .exe 3, .mdc 2, .spec 2)

## Summary
- 494 nodes · 1179 edges · 29 communities (21 shown, 8 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ac57421e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LottoOptimizerV3_10.py
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
- LottoOptimizerV3_11.py
- estado
- DESIGN.md
- main_gui
- BitUtils
- BitUtils

## God Nodes (most connected - your core abstractions)
1. `api_dispatch()` - 26 edges
2. `api_dispatch()` - 24 edges
3. `main_gui()` - 23 edges
4. `api_dispatch()` - 21 edges
5. `LottoOptimizerV3` - 18 edges
6. `LottoOptimizerV3` - 18 edges
7. `hilo()` - 18 edges
8. `Lotto Optimizer V3.10` - 16 edges
9. `parse_datos()` - 15 edges
10. `parse_datos()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `main_gui()` --indirect_call--> `mapear()`  [INFERRED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 26 → community 0_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 0_
- `trabajo()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 26_
- `cargar()` --calls--> `analizar_entrada_numeros()`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 22 → community 4_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 19 → community 22_

## Import Cycles
- None detected.

## Communities (29 total, 8 thin omitted)

### Community 0 - "LottoOptimizerV3_10.py"
Cohesion: 0.12
Nodes (24): dataclasses, datetime, io, analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), _grupos_desde_texto(), leer_entero() (+16 more)

### Community 1 - "LottoOptimizerV3"
Cohesion: 0.18
Nodes (3): Configuracion, LottoOptimizerV3, MotorMutaciones

### Community 2 - "Lotto Optimizer V3.10"
Cohesion: 0.12
Nodes (16): Cobertura, Ganancia, Generación, Grupos, Lotto Optimizer V3.10, Muestra de sorteos, Números reales, Optimización (+8 more)

### Community 3 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 4 - "main_gui"
Cohesion: 0.15
Nodes (21): escribir_apuestas(), main_gui(), analizar(), _anotar(), calcular(), cargar(), _con_apuestas(), estadisticas() (+13 more)

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

### Community 19 - "LottoOptimizerV3"
Cohesion: 0.18
Nodes (3): Configuracion, LottoOptimizerV3, MotorMutaciones

### Community 20 - "LottoOptimizerV3_14.c"
Cohesion: 0.06
Nodes (97): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), apuestas_de_url() (+89 more)

### Community 21 - "LottoOptimizerV3_12.c"
Cohesion: 0.06
Nodes (88): commdlg, ctype, limits, abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar() (+80 more)

### Community 22 - "LottoOptimizerV3_11.py"
Cohesion: 0.17
Nodes (23): analizar_entrada_numeros(), apuesta_pasa_filtros(), CondicionGrupo, configurar_consola(), datos_desde_ui(), descargar_reducida_lotoideas(), _entero_ui(), escrutar_apuestas() (+15 more)

### Community 24 - "estado"
Cohesion: 0.50
Nodes (4): estado(), _volcar(), _palabra(), _porcentaje()

### Community 26 - "main_gui"
Cohesion: 0.18
Nodes (9): descargar_reducida_lotoideas(), escribir_apuestas(), _leer_enteros_gui(), main_gui(), aviso_record(), lanzar(), trabajo(), ocupado() (+1 more)

## Knowledge Gaps
- **48 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 109 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main_gui()` connect `main_gui` to `estado`, `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_10.py`, `main_gui`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `main_gui`, `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LottoOptimizerV3_10.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `Lotto Optimizer V3.10` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `main_gui` be split into smaller, more focused modules?**
  _Cohesion score 0.14666666666666667 - nodes in this community are weakly interconnected._
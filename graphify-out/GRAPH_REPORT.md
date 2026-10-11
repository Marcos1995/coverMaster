# Graph Report - coverMaster  (2026-10-11)

## Corpus Check
- 27 files · ~117,643 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .exe 5, .pdb 4, .mdc 2)

## Summary
- 711 nodes · 1933 edges · 32 communities (22 shown, 10 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0148a9fa`
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

## God Nodes (most connected - your core abstractions)
1. `api_dispatch()` - 27 edges
2. `api_dispatch()` - 26 edges
3. `api_dispatch()` - 26 edges
4. `api_dispatch()` - 24 edges
5. `main_gui()` - 23 edges
6. `api_dispatch()` - 21 edges
7. `hilo()` - 19 edges
8. `LottoOptimizerV3` - 18 edges
9. `LottoOptimizerV3` - 18 edges
10. `hilo()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `main_gui()` --indirect_call--> `mapear()`  [INFERRED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 31 → community 0_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 0_
- `trabajo()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 31_
- `cargar()` --calls--> `analizar_entrada_numeros()`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 22 → community 4_
- `main()` --calls--> `limpiar_pantalla()`  [EXTRACTED]
  LottoOptimizerV3_11.py → LottoOptimizerV3_11.py  _Bridges community 19 → community 22_

## Import Cycles
- None detected.

## Communities (32 total, 10 thin omitted)

### Community 0 - "LottoOptimizerV3_11.py"
Cohesion: 0.13
Nodes (25): dataclasses, datetime, io, analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), descargar_reducida_lotoideas(), leer_entero() (+17 more)

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
Cohesion: 0.10
Nodes (29): descargar_reducida_lotoideas(), escribir_apuestas(), escrutar_apuestas(), main_gui(), analizar(), _anotar(), calcular(), cargar() (+21 more)

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
Cohesion: 0.19
Nodes (14): analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), datos_desde_ui(), _entero_ui(), _filtros_desde_ui(), _grupos_desde_texto(), grupos_traducidos() (+6 more)

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
Cohesion: 0.19
Nodes (9): escribir_apuestas(), _grupos_desde_texto(), _leer_enteros_gui(), main_gui(), aviso_record(), lanzar(), trabajo(), ocupado() (+1 more)

## Knowledge Gaps
- **48 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 121 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main_gui()` connect `main_gui` to `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`, `main_gui`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`, `main_gui`, `Configuracion`, `main`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LottoOptimizerV3_11.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13227513227513227 - nodes in this community are weakly interconnected._
- **Should `Lotto Optimizer V3.10` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `main_gui` be split into smaller, more focused modules?**
  _Cohesion score 0.10416666666666667 - nodes in this community are weakly interconnected._
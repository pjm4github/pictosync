# Diagram Round-Tripping Tools
## *PUML ↔ JSON ↔ Canvas ↔ PPTX — Commercial and Open Source Alternatives*

**Last updated: February 2026**

## Overview

This survey evaluates tools that support **human-in-the-loop round-tripping** between diagram formats — specifically PlantUML import, JSON intermediate representation, visual canvas editing with PNG overlay, and PowerPoint export. These capabilities matter for architecture documentation workflows where diagrams must flow between code-as-documentation, visual refinement, and presentation delivery.

Tools are organized into six categories:
1. **PlantUML Ecosystem** — Rendering and editing tools built around PlantUML
2. **Diagram-as-Code** — Text DSL tools with visual editing and export
3. **Visual Diagramming** — Canvas-first tools with code import/export
4. **AI-Powered Diagram Tools** — Image-to-diagram extraction with AI
5. **C4 Model Tools** — Architecture-specific modeling tools
6. **JSON-Based Diagram Formats** — Tools using JSON as native or intermediate format

---

## Master Comparison Matrix

The core capabilities that define the round-trip workflow:

| Tool | PUML Import | JSON IR | Canvas Edit | Bidi Sync | PPTX Export | PNG Overlay | AI Extract | Open Source |
|------|:-----------:|:-------:|:-----------:|:---------:|:-----------:|:-----------:|:----------:|:----------:|
| **PictoSync** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** |
| D2 Studio | No | No | Yes | Yes | Yes | No | No | Partial |
| dAIgram | No | Yes | Yes | No | Yes | Yes (input) | Yes | No |
| Eraser.io | Converts | No | Yes | Partial | No | No | Yes | No |
| draw.io | Removed 2025 | No (XML) | Yes | No | Add-in | Image layer | No | Yes |
| OxDraw | No | No | Yes | Yes | No | No | Code maps | Yes |
| Excalidraw | No | Yes (native) | Yes | No | No | No | No | Yes |
| LikeC4 | No | No | Yes | With draw.io | No | No | No | Yes |
| Structurizr | No | Yes | No | No | No | No | No | Partial |
| IcePanel | No | Yes | Yes | No | No | No | No | No |
| Miro + PlantUML App | Via app | No | Whiteboard | No | No | Images on board | Miro Assist | No |
| Lucidchart | Minimal | No | Yes | No | Image only | No | AI text-to-diagram | No |
| Visual Paradigm | Via plugin | Yes (export) | Yes | Code eng. only | Limited | No | AI builder | No |

**Key**: Yes = native support, No = not supported, Partial = limited or via add-on

---

## 1. PlantUML Ecosystem Tools

Tools built around the PlantUML text-to-diagram rendering engine.

### PlantUML (core)
- **Website**: [plantuml.com](https://plantuml.com/)
- **License**: GPL (open source)
- Text-to-diagram rendering for UML, C4, and 15+ diagram types
- Exports to PNG, SVG, EPS, LaTeX — **no native PPTX export**
- No visual editing — strictly one-way text → image rendering
- No JSON intermediate format (uses its own text DSL)
- A [PlantUML PowerPoint Add-in](https://github.com/kmierzeje/plantuml-powerpoint-addin) exists (Windows only) to embed PlantUML diagrams as images in PPTX presentations

### Kroki
- **Website**: [kroki.io](https://kroki.io/)
- **License**: MIT (open source)
- Unified API server rendering diagrams from 20+ text formats (PlantUML, Mermaid, D2, Excalidraw, GraphViz, C4, etc.)
- Pure rendering service — no visual editing, no PPTX export, no JSON format
- Useful as a backend renderer for other tools

### PlantText / Pladitor
- **PlantText**: [planttext.com](https://www.planttext.com/) — online PlantUML editor with live preview
- **Pladitor**: [plantumleditor.com](https://plantumleditor.com/) — cross-platform PlantUML editor with templates
- Both are text-based editors only — no canvas manipulation, no PPTX export

### Ericsson PlantUML Interactive Editor
- **Repo**: [github.com/Ericsson/PlantUML-Interactive-Editor](https://github.com/Ericsson/PlantUML-Interactive-Editor)
- Open source graphical editor for PlantUML with real-time rendering
- Some interactivity but not full bidirectional canvas editing

| Capability | PlantUML | Kroki | PlantText | Pladitor |
|---|:---:|:---:|:---:|:---:|
| Import PlantUML | Native | Yes | Yes | Yes |
| Visual canvas editing | No | No | No | No |
| Bidirectional sync | No | No | No | No |
| PPTX export | No (add-in) | No | No | No |
| PNG annotation overlay | No | No | No | No |
| JSON intermediate format | No | No | No | No |

**Gap**: The entire PlantUML ecosystem is one-way (text → image). No tool provides visual editing of rendered output or round-trip back to PUML source.

---

## 2. Diagram-as-Code Tools

Text DSL tools that generate diagrams, some with visual editing.

### D2 / Terrastruct D2 Studio
- **Website**: [terrastruct.com](https://terrastruct.com/) / [d2lang.com](https://d2lang.com/)
- **License**: D2 is MIT (open source); D2 Studio is commercial
- **Bidirectional editing**: D2 Studio supports both drag-and-drop visual editing and text editing with changes synced bidirectionally — the strongest code ↔ visual sync in this category
- **PPTX export**: Supported since v0.4.1 for multi-board compositions (uses Playwright for rendering)
- Uses its own DSL (not PlantUML). No PNG annotation/overlay. No JSON intermediate format
- **Closest competitor** for bidi sync + PPTX, but missing PlantUML and AI extraction

### Mermaid / Mermaid Chart
- **Website**: [mermaid.js.org](https://mermaid.js.org/) / [mermaidchart.com](https://www.mermaidchart.com/)
- **License**: Mermaid.js is MIT (open source); Mermaid Chart is commercial SaaS
- A [Mermaid PowerPoint Add-in](https://docs.mermaidchart.com/plugins/microsoft-powerpoint) exists to insert and edit Mermaid diagrams directly in PPTX with persistent source code and live preview
- No native PlantUML import. No bidirectional visual editing in the core library
- [Diagramming AI](https://diagrammingai.com/) offers a Visual Editor converting Mermaid to Excalidraw canvases (one-way)

### OxDraw
- **Repo**: [github.com/RohanAdwankar/oxdraw](https://github.com/RohanAdwankar/oxdraw)
- **License**: Open source (Rust + React)
- **True bidirectional sync**: Drag nodes in the web UI and positions persist back to `.mmd` source file. Grid snapping, alignment guides, edge handle dragging
- Exports to SVG, PNG, PDF — **no PPTX export**
- No PlantUML import (Mermaid only). Includes AI and static analysis for code map generation

### Eraser.io
- **Website**: [eraser.io](https://www.eraser.io/)
- **License**: Commercial SaaS
- **PlantUML import**: Paste PlantUML code and it converts to Eraser's diagram format
- Supports drag-and-drop editing alongside code editing
- DiagramGPT for AI generation from text prompts
- Exports to PNG, SVG, PDF — **no PPTX export**

| Capability | D2 Studio | Mermaid | OxDraw | Eraser.io |
|---|:---:|:---:|:---:|:---:|
| Import PlantUML | No | No | No | Converts |
| Visual canvas editing | Yes | Limited | Yes | Yes |
| Bidirectional sync | Yes | No | Yes | Partial |
| PPTX export | Yes | Add-in | No | No |
| PNG annotation overlay | No | No | No | No |
| JSON intermediate format | No | No | No | No |
| AI capabilities | No | No | Code maps | DiagramGPT |
| Open source | Partial | Yes | Yes | No |

**Gap**: D2 Studio has the best bidi sync + PPTX story, but no PlantUML, no AI extraction, no PNG annotation. Eraser can import PlantUML but loses round-trip capability.

---

## 3. Visual Diagramming Tools

Canvas-first tools with varying levels of code import/export.

### draw.io / diagrams.net
- **Website**: [drawio.com](https://www.drawio.com/)
- **License**: jgraph (open source)
- **PlantUML import**: Previously supported but **being removed at end of 2025** from the online version (2028 from Confluence/Jira). Migration path is PlantUML → Mermaid → draw.io
- Third-party converters: [plantuml2drawio](https://github.com/doubleSlashde/plantuml2drawio), [plantuml_to_drawio](https://github.com/rglaue/plantuml_to_drawio)
- Full visual canvas editing. Uses XML (mxGraph) as native format, not JSON
- **PPTX export**: No native export. A free [Office Add-in](https://www.drawio.com/doc/faq/microsoft-office-diagrams) embeds diagram images. [drawio2pptx](https://github.com/mashu3/drawio2pptx) converts programmatically
- No bidirectional code-to-visual sync. Can overlay images on canvas but not structured annotation

### Lucidchart
- **Website**: [lucidchart.com](https://www.lucidchart.com/)
- **License**: Commercial SaaS
- **PlantUML import**: Very limited — sequence diagrams only, and some PlantUML syntax not supported. Frequently requested feature with no full implementation
- AI-powered diagram generation from text (Lucid Custom GPT, Microsoft Copilot integration)
- Exports to PNG, SVG, PDF, Visio — PPTX via image insertion only
- No bidirectional code sync. No JSON intermediate format

### Miro
- **Website**: [miro.com](https://miro.com/)
- **License**: Commercial SaaS (collaborative whiteboard)
- **PlantUML import**: Via the [PlantUML app for Miro](https://miro.com/marketplace/plantUML/) by Gend. Renders PlantUML as a static image on the board; double-click to edit source and re-render
- No true bidirectional sync — rendered image is static. Miro Assist AI can convert notes into diagrams
- No native PPTX export for diagrams

### Microsoft Visio
- PlantUML can export to Visio format via `-tvdx` flag (one-directional only)
- No PlantUML import into Visio. No bidirectional sync
- Strong PPTX integration within the Microsoft ecosystem

### Visual Paradigm
- **Website**: [visual-paradigm.com](https://www.visual-paradigm.com/)
- **License**: Commercial
- [PlantUML VP Plugin](https://github.com/nbourdi/PlantUML-VP-Plugin) for import/export with live side-by-side preview
- Exports to JSON for sharing/versioning, SVG, and PlantUML code
- Supports round-trip code engineering (Java ↔ UML), but not round-trip PlantUML text ↔ visual canvas

| Capability | draw.io | Lucidchart | Miro | Visio | Visual Paradigm |
|---|:---:|:---:|:---:|:---:|:---:|
| Import PlantUML | Removed 2025 | Minimal | Via app | One-way | Via plugin |
| Visual canvas editing | Yes | Yes | Yes | Yes | Yes |
| Bidirectional sync | No | No | No | No | Code eng. only |
| PPTX export | Add-in | Image only | No | Yes | Limited |
| PNG annotation overlay | Image layer | No | Board images | No | No |
| JSON intermediate format | No (XML) | No | No | No | Yes (export) |
| AI capabilities | No | AI text-to-diagram | Miro Assist | No | AI builder |

**Gap**: draw.io is dropping PlantUML. Lucidchart's support is minimal. None provide true bidirectional sync between code and canvas. PPTX export is universally weak (image insertion, not native shapes).

---

## 4. AI-Powered Diagram Tools

Tools that use AI to extract or generate diagrams.

### dAIgram
- **Website**: [daigram.app](https://www.daigram.app/)
- **License**: Commercial (by Synergy Codes). White-label options available
- **Core workflow**: Upload a PNG/photo of a hand-drawn or existing diagram → GPT-4o extracts elements → produces a **JSON intermediate representation** (objects, locations, shapes, texts, relationships) → renders as an editable diagram on a canvas
- **JSON export**: Explicit JSON export alongside JPG, PNG, PDF
- **PPTX export**: Supported (also Visio)
- **Human-in-the-loop**: After AI extraction, add/remove objects and arrows, adjust shapes and colors, edit text, undo/redo
- **No PlantUML import**. Not open source
- **Closest commercial competitor** to PictoSync's AI extraction workflow

### Livoa
- **Website**: [livoa.io](https://www.livoa.io/image-to-diagram)
- AI-powered image-to-diagram conversion for flowcharts, mind maps, and diagrams
- Limited information on export formats and intermediate representation

### DiagramGPT (by Eraser)
- **Website**: [eraser.io/diagramgpt](https://www.eraser.io/diagramgpt)
- AI generates diagrams from text prompts — not image-to-diagram
- Outputs to Eraser's own format

### Diagramming AI
- **Website**: [diagrammingai.com](https://diagrammingai.com/)
- AI-generated Mermaid code with Visual Editor converting to Excalidraw canvases
- PlantUML editor with AI generation capabilities
- One-way visual conversion (not true round-trip)

### DeepDiagram
- **Repo**: [github.com/twwch/DeepDiagram](https://github.com/twwch/DeepDiagram)
- **License**: Open source
- AI visualization converting natural language to Mind Maps, Mermaid, ECharts
- 6 core agents. Interactive canvas with zoom/pan/editing
- Human-in-the-loop: refine results by asking AI to modify them

| Capability | dAIgram | Livoa | DiagramGPT | Diagramming AI | DeepDiagram |
|---|:---:|:---:|:---:|:---:|:---:|
| Import PlantUML | No | No | No | Yes | No |
| Visual canvas editing | Yes | Yes | Via Eraser | Via Excalidraw | Yes |
| Bidirectional sync | No | No | No | One-way | No |
| PPTX export | Yes | Unknown | No | No | No |
| PNG/image input | Yes | Yes | No | No | No |
| JSON intermediate format | Yes | Unknown | No | No | No |
| Open source | No | No | No | No | Yes |

**Gap**: dAIgram is the closest to PictoSync's AI workflow (image → JSON → canvas → PPTX), but lacks PlantUML import and bidirectional sync. No AI tool found supports the full PUML → JSON → Canvas round-trip.

---

## 5. C4 Model Tools

Architecture-specific modeling tools, many designed around the C4 model.

### Structurizr
- **Website**: [structurizr.com](https://structurizr.com/)
- **License**: CLI is open source; SaaS is commercial
- Uses its own DSL. CLI exports to **JSON format** ([Structurizr JSON schema](https://github.com/structurizr/json)), PlantUML, Mermaid, D2, DOT, and more
- Structurizr Lite (free) provides a browser-based viewer/editor
- No native PPTX export. No visual drag-and-drop editing. No PNG annotation
- JSON is the workspace interchange format but not designed for manual authoring

### IcePanel
- **Website**: [icepanel.io](https://icepanel.io/)
- **License**: Commercial SaaS
- Exports to **JSON, CSV, SVG, PNG, PDF**. "Smarter exports" added May 2025 (more granular, LLM-friendly)
- Imports from Structurizr and Backstage — **no PlantUML import**
- Visual collaborative editing. No PPTX export

### LikeC4
- **Website**: [likec4.dev](https://likec4.dev/)
- **License**: Open source
- Uses its own `.c4` DSL. Compiles model into multiple diagrams
- **Bidirectional with draw.io**: Export to `.drawio` and import back to `.c4` source — round-tripping between LikeC4 and draw.io
- Exports to PNG (via Playwright), draw.io. Can generate Mermaid, DOT, D2, PlantUML representations
- No native PPTX export. No PlantUML import. No PNG annotation

### C4-PlantUML
- **Repo**: [github.com/plantuml-stdlib/C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
- **License**: Open source
- Extends PlantUML with C4 model macros. Renders via PlantUML server
- Inherits all PlantUML limitations (no visual editing, no PPTX export)

| Capability | Structurizr | IcePanel | LikeC4 | C4-PlantUML |
|---|:---:|:---:|:---:|:---:|
| Import PlantUML | No | No | No | Native |
| Visual canvas editing | No | Yes | Yes | No |
| Bidirectional sync | No | No | With draw.io | No |
| PPTX export | No | No | No | No |
| PNG annotation overlay | No | No | No | No |
| JSON intermediate format | Yes | Yes | No (DSL) | No |
| Open source | Partial | No | Yes | Yes |

**Gap**: C4 tools focus on the modeling layer, not the presentation layer. None support PPTX export or PNG annotation. LikeC4's draw.io round-trip is the most interesting bidirectional story in this category.

---

## 6. JSON-Based Diagram Formats

Tools that use JSON as a native or intermediate representation.

### Excalidraw
- **Website**: [excalidraw.com](https://excalidraw.com/)
- **License**: MIT (open source)
- Uses **plaintext JSON** as its native format (`.excalidraw` files)
- [JSON schema](https://docs.excalidraw.com/docs/codebase/json-schema) documents element types, positions, styles, and relationships
- **PNG metadata embedding**: Exported PNGs can embed the full JSON scene data in PNG metadata, allowing re-import for continued editing — an elegant round-trip pattern
- Full visual canvas editing. Collaborative
- `@excalidraw/mermaid-to-excalidraw` converts Mermaid to Excalidraw JSON (no PlantUML converter)
- No PPTX export

### ToDiagram
- **Website**: [todiagram.com](https://todiagram.com/)
- Turns JSON, YAML, CSV, XML into interactive two-way diagrams and tree views
- Browser-based editor. Not a diagram authoring tool

### JSON Crack
- **Website**: [jsoncrack.com](https://jsoncrack.com/)
- **License**: Open source
- Visualizes JSON/YAML/CSV/XML as interactive graphs
- Data visualization tool, not a diagram authoring tool

### diagram-converter (npm)
- **Package**: [@whitebite/diagram-converter](https://www.npmjs.com/package/@whitebite/diagram-converter)
- Universal format converter between Mermaid, Draw.io, Excalidraw, PlantUML, and DOT (Graphviz)
- Useful as a bridge library for format interoperability, not an end-user tool

| Capability | Excalidraw | ToDiagram | JSON Crack | diagram-converter |
|---|:---:|:---:|:---:|:---:|
| Import PlantUML | No | No | No | Yes (converts) |
| Visual canvas editing | Yes | Yes | View only | N/A (library) |
| Bidirectional sync | No | Two-way data↔diagram | No | N/A |
| PPTX export | No | No | No | No |
| PNG annotation overlay | No | No | No | No |
| JSON intermediate format | Yes (native) | Yes (input) | Yes (input) | Converts formats |
| Open source | Yes | No | Yes | Unknown |

**Gap**: Excalidraw's JSON-native format with PNG metadata embedding is technically elegant, but it lacks PlantUML import and PPTX export. No JSON-based tool found supports the full round-trip workflow.

---

## Key Findings

### 1. No single tool covers the full round-trip

PictoSync's combination of capabilities is **unique** in the current landscape:

```
PlantUML → SVG Parsing → JSON Annotations → Canvas Editing → PPTX Export
    ↑                          ↕                    ↕
    └── AI Extraction ←── PNG Image ←──── Bidirectional Sync
```

No other tool found supports all six pillars: (1) PlantUML import, (2) JSON intermediate representation, (3) visual canvas editing with PNG overlay, (4) bidirectional sync, (5) PPTX export with native shapes, and (6) AI-powered extraction.

### 2. draw.io is dropping PlantUML support

draw.io (diagrams.net) announced removal of PlantUML support at end of 2025 (online version) and 2028 (Confluence/Jira apps). The recommended migration path is PlantUML → Mermaid → draw.io. This creates an opportunity gap for PlantUML-based workflows.

### 3. Closest competitors by capability

| Competitor | Strengths vs PictoSync | Gaps vs PictoSync |
|---|---|---|
| **D2 Studio** | Best bidi sync, PPTX export | No PlantUML, no AI, no PNG overlay |
| **dAIgram** | AI extraction, JSON IR, PPTX | No PlantUML, no bidi sync, not open source |
| **Eraser.io** | PlantUML conversion, AI generation | No PPTX, no bidi sync, no PNG overlay |
| **draw.io** | Dominant market share, open source | Dropping PlantUML, no bidi sync, image-only PPTX |
| **Excalidraw** | JSON native, PNG metadata embedding | No PlantUML, no PPTX, no AI extraction |
| **LikeC4** | draw.io round-trip, open source | No PlantUML import, no PPTX, no AI |

### 4. PPTX export is universally weak

Most tools either don't support PPTX at all, or export diagrams as embedded images (not editable native shapes). PictoSync's approach of exporting as native PowerPoint shapes (rectangles, freeforms, bezier curves, text boxes) with preserved colors, styles, and arrowheads is uncommon.

### 5. Bidirectional sync is rare

True bidirectional synchronization between a text/code representation and visual canvas exists in only three tools: D2 Studio, OxDraw, and PictoSync. Most tools are either code-first (render only) or visual-first (export only).

### 6. AI extraction from images is emerging

dAIgram (GPT-4o) and PictoSync (Google Gemini) are the only tools found that extract diagram elements from PNG images into an editable intermediate format. This is a growing space as multimodal AI models improve.

---

## PictoSync Differentiators

| Differentiator | Detail |
|---|---|
| **Full round-trip** | PUML → JSON → Canvas → PPTX with bidirectional sync at every stage |
| **SVG path preservation** | PlantUML connector curves parsed as native bezier annotations (not simplified to center-to-center lines) |
| **Native PPTX shapes** | Exports as editable PowerPoint shapes with bezier curves, arrowheads, and text — not embedded images |
| **JSON-centric architecture** | All annotations stored as JSON with a defined schema; canvas and editor are synchronized views of the same data |
| **PNG overlay editing** | Draw and refine annotations directly on top of a background PNG image |
| **AI + human workflow** | Gemini extracts initial annotations → human refines on canvas → JSON stays in sync → export to PPTX |
| **OpenCV alignment** | Snap annotations to match visual elements in the background PNG using computer vision |
| **Open source** | MIT license, Python/PyQt6, runs locally with no cloud dependency (except optional AI) |

---

## Sources

- [PlantUML](https://plantuml.com/) | [PlantUML PowerPoint Add-in](https://github.com/kmierzeje/plantuml-powerpoint-addin)
- [Kroki](https://kroki.io/)
- [PlantText](https://www.planttext.com/) | [Pladitor](https://plantumleditor.com/)
- [Ericsson PlantUML Interactive Editor](https://github.com/Ericsson/PlantUML-Interactive-Editor)
- [Terrastruct D2 Studio](https://terrastruct.com/) | [D2 v0.4.1 PPTX export](https://d2lang.com/releases/0.4.1/)
- [Mermaid](https://mermaid.js.org/) | [Mermaid Chart PPTX Plugin](https://docs.mermaidchart.com/plugins/microsoft-powerpoint) | [Mermaid PowerPoint Add-in](https://github.com/accionlabs/mermaid-powerpoint-addin)
- [OxDraw](https://github.com/RohanAdwankar/oxdraw)
- [Eraser.io](https://www.eraser.io/) | [DiagramGPT](https://www.eraser.io/diagramgpt)
- [draw.io PlantUML to Mermaid Migration](https://www.drawio.com/blog/plantuml-to-mermaid) | [draw.io Office Add-in](https://www.drawio.com/doc/faq/microsoft-office-diagrams)
- [plantuml2drawio](https://github.com/doubleSlashde/plantuml2drawio) | [drawio2pptx](https://github.com/mashu3/drawio2pptx)
- [Lucidchart](https://www.lucidchart.com/) | [Lucidchart PlantUML Request](https://community.lucid.co/ideas/implement-proper-integration-with-plantuml-markup-language-7281)
- [Miro](https://miro.com/) | [Miro PlantUML App](https://miro.com/marketplace/plantUML/)
- [Visual Paradigm](https://www.visual-paradigm.com/) | [PlantUML VP Plugin](https://github.com/nbourdi/PlantUML-VP-Plugin)
- [dAIgram](https://www.daigram.app/) | [dAIgram Case Study](https://www.synergycodes.com/portfolio/daigram-case-study)
- [Livoa Image to Diagram](https://www.livoa.io/image-to-diagram)
- [Diagramming AI](https://diagrammingai.com/) | [DeepDiagram](https://github.com/twwch/DeepDiagram)
- [Structurizr](https://structurizr.com/) | [Structurizr JSON Schema](https://github.com/structurizr/json)
- [IcePanel](https://icepanel.io/) | [IcePanel Smarter Exports](https://icepanel.io/blog/2025-05-19-new-smarter-exports)
- [LikeC4](https://likec4.dev/) | [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
- [Excalidraw](https://excalidraw.com/) | [Excalidraw JSON Schema](https://docs.excalidraw.com/docs/codebase/json-schema) | [mermaid-to-excalidraw](https://docs.excalidraw.com/docs/@excalidraw/mermaid-to-excalidraw/api)
- [ToDiagram](https://todiagram.com/) | [JSON Crack](https://jsoncrack.com/)
- [diagram-converter npm](https://www.npmjs.com/package/@whitebite/diagram-converter)
- [JSON Graph Specification](https://github.com/jsongraph/json-graph-specification)

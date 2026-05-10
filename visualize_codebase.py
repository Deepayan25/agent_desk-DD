from __future__ import annotations

import ast
import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}


@dataclass
class FunctionInfo:
    name: str
    lineno: int
    end_lineno: int
    calls: Set[str] = field(default_factory=set)
    attribute_calls: Set[str] = field(default_factory=set)


@dataclass
class ModuleInfo:
    path: Path
    imports_local: Set[str] = field(default_factory=set)
    imports_external: Set[str] = field(default_factory=set)
    functions: List[FunctionInfo] = field(default_factory=list)


class FunctionCallCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: Set[str] = set()
        self.attribute_calls: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            self.calls.add(func.id)
        elif isinstance(func, ast.Attribute):
            parts = []
            current = func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                self.attribute_calls.add(".".join(reversed(parts)))
        self.generic_visit(node)


class CodebaseAnalyzer:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.python_files = self._find_python_files()
        self.local_modules = {path.stem for path in self.python_files}

    def _find_python_files(self) -> List[Path]:
        files: List[Path] = []
        for path in self.root.rglob("*.py"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            files.append(path)
        return sorted(files)

    def analyze(self) -> Dict[str, ModuleInfo]:
        modules: Dict[str, ModuleInfo] = {}
        for path in self.python_files:
            relative_path = path.relative_to(self.root)
            module_name = path.stem
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(relative_path))

            module_info = ModuleInfo(path=relative_path)
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_level = alias.name.split(".")[0]
                        if top_level in self.local_modules:
                            module_info.imports_local.add(top_level)
                        else:
                            module_info.imports_external.add(top_level)
                elif isinstance(node, ast.ImportFrom):
                    if not node.module:
                        continue
                    top_level = node.module.split(".")[0]
                    if top_level in self.local_modules:
                        module_info.imports_local.add(top_level)
                    else:
                        module_info.imports_external.add(top_level)
                elif isinstance(node, ast.FunctionDef):
                    collector = FunctionCallCollector()
                    collector.visit(node)
                    module_info.functions.append(
                        FunctionInfo(
                            name=node.name,
                            lineno=node.lineno,
                            end_lineno=getattr(node, "end_lineno", node.lineno),
                            calls=collector.calls,
                            attribute_calls=collector.attribute_calls,
                        )
                    )

            modules[module_name] = module_info
        return modules


def build_graph(modules: Dict[str, ModuleInfo]) -> Dict[str, object]:
    nodes = []
    links = []
    local_function_names = {
        function.name
        for module in modules.values()
        for function in module.functions
    }

    for module_name, module_info in modules.items():
        file_id = f"module:{module_name}"
        nodes.append(
            {
                "id": file_id,
                "label": module_name,
                "kind": "module",
                "path": str(module_info.path),
                "details": f"Python module at {module_info.path}",
            }
        )

        for local_import in sorted(module_info.imports_local):
            links.append(
                {
                    "source": file_id,
                    "target": f"module:{local_import}",
                    "type": "imports",
                }
            )

        for external_import in sorted(module_info.imports_external):
            package_id = f"external:{external_import}"
            if not any(node["id"] == package_id for node in nodes):
                nodes.append(
                    {
                        "id": package_id,
                        "label": external_import,
                        "kind": "external",
                        "path": "",
                        "details": f"External dependency or stdlib module: {external_import}",
                    }
                )
            links.append(
                {
                    "source": file_id,
                    "target": package_id,
                    "type": "imports",
                }
            )

        for function in module_info.functions:
            function_id = f"function:{module_name}.{function.name}"
            nodes.append(
                {
                    "id": function_id,
                    "label": function.name,
                    "kind": "function",
                    "path": f"{module_info.path}:{function.lineno}",
                    "details": (
                        f"Function {function.name} in {module_info.path} "
                        f"(lines {function.lineno}-{function.end_lineno})"
                    ),
                }
            )
            links.append(
                {
                    "source": file_id,
                    "target": function_id,
                    "type": "defines",
                }
            )

            for call in sorted(function.calls):
                if call in local_function_names:
                    target = next(
                        (
                            f"function:{owner_module}.{owner_function.name}"
                            for owner_module, owner_info in modules.items()
                            for owner_function in owner_info.functions
                            if owner_function.name == call
                        ),
                        None,
                    )
                    if target:
                        links.append(
                            {
                                "source": function_id,
                                "target": target,
                                "type": "calls",
                            }
                        )
                else:
                    builtin_id = f"symbol:{call}"
                    if not any(node["id"] == builtin_id for node in nodes):
                        nodes.append(
                            {
                                "id": builtin_id,
                                "label": call,
                                "kind": "symbol",
                                "path": "",
                                "details": f"Referenced callable symbol: {call}",
                            }
                        )
                    links.append(
                        {
                            "source": function_id,
                            "target": builtin_id,
                            "type": "calls",
                        }
                    )

            for call in sorted(function.attribute_calls):
                symbol_id = f"symbol:{call}"
                if not any(node["id"] == symbol_id for node in nodes):
                    nodes.append(
                        {
                            "id": symbol_id,
                            "label": call,
                            "kind": "symbol",
                            "path": "",
                            "details": f"Qualified call reference: {call}",
                        }
                    )
                links.append(
                    {
                        "source": function_id,
                        "target": symbol_id,
                        "type": "calls",
                    }
                )

    return {
        "nodes": nodes,
        "links": links,
        "summary": {
            "module_count": sum(1 for node in nodes if node["kind"] == "module"),
            "function_count": sum(1 for node in nodes if node["kind"] == "function"),
            "external_count": sum(1 for node in nodes if node["kind"] == "external"),
            "symbol_count": sum(1 for node in nodes if node["kind"] == "symbol"),
            "link_count": len(links),
        },
    }


def render_html(graph: Dict[str, object], title: str) -> str:
    escaped_title = html.escape(title)
    graph_json = json.dumps(graph, indent=2)
    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {{
      --bg: #04070d;
      --bg-grid: rgba(59, 130, 246, 0.08);
      --panel: rgba(5, 12, 22, 0.92);
      --panel-2: rgba(8, 18, 32, 0.88);
      --border: rgba(96, 165, 250, 0.18);
      --text: #d8f3ff;
      --muted: #89a9c7;
      --accent: #22d3ee;
      --accent-2: #7c3aed;
      --success: #2dd4bf;
      --warning: #f59e0b;
      --module: #38bdf8;
      --function: #22c55e;
      --external: #fb7185;
      --symbol: #a78bfa;
      --selected: #f8fafc;
      --neighbor: #67e8f9;
      --trace: #f59e0b;
      --danger: #ef4444;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      color: var(--text);
      min-height: 100vh;
      font-family: "Cascadia Code", "Consolas", "Segoe UI", monospace;
      background:
        linear-gradient(rgba(4, 7, 13, 0.94), rgba(4, 7, 13, 0.98)),
        radial-gradient(circle at 20% 0%, rgba(34, 211, 238, 0.2), transparent 26%),
        radial-gradient(circle at 80% 15%, rgba(124, 58, 237, 0.22), transparent 24%),
        radial-gradient(circle at 50% 100%, rgba(34, 197, 94, 0.16), transparent 28%),
        var(--bg);
      background-color: var(--bg);
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr) 360px;
    }}

    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(var(--bg-grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--bg-grid) 1px, transparent 1px);
      background-size: 36px 36px;
      pointer-events: none;
      mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.75), transparent 92%);
    }}

    .panel {{
      position: relative;
      z-index: 1;
      padding: 22px;
      background: linear-gradient(180deg, rgba(8, 18, 32, 0.95), rgba(5, 12, 22, 0.9));
      backdrop-filter: blur(18px);
      border-right: 1px solid var(--border);
      overflow: auto;
      max-height: 100vh;
    }}

    .panel.right {{
      border-right: none;
      border-left: 1px solid var(--border);
    }}

    .eyebrow {{
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.22em;
      font-size: 0.72rem;
      margin-bottom: 10px;
    }}

    h1 {{
      margin: 0 0 12px;
      font-size: 1.55rem;
      line-height: 1.15;
      text-shadow: 0 0 18px rgba(34, 211, 238, 0.2);
    }}

    h2 {{
      margin: 24px 0 12px;
      font-size: 0.9rem;
      color: var(--accent);
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }}

    p, li {{
      color: var(--muted);
      line-height: 1.55;
    }}

    .stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}

    .card, .section-box {{
      border: 1px solid var(--border);
      border-radius: 16px;
      background:
        linear-gradient(180deg, rgba(11, 27, 48, 0.88), rgba(8, 18, 32, 0.92));
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.03),
        0 0 0 1px rgba(34, 211, 238, 0.02),
        0 18px 40px rgba(0, 0, 0, 0.28);
    }}

    .card {{
      padding: 12px;
    }}

    .card strong {{
      display: block;
      margin-bottom: 4px;
      color: var(--text);
      font-size: 1.25rem;
    }}

    .section-box {{
      padding: 14px;
      margin-top: 12px;
    }}

    .filters {{
      display: grid;
      gap: 10px;
    }}

    label {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text);
      font-size: 0.92rem;
    }}

    input[type="search"],
    textarea {{
      width: 100%;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(96, 165, 250, 0.26);
      background: rgba(7, 16, 30, 0.92);
      color: var(--text);
      outline: none;
      box-shadow: inset 0 0 0 1px rgba(34, 211, 238, 0.02);
    }}

    textarea {{
      min-height: 88px;
      resize: vertical;
      font: inherit;
      line-height: 1.45;
    }}

    input[type="search"]:focus,
    textarea:focus {{
      border-color: rgba(34, 211, 238, 0.6);
      box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.12);
    }}

    button {{
      border: 1px solid rgba(34, 211, 238, 0.28);
      background:
        linear-gradient(180deg, rgba(14, 116, 144, 0.82), rgba(8, 47, 73, 0.94));
      color: var(--text);
      padding: 11px 14px;
      border-radius: 14px;
      cursor: pointer;
      font: inherit;
      transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
      box-shadow: 0 8px 24px rgba(8, 47, 73, 0.32);
    }}

    button:hover {{
      transform: translateY(-1px);
      border-color: rgba(103, 232, 249, 0.54);
      box-shadow: 0 12px 28px rgba(14, 116, 144, 0.34);
    }}

    button.secondary {{
      background:
        linear-gradient(180deg, rgba(49, 46, 129, 0.82), rgba(30, 27, 75, 0.94));
      border-color: rgba(167, 139, 250, 0.26);
    }}

    .button-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }}

    .legend {{
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }}

    .legend span {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
    }}

    .dot {{
      width: 12px;
      height: 12px;
      border-radius: 999px;
      display: inline-block;
      box-shadow: 0 0 12px currentColor;
    }}

    .workspace {{
      position: relative;
      overflow: hidden;
      min-height: 100vh;
    }}

    .workspace::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at center, rgba(34, 211, 238, 0.06), transparent 38%);
      pointer-events: none;
    }}

    svg {{
      position: relative;
      z-index: 1;
      width: 100%;
      height: 100vh;
      display: block;
      cursor: grab;
      touch-action: none;
    }}

    svg.dragging {{
      cursor: grabbing;
    }}

    .help {{
      position: absolute;
      right: 18px;
      bottom: 18px;
      z-index: 2;
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(5, 12, 22, 0.8);
      border: 1px solid var(--border);
      color: var(--muted);
      max-width: 360px;
      font-size: 0.9rem;
      backdrop-filter: blur(14px);
    }}

    .details-title {{
      font-size: 1.12rem;
      margin-bottom: 8px;
      color: var(--text);
    }}

    .meta {{
      padding: 12px;
      border-radius: 14px;
      background: rgba(7, 16, 30, 0.78);
      border: 1px solid rgba(96, 165, 250, 0.14);
      margin-top: 12px;
    }}

    .meta strong {{
      color: var(--text);
    }}

    .node-list {{
      margin-top: 12px;
      padding-left: 18px;
    }}

    .node-list li {{
      margin-bottom: 8px;
    }}

    .empty {{
      color: var(--muted);
      font-style: italic;
    }}

    .status {{
      margin-top: 10px;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid rgba(96, 165, 250, 0.16);
      background: rgba(7, 16, 30, 0.72);
      color: var(--muted);
      font-size: 0.9rem;
    }}

    .status strong {{
      color: var(--text);
    }}

    .step-list {{
      list-style: none;
      padding: 0;
      margin: 12px 0 0;
      display: grid;
      gap: 10px;
    }}

    .step-list li {{
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(7, 16, 30, 0.78);
      border: 1px solid rgba(96, 165, 250, 0.14);
    }}

    .step-list small {{
      display: block;
      margin-top: 4px;
      color: var(--muted);
    }}

    .signal {{
      color: var(--warning);
    }}

    @media (max-width: 1220px) {{
      body {{
        grid-template-columns: 1fr;
      }}

      .panel, .panel.right {{
        border: none;
        max-height: none;
      }}

      svg {{
        height: 72vh;
      }}
    }}
  </style>
</head>
<body>
  <aside class="panel">
    <div class="eyebrow">Interactive Code Surface</div>
    <h1>__TITLE__</h1>
    <p>This graph is generated from your Python files. Select a node to spotlight its local neighborhood, trigger a pulse across the graph, or trace how a particular input would travel through your code.</p>

    <div class="stats" id="stats"></div>

    <h2>Filters</h2>
    <div class="section-box">
      <input id="search" type="search" placeholder="Search files, functions, imports">
      <div class="filters" style="margin-top: 12px;">
        <label><input type="checkbox" id="modules" checked> Show modules</label>
        <label><input type="checkbox" id="functions" checked> Show functions</label>
        <label><input type="checkbox" id="externals" checked> Show external deps</label>
        <label><input type="checkbox" id="symbols" checked> Show call symbols</label>
        <label><input type="checkbox" id="imports" checked> Show import edges</label>
        <label><input type="checkbox" id="calls" checked> Show call edges</label>
        <label><input type="checkbox" id="defines" checked> Show defines edges</label>
      </div>
    </div>

    <h2>Workflow Trace</h2>
    <div class="section-box">
      <p>Type an example user input to map the likely runtime path through your codebase.</p>
      <textarea id="workflowInput" placeholder="Example: type hello in np"></textarea>
      <div class="button-row">
        <button id="traceWorkflow">Trace Workflow</button>
        <button id="clearWorkflow" class="secondary">Clear Trace</button>
      </div>
      <div class="status" id="workflowStatus">
        <strong>Ready:</strong> waiting for an input trace.
      </div>
    </div>

    <h2>Legend</h2>
    <div class="section-box">
      <div class="legend">
        <span><i class="dot" style="background: var(--module)"></i> Module</span>
        <span><i class="dot" style="background: var(--function)"></i> Function</span>
        <span><i class="dot" style="background: var(--external)"></i> External import</span>
        <span><i class="dot" style="background: var(--symbol)"></i> Referenced callable</span>
        <span><i class="dot" style="background: var(--neighbor)"></i> Selected neighbor</span>
        <span><i class="dot" style="background: var(--trace)"></i> Workflow trace</span>
      </div>
    </div>
  </aside>

  <main class="workspace">
    <svg id="graph" viewBox="0 0 1400 900" aria-label="Codebase graph">
      <g id="viewport">
        <g id="links"></g>
        <g id="nodes"></g>
      </g>
    </svg>
    <div class="help">
      Scroll to zoom. Drag the background to pan. Click a node to select it, highlight neighbors, and send a pulse through the graph.
    </div>
  </main>

  <aside class="panel right">
    <h2>Inspector</h2>
    <div id="inspector">
      <p class="empty">Select a node to inspect its details and direct neighbors.</p>
    </div>
    <h2>Trace Steps</h2>
    <div id="workflowSteps">
      <p class="empty">Run a workflow trace to see the probable execution path for an example input.</p>
    </div>
  </aside>

  <script>
    const graph = __GRAPH_JSON__;
    const svg = document.getElementById("graph");
    const viewport = document.getElementById("viewport");
    const linksLayer = document.getElementById("links");
    const nodesLayer = document.getElementById("nodes");
    const inspector = document.getElementById("inspector");
    const searchInput = document.getElementById("search");
    const workflowInput = document.getElementById("workflowInput");
    const workflowStatus = document.getElementById("workflowStatus");
    const workflowSteps = document.getElementById("workflowSteps");
    const traceWorkflowButton = document.getElementById("traceWorkflow");
    const clearWorkflowButton = document.getElementById("clearWorkflow");

    const typeColor = {{
      module: getComputedStyle(document.documentElement).getPropertyValue("--module").trim(),
      function: getComputedStyle(document.documentElement).getPropertyValue("--function").trim(),
      external: getComputedStyle(document.documentElement).getPropertyValue("--external").trim(),
      symbol: getComputedStyle(document.documentElement).getPropertyValue("--symbol").trim(),
    }};

    const filters = {{
      module: document.getElementById("modules"),
      function: document.getElementById("functions"),
      external: document.getElementById("externals"),
      symbol: document.getElementById("symbols"),
      imports: document.getElementById("imports"),
      calls: document.getElementById("calls"),
      defines: document.getElementById("defines"),
    }};

    document.getElementById("stats").innerHTML = `
      <div class="card"><strong>${{graph.summary.module_count}}</strong>Modules</div>
      <div class="card"><strong>${{graph.summary.function_count}}</strong>Functions</div>
      <div class="card"><strong>${{graph.summary.external_count}}</strong>External</div>
      <div class="card"><strong>${{graph.summary.link_count}}</strong>Edges</div>
    `;

    const nodes = graph.nodes.map((node, index) => ({{
      ...node,
      x: 180 + (index % 6) * 180 + Math.random() * 40,
      y: 140 + Math.floor(index / 6) * 120 + Math.random() * 40,
      vx: 0,
      vy: 0,
      radius: node.kind === "module" ? 28 : node.kind === "function" ? 18 : 14,
    }}));

    const nodeMap = new Map(nodes.map(node => [node.id, node]));

    const links = graph.links.map(link => ({{
      ...link,
      sourceNode: nodeMap.get(link.source),
      targetNode: nodeMap.get(link.target),
    }}));

    const adjacency = new Map();
    nodes.forEach(node => adjacency.set(node.id, new Set()));
    links.forEach(link => {{
      adjacency.get(link.source)?.add(link.target);
      adjacency.get(link.target)?.add(link.source);
    }});

    let selectedNode = null;
    let draggedNode = null;
    let selectionNeighbors = new Set();
    let workflowTraceNodeIds = [];
    let workflowTraceNodeSet = new Set();
    let workflowTraceEdgeSet = new Set();
    let workflowTraceStepsData = [];
    let activePulse = null;
    let currentScale = 1;
    let panX = 0;
    let panY = 0;
    let isPanning = false;
    let startPan = {{ x: 0, y: 0 }};
    let backgroundPointerMoved = false;
    let pointerState = null;

    const actionFunctionMap = {{
      open: "function:actions.open_app",
      type: "function:actions.type_text",
      search: "function:actions.search_web",
      play: "function:actions.play_on_youtube",
      wait: "function:actions.wait",
      enter: "function:actions.press_enter",
      del: "function:actions.backspace",
      focus: "function:actions.focus_search",
    }};

    const stopwords = new Set(["i", "want", "to", "wish", "would", "like", "please", "me", "can", "you", "could", "in", "on", "at", "from", "the", "a", "an"]);
    const questionPatterns = ["what is", "what are", "how to", "who is", "where is", "why is"];
    const primitiveActions = new Set(["open", "wait", "enter", "del", "focus"]);
    const platformTokens = new Set(["youtube", "yt", "google", "notepad", "notes", "np", "ggl", "xl", "word"]);

    function linkKey(source, target) {{
      return `${{source}}=>${{target}}`;
    }}

    function visibleKinds() {{
      return new Set(
        Object.entries(filters)
          .filter(([key, input]) => ["imports", "calls", "defines"].includes(key) ? false : input.checked)
          .map(([key]) => key)
      );
    }}

    function matchesSearch(node) {{
      const term = searchInput.value.trim().toLowerCase();
      if (!term) {{
        return true;
      }}
      return [node.label, node.path, node.details].join(" ").toLowerCase().includes(term);
    }}

    function isNodeVisible(node) {{
      return visibleKinds().has(node.kind) && matchesSearch(node);
    }}

    function isLinkVisible(link) {{
      const edgeToggle = filters[link.type];
      return edgeToggle.checked && isNodeVisible(link.sourceNode) && isNodeVisible(link.targetNode);
    }}

    function neighborsOf(nodeId) {{
      return [...(adjacency.get(nodeId) || [])].map(id => nodeMap.get(id)).filter(Boolean);
    }}

    function computeDistances(originId) {{
      const distances = new Map([[originId, 0]]);
      const queue = [originId];
      while (queue.length) {{
        const current = queue.shift();
        const currentDistance = distances.get(current);
        for (const neighbor of adjacency.get(current) || []) {{
          if (!distances.has(neighbor)) {{
            distances.set(neighbor, currentDistance + 1);
            queue.push(neighbor);
          }}
        }}
      }}
      return distances;
    }}

    function selectNode(node) {{
      selectedNode = node;
      selectionNeighbors = new Set(neighborsOf(node.id).map(item => item.id));
      activePulse = {{
        originId: node.id,
        startedAt: performance.now(),
        distances: computeDistances(node.id),
      }};
      renderInspector(node);
      render();
    }}

    function clearSelection() {{
      selectedNode = null;
      selectionNeighbors = new Set();
      activePulse = null;
      renderInspector(null);
      render();
    }}

    function isSelectedOrNeighbor(node) {{
      if (!selectedNode) {{
        return false;
      }}
      return node.id === selectedNode.id || selectionNeighbors.has(node.id);
    }}

    function hasWorkflowTrace() {{
      return workflowTraceNodeIds.length > 0;
    }}

    function nodePulseState(node, now) {{
      if (!activePulse || !activePulse.distances.has(node.id)) {{
        return null;
      }}
      const delay = activePulse.distances.get(node.id) * 150;
      const elapsed = now - activePulse.startedAt - delay;
      if (elapsed < 0 || elapsed > 1100) {{
        return null;
      }}
      const progress = elapsed / 1100;
      return {{
        radius: node.radius + progress * 42,
        opacity: 0.7 * (1 - progress),
      }};
    }}

    function edgePulseState(link, now) {{
      if (!activePulse) {{
        return null;
      }}
      const sourceDistance = activePulse.distances.get(link.source);
      const targetDistance = activePulse.distances.get(link.target);
      if (sourceDistance == null || targetDistance == null) {{
        return null;
      }}
      const delay = Math.min(sourceDistance, targetDistance) * 150;
      const elapsed = now - activePulse.startedAt - delay;
      if (elapsed < 0 || elapsed > 850) {{
        return null;
      }}
      return 0.5 * (1 - elapsed / 850);
    }}

    function renderWorkflowTrace(steps) {{
      if (!steps.length) {{
        workflowSteps.innerHTML = '<p class="empty">Run a workflow trace to see the probable execution path for an example input.</p>';
        return;
      }}
      workflowSteps.innerHTML = `
        <ul class="step-list">
          ${steps.map(step => `
            <li>
              <strong>${step.title}</strong>
              <small>${step.detail}</small>
            </li>
          `).join("")}
        </ul>
      `;
    }}

    function setWorkflowTrace(nodeIds, steps, statusText) {{
      const filteredIds = nodeIds.filter(id => nodeMap.has(id));
      workflowTraceNodeIds = filteredIds;
      workflowTraceNodeSet = new Set(filteredIds);
      workflowTraceEdgeSet = new Set();
      for (let i = 0; i < filteredIds.length - 1; i += 1) {{
        workflowTraceEdgeSet.add(linkKey(filteredIds[i], filteredIds[i + 1]));
        workflowTraceEdgeSet.add(linkKey(filteredIds[i + 1], filteredIds[i]));
      }}
      workflowTraceStepsData = steps;
      workflowStatus.innerHTML = `<strong>Trace:</strong> ${statusText}`;
      renderWorkflowTrace(steps);
      render();
    }}

    function clearWorkflowTrace() {{
      workflowTraceNodeIds = [];
      workflowTraceNodeSet = new Set();
      workflowTraceEdgeSet = new Set();
      workflowTraceStepsData = [];
      workflowStatus.innerHTML = '<strong>Ready:</strong> waiting for an input trace.';
      renderWorkflowTrace([]);
      render();
    }}

    function splitChunks(text) {{
      return text
        .toLowerCase()
        .split(/\\b(?:and then|after that|then|and)\\b/g)
        .map(part => part.trim())
        .filter(Boolean);
    }}

    function inferActionsForChunk(chunk) {{
      const words = chunk.split(/\\s+/).filter(Boolean);
      if (!words.length) {{
        return [];
      }}
      if (primitiveActions.has(words[0])) {{
        return [words[0]];
      }}
      if (questionPatterns.some(pattern => chunk.startsWith(pattern))) {{
        return ["search"];
      }}
      let cleanWords = words.filter(word => !stopwords.has(word));
      const noiseIndex = cleanWords.findIndex(word => ["while", "when", "whilst", "during"].includes(word));
      if (noiseIndex >= 0) {{
        cleanWords = cleanWords.slice(0, noiseIndex);
      }}
      const platform = cleanWords.find(word => platformTokens.has(word));
      const hasType = cleanWords.some(word => ["type", "write"].includes(word));
      if (cleanWords.includes("open")) {{
        return ["open"];
      }}
      if (cleanWords.some(word => ["search", "find"].includes(word))) {{
        return ["search"];
      }}
      if (cleanWords.some(word => ["play", "watch", "listen"].includes(word))) {{
        return ["play"];
      }}
      if (hasType) {{
        return platform ? ["open", "type"] : ["type"];
      }}
      return [];
    }}

    function traceWorkflowFromInput(text) {{
      const trimmed = text.trim();
      if (!trimmed) {{
        setWorkflowTrace([], [], "please enter an example input first.");
        return;
      }}

      const chunks = splitChunks(trimmed);
      const steps = [];
      const nodeIds = [];
      const uniquePush = id => {{
        if (id && nodeMap.has(id) && !nodeIds.includes(id)) {{
          nodeIds.push(id);
        }}
      }};

      uniquePush("module:main");
      steps.push({{
        title: "Input enters the main loop",
        detail: "The command is read by the REPL in main.py and prepared for splitting.",
      }});

      chunks.forEach((chunk, index) => {{
        uniquePush("function:intent.parse_intent");
        steps.push({{
          title: `Chunk ${index + 1}: parse intent`,
          detail: `The chunk "${chunk}" is normalized and interpreted by intent.parse_intent().`,
        }});

        const actions = inferActionsForChunk(chunk);
        uniquePush("function:main.action_parser");
        steps.push({{
          title: `Chunk ${index + 1}: dispatch`,
          detail: actions.length
            ? `main.action_parser() routes the parsed chunk to ${actions.join(" -> ")}.`
            : "main.action_parser() handles fallback dispatch because no clear action pattern was inferred.",
        }});

        uniquePush("module:actions");
        actions.forEach(action => {{
          const targetId = actionFunctionMap[action];
          uniquePush(targetId);
          steps.push({{
            title: `Execute ${action}`,
            detail: `The action registry resolves "${action}" to its concrete handler in actions.py.`,
          }});
        }});
      }});

      if (!nodeIds.length) {{
        setWorkflowTrace([], [], "no traceable runtime path was found for that input.");
        return;
      }}

      setWorkflowTrace(
        nodeIds,
        steps,
        `mapped ${chunks.length} input chunk${chunks.length === 1 ? "" : "s"} through the current runtime pipeline.`,
      );

      const lastNode = nodeMap.get(nodeIds[nodeIds.length - 1]);
      if (lastNode) {{
        selectNode(lastNode);
      }}
    }}

    function renderInspector(node) {{
      if (!node) {{
        inspector.innerHTML = '<p class="empty">Select a node to inspect its details and direct neighbors.</p>';
        return;
      }}
      const neighbors = neighborsOf(node.id)
        .sort((a, b) => a.label.localeCompare(b.label))
        .map(neighbor => `<li>${{neighbor.label}} <span style="color: var(--muted)">(${{
          neighbor.kind
        }})</span></li>`)
        .join("");
      inspector.innerHTML = `
        <div class="details-title">${{node.label}}</div>
        <p>${{node.details}}</p>
        <div class="meta"><strong>Kind:</strong> ${{node.kind}}</div>
        <div class="meta"><strong>Location:</strong> ${{node.path || "N/A"}}</div>
        <div class="meta"><strong>Connected nodes:</strong> ${{neighborsOf(node.id).length}}</div>
        <div class="meta"><strong>Neighbors:</strong></div>
        ${
          neighbors
            ? `<ul class="node-list">${{neighbors}}</ul>`
            : '<p class="empty">No direct neighbors in the current graph.</p>'
        }
      `;
    }}

    function updateViewportTransform() {{
      viewport.setAttribute("transform", `translate(${{panX}} ${{panY}}) scale(${{currentScale}})`);
    }}

    function render() {{
      const now = performance.now();
      linksLayer.innerHTML = "";
      nodesLayer.innerHTML = "";

      links.filter(isLinkVisible).forEach(link => {{
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", link.sourceNode.x);
        line.setAttribute("y1", link.sourceNode.y);
        line.setAttribute("x2", link.targetNode.x);
        line.setAttribute("y2", link.targetNode.y);
        const selectedEdge = selectedNode && (
          (link.source === selectedNode.id && selectionNeighbors.has(link.target)) ||
          (link.target === selectedNode.id && selectionNeighbors.has(link.source))
        );
        const tracedEdge = workflowTraceEdgeSet.has(linkKey(link.source, link.target));
        const pulse = edgePulseState(link, now);
        let stroke = link.type === "calls" ? "rgba(245, 158, 11, 0.42)" : "rgba(103, 232, 249, 0.16)";
        let strokeWidth = link.type === "defines" ? 1.4 : 1.8;
        if (selectedEdge) {{
          stroke = "rgba(103, 232, 249, 0.92)";
          strokeWidth = 3;
        }} else if (tracedEdge) {{
          stroke = "rgba(245, 158, 11, 0.88)";
          strokeWidth = 3;
        }}
        if (pulse) {{
          stroke = `rgba(248, 250, 252, ${{Math.min(0.96, 0.34 + pulse)}})`;
          strokeWidth = Math.max(strokeWidth, 2.4 + pulse * 4);
        }}
        if (selectedNode && !selectedEdge && !tracedEdge) {{
          line.setAttribute("opacity", "0.24");
        }}
        line.setAttribute("stroke", stroke);
        line.setAttribute("stroke-width", strokeWidth);
        line.setAttribute("stroke-dasharray", link.type === "imports" ? "6 6" : "0");
        linksLayer.appendChild(line);
      }});

      nodes.filter(isNodeVisible).forEach(node => {{
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.style.cursor = "pointer";
        group.dataset.nodeId = node.id;
        group.dataset.kind = node.kind;

        const pulseState = nodePulseState(node, now);
        if (pulseState) {{
          const pulseRing = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          pulseRing.setAttribute("cx", node.x);
          pulseRing.setAttribute("cy", node.y);
          pulseRing.setAttribute("r", pulseState.radius);
          pulseRing.setAttribute("fill", "none");
          pulseRing.setAttribute("stroke", "rgba(248, 250, 252, 0.9)");
          pulseRing.setAttribute("stroke-width", "2");
          pulseRing.setAttribute("stroke-opacity", pulseState.opacity);
          group.appendChild(pulseRing);
        }}

        const selected = selectedNode && selectedNode.id === node.id;
        const neighbor = !selected && selectionNeighbors.has(node.id);
        const traced = workflowTraceNodeSet.has(node.id);
        const dimmed = selectedNode && !selected && !neighbor && !traced;

        if (selected || neighbor || traced) {{
          const halo = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          halo.setAttribute("cx", node.x);
          halo.setAttribute("cy", node.y);
          halo.setAttribute("r", node.radius + (selected ? 13 : neighbor ? 10 : 9));
          halo.setAttribute("fill", selected ? "rgba(248,250,252,0.18)" : neighbor ? "rgba(103,232,249,0.16)" : "rgba(245,158,11,0.18)");
          halo.setAttribute("stroke", "none");
          group.appendChild(halo);
        }}

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", node.x);
        circle.setAttribute("cy", node.y);
        circle.setAttribute("r", node.radius);
        circle.setAttribute("fill", selected ? "rgba(248,250,252,0.98)" : traced ? "rgba(245,158,11,0.94)" : neighbor ? "rgba(103,232,249,0.96)" : typeColor[node.kind]);
        circle.setAttribute("fill-opacity", dimmed ? "0.24" : selected ? "1" : "0.9");
        circle.setAttribute("stroke", selected ? "rgba(255,255,255,1)" : traced ? "rgba(245,158,11,1)" : neighbor ? "rgba(103,232,249,1)" : "rgba(255,255,255,0.16)");
        circle.setAttribute("stroke-width", selected ? "3.6" : traced || neighbor ? "2.6" : "1.3");

        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("x", node.x);
        label.setAttribute("y", node.y + node.radius + 18);
        label.setAttribute("fill", selected ? "#ffffff" : traced ? "#fcd34d" : neighbor ? "#a5f3fc" : "#d8f3ff");
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("font-size", "13");
        label.setAttribute("font-weight", selected || neighbor || traced ? "700" : "500");
        label.setAttribute("opacity", dimmed ? "0.28" : "1");
        label.textContent = node.label;

        group.append(circle, label);
        nodesLayer.appendChild(group);
      }});
    }}

    function stepSimulation() {{
      const visibleNodes = nodes.filter(isNodeVisible);
      const visibleLinks = links.filter(isLinkVisible);

      for (let i = 0; i < visibleNodes.length; i += 1) {{
        for (let j = i + 1; j < visibleNodes.length; j += 1) {{
          const a = visibleNodes[i];
          const b = visibleNodes[j];
          let dx = b.x - a.x;
          let dy = b.y - a.y;
          const distanceSq = dx * dx + dy * dy + 0.01;
          const distance = Math.sqrt(distanceSq);
          const force = 2600 / distanceSq;
          dx /= distance;
          dy /= distance;
          a.vx -= dx * force;
          a.vy -= dy * force;
          b.vx += dx * force;
          b.vy += dy * force;
        }}
      }}

      visibleLinks.forEach(link => {{
        const a = link.sourceNode;
        const b = link.targetNode;
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        const distance = Math.sqrt(dx * dx + dy * dy) || 1;
        const desired = link.type === "defines" ? 110 : 170;
        const spring = (distance - desired) * 0.0035;
        dx /= distance;
        dy /= distance;
        a.vx += dx * spring;
        a.vy += dy * spring;
        b.vx -= dx * spring;
        b.vy -= dy * spring;
      }});

      visibleNodes.forEach(node => {{
        if (draggedNode && draggedNode.id === node.id) {{
          return;
        }}
        node.vx *= 0.86;
        node.vy *= 0.86;
        node.x += node.vx;
        node.y += node.vy;
      }});

      render();
      requestAnimationFrame(stepSimulation);
    }}

    function screenToGraph(clientX, clientY) {{
      const rect = svg.getBoundingClientRect();
      return {{
        x: (clientX - rect.left - panX) / currentScale,
        y: (clientY - rect.top - panY) / currentScale,
      }};
    }}

    function findNodeFromEventTarget(target) {{
      const group = target.closest("g[data-node-id]");
      if (!group) {{
        return null;
      }}
      return nodeMap.get(group.dataset.nodeId) || null;
    }}

    svg.addEventListener("wheel", event => {{
      event.preventDefault();
      const scaleFactor = event.deltaY < 0 ? 1.08 : 0.92;
      const point = screenToGraph(event.clientX, event.clientY);
      currentScale = Math.min(3, Math.max(0.45, currentScale * scaleFactor));
      panX = event.clientX - svg.getBoundingClientRect().left - point.x * currentScale;
      panY = event.clientY - svg.getBoundingClientRect().top - point.y * currentScale;
      updateViewportTransform();
    }}, {{ passive: false }});

    svg.addEventListener("pointerdown", event => {{
      const node = findNodeFromEventTarget(event.target);
      if (node) {{
        event.stopPropagation();
        draggedNode = node;
        node.vx = 0;
        node.vy = 0;
        const point = screenToGraph(event.clientX, event.clientY);
        node.dragOffsetX = point.x - node.x;
        node.dragOffsetY = point.y - node.y;
        pointerState = {{
          nodeId: node.id,
          startClientX: event.clientX,
          startClientY: event.clientY,
          moved: false,
        }};
        return;
      }}
      isPanning = true;
      backgroundPointerMoved = false;
      svg.classList.add("dragging");
      startPan = {{ x: event.clientX - panX, y: event.clientY - panY }};
    }});

    window.addEventListener("pointermove", event => {{
      if (draggedNode) {{
        const point = screenToGraph(event.clientX, event.clientY);
        draggedNode.x = point.x - draggedNode.dragOffsetX;
        draggedNode.y = point.y - draggedNode.dragOffsetY;
        if (pointerState) {{
          const moved = Math.hypot(
            event.clientX - pointerState.startClientX,
            event.clientY - pointerState.startClientY
          );
          if (moved > 6) {{
            pointerState.moved = true;
          }}
        }}
        render();
      }} else if (isPanning) {{
        panX = event.clientX - startPan.x;
        panY = event.clientY - startPan.y;
        backgroundPointerMoved = true;
        updateViewportTransform();
      }}
    }});

    window.addEventListener("pointerup", () => {{
      if (draggedNode && pointerState && !pointerState.moved && draggedNode.id === pointerState.nodeId) {{
        selectNode(draggedNode);
      }}
      draggedNode = null;
      pointerState = null;
      isPanning = false;
      svg.classList.remove("dragging");
    }});

    svg.addEventListener("click", event => {{
      if (findNodeFromEventTarget(event.target)) {{
        return;
      }}
      if (!backgroundPointerMoved) {{
        clearSelection();
      }}
      backgroundPointerMoved = false;
    }});

    searchInput.addEventListener("input", render);
    Object.values(filters).forEach(input => input.addEventListener("change", render));
    traceWorkflowButton.addEventListener("click", () => traceWorkflowFromInput(workflowInput.value));
    clearWorkflowButton.addEventListener("click", clearWorkflowTrace);
    workflowInput.addEventListener("keydown", event => {{
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {{
        traceWorkflowFromInput(workflowInput.value);
      }}
    }});

    updateViewportTransform();
    renderInspector(null);
    renderWorkflowTrace([]);
    render();
    requestAnimationFrame(stepSimulation);
  </script>
</body>
</html>
"""
    normalized = template.replace("{{", "{").replace("}}", "}")
    return normalized.replace("__TITLE__", escaped_title).replace("__GRAPH_JSON__", graph_json)


def write_graph(output_path: Path, root: Path) -> Path:
    analyzer = CodebaseAnalyzer(root)
    graph = build_graph(analyzer.analyze())
    output_path.write_text(
        render_html(graph, f"{root.name} Codebase Graph"),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    root = Path(__file__).resolve().parent
    output_path = root / "codebase_graph.html"
    write_graph(output_path, root)
    print(f"Generated interactive graph at: {output_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SCADE-X Diagram Generator
=========================
Programmatically renders 20 high-quality, professional, publication-ready diagrams
for the SCADE-X system documentation using Matplotlib and NetworkX.
"""
import os
import math
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Headless mode
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Professional Color Palette
C_PRIMARY = "#1A365D"      # Navy Blue (Headers, critical boundaries)
C_SECONDARY = "#2B6CB0"    # Medium Blue (Subsystems, normal operations)
C_ACCENT = "#319795"       # Deep Teal (Fusions, structural metrics)
C_HIGHLIGHT = "#D69E2E"    # Warm Gold/Amber (Warnings, risk amplification)
C_DANGER = "#C53030"       # Muted Red (Violations, immediate actions)
C_BG = "#F7FAFC"           # Off-white / Light Grey (Box backgrounds)
C_TEXT = "#2D3748"         # Charcoal (General text)
C_TEXT_LIGHT = "#FFFFFF"   # White (Text on dark nodes)
C_BORDER = "#CBD5E0"       # Light Slate (Borders)
C_MUTED = "#718096"        # Slate (Arrows, auxiliary details)

def setup_ax():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    return fig, ax

def draw_box(ax, text, x, y, w, h, facecolor, edgecolor=C_BORDER, text_color=C_TEXT, font_weight='normal', font_size=8, alignment='center'):
    # Draw rounded rectangle
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.2,
        mutation_scale=1.0,
        zorder=3
    )
    ax.add_patch(rect)
    
    # Text placement
    ty = y + h / 2.0
    if alignment == 'center':
        tx = x + w / 2.0
        ax.text(tx, ty, text, color=text_color, fontsize=font_size, fontweight=font_weight,
                ha='center', va='center', zorder=4, wrap=True)
    else:
        tx = x + 0.05
        ax.text(tx, ty, text, color=text_color, fontsize=font_size, fontweight=font_weight,
                ha='left', va='center', zorder=4, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, text=None, text_offset_y=0.04, color=C_MUTED, line_style='-'):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle="arc3",
            color=color,
            linewidth=1.3,
            linestyle=line_style,
            mutation_scale=12,
            zorder=2
        )
    )
    if text:
        tx = (x1 + x2) / 2.0
        ty = (y1 + y2) / 2.0 + text_offset_y
        ax.text(tx, ty, text, color=C_MUTED, fontsize=7.5, ha='center', va='center', zorder=5)

def save_fig(fig, output_path, title):
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Generated: {title} -> {output_path.name}")

# ==========================================
# DIAGRAMS DEFINITIONS
# ==========================================

def render_diagram_1(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    # Title
    ax.text(5, 5.7, "Figure 1: High-Level SCADE-X Hybrid Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    # Nodes
    draw_box(ax, "Raw Supply Chain logs\n(synthetic_supply_chain.csv)", 0.2, 2.2, 2.0, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "ASTRA Subsystem\n(Deep Learning Anomaly)", 2.8, 3.4, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "SCADE Subsystem\n(Deterministic Conformance)", 2.8, 1.2, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Schema Normalizer\n(unified_case_intelligence.csv)", 5.4, 2.3, 1.8, 1.0, C_ACCENT, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Supply Chain Resilience & Fusion\n(Propagated Risk, TTR/TTS Gaps)", 7.8, 2.3, 2.0, 1.0, C_HIGHLIGHT, text_color=C_TEXT, font_weight='bold')
    draw_box(ax, "Actionable Outputs\n(Mitigations & Explanations)", 7.8, 0.4, 2.0, 0.9, C_BG, text_color=C_TEXT, font_weight='bold')
    
    # Arrows
    draw_arrow(ax, 2.2, 2.8, 2.7, 3.9, "Raw Log Ingestion")
    draw_arrow(ax, 2.2, 2.8, 2.7, 1.7, "Raw Log Ingestion")
    
    draw_arrow(ax, 4.8, 3.9, 5.3, 2.9, "fused_risk_scores.csv")
    draw_arrow(ax, 4.8, 1.7, 5.3, 2.7, "results.csv")
    
    draw_arrow(ax, 7.2, 2.8, 7.7, 2.8, "Normalised Schema")
    draw_arrow(ax, 8.8, 2.3, 8.8, 1.3, "Decision Engine")
    
    save_fig(fig, path, "Diagram 1: High-Level Architecture")

def render_diagram_2(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    
    ax.text(6, 6.6, "Figure 2: End-to-End Pipeline Execution Sequence", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    stages = [
        "1. Input Validation", "2. Env Validation", "3. ASTRA Subprocess", "4. SCADE Subprocess",
        "5. Schema Normalisation", "6. Resilience Intelligence", "7. Hybrid Fusion", "8. Decision Engine",
        "9. Explainability (XAI)", "10. Benchmarking", "11. Artifact Export"
    ]
    
    for i, stage in enumerate(stages):
        # Calculate grid position
        row = i // 4
        col = i % 4
        x = 0.5 + col * 2.8
        y = 4.8 - row * 2.0
        
        color = C_PRIMARY if i in [0, 1] else (C_SECONDARY if i in [2, 3] else (C_ACCENT if i in [4, 5, 6] else C_HIGHLIGHT))
        text_color = C_TEXT_LIGHT if color != C_HIGHLIGHT else C_TEXT
        
        draw_box(ax, stage, x, y, 2.4, 1.0, color, text_color=text_color, font_weight='bold', font_size=8.5)
        
        # Draw flow arrow
        if col < 3 and i < len(stages) - 1:
            draw_arrow(ax, x + 2.4, y + 0.5, x + 2.8, y + 0.5)
        elif col == 3 and i < len(stages) - 1:
            draw_arrow(ax, x + 1.2, y, x + 1.2, y - 1.0)
            
    save_fig(fig, path, "Diagram 2: End-to-End Pipeline")

def render_diagram_3(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 3: ASTRA Subsystem Internal Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Input Event Logs\n(Pandas Dataframe)", 0.2, 2.2, 2.0, 1.2, C_BG, font_weight='bold')
    
    # Parallel paths
    draw_box(ax, "Activity Sequence Tokenizer\n& Embedding Generation", 2.8, 3.8, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Transformer Sequence Encoder\n(Multi-Head Self-Attention)", 5.2, 3.8, 2.0, 1.0, C_PRIMARY, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Continuous Numeric Features\n(Duration, Amount, Counts)", 2.8, 2.3, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Isolation Forest\n(Probabilistic Anomaly Scoring)", 5.2, 2.3, 2.0, 1.0, C_PRIMARY, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Bipartite Centrality\n(Case-Supplier Graph)", 2.8, 0.8, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Topological Graph Metrics\n(Degree & PageRank)", 5.2, 0.8, 2.0, 1.0, C_PRIMARY, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "ASTRA Risk Fusion\n(fused_risk_scores.csv)", 7.8, 2.2, 2.0, 1.2, C_HIGHLIGHT, font_weight='bold')
    
    # Connections
    draw_arrow(ax, 2.2, 3.2, 2.7, 4.3)
    draw_arrow(ax, 2.2, 2.8, 2.7, 2.8)
    draw_arrow(ax, 2.2, 2.4, 2.7, 1.3)
    
    draw_arrow(ax, 4.8, 4.3, 5.1, 4.3)
    draw_arrow(ax, 4.8, 2.8, 5.1, 2.8)
    draw_arrow(ax, 4.8, 1.3, 5.1, 1.3)
    
    draw_arrow(ax, 7.2, 4.3, 7.7, 3.2)
    draw_arrow(ax, 7.2, 2.8, 7.7, 2.8)
    draw_arrow(ax, 7.2, 1.3, 7.7, 2.4)
    
    save_fig(fig, path, "Diagram 3: ASTRA Internal")

def render_diagram_4(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    
    ax.text(5.5, 5.7, "Figure 4: SCADE Subsystem Internal Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Event Log Logins\n(SIEM + ERP Logs)", 0.2, 2.2, 2.0, 1.2, C_BG, font_weight='bold')
    
    draw_box(ax, "Inductive Miner Discovery\n(Algorithm discovers Petri Net)", 2.6, 2.2, 2.0, 1.2, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Multi-perspectives
    perspectives = [
        "Control Flow Conformance\n(Token-Based Replay cf_score)",
        "Temporal Drift Bounds\n(Gaussian Limits time_score)",
        "Segregation of Duties\n(Resource resource_score)",
        "Financial Amount Delta\n(amount_score)",
        "SIEM Security Context\n(security_score)"
    ]
    
    for i, p in enumerate(perspectives):
        py = 4.4 - i * 1.0
        draw_box(ax, p, 5.2, py, 3.0, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
        draw_arrow(ax, 4.6, 2.8, 5.1, py + 0.4)
        draw_arrow(ax, 8.2, py + 0.4, 8.7, 2.8)
        
    draw_box(ax, "SCADE Composite Score\n(results.csv)", 8.8, 2.2, 2.0, 1.2, C_HIGHLIGHT, font_weight='bold')
    
    draw_arrow(ax, 2.2, 2.8, 2.5, 2.8)
    draw_arrow(ax, 4.6, 2.8, 5.1, 2.8)
    
    save_fig(fig, path, "Diagram 4: SCADE Internal")

def render_diagram_5(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 5: Supply Chain Resilience (SCR) Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Case & Supplier Mapping\n(NetworkX Graph)", 0.2, 2.2, 2.0, 1.2, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Dynamic Math blocks
    draw_box(ax, "Supplier Criticality\n(Degree & PageRank)", 2.8, 3.8, 2.0, 1.0, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Structural Bottlenecks\n(Betweenness Centrality)", 2.8, 2.3, 2.0, 1.0, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Cascading Propagation\n(Damped Diffusion alpha=0.3)", 2.8, 0.8, 2.0, 1.0, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Kinetics & Survival Estimation\n(TTR vs TTS Windows)", 5.4, 2.2, 2.0, 1.2, C_HIGHLIGHT, font_weight='bold')
    draw_box(ax, "Mitigation & Priority Engine\n(resilience_intelligence.csv)", 7.8, 2.2, 2.0, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Connections
    draw_arrow(ax, 2.2, 3.2, 2.7, 4.3)
    draw_arrow(ax, 2.2, 2.8, 2.7, 2.8)
    draw_arrow(ax, 2.2, 2.4, 2.7, 1.3)
    
    draw_arrow(ax, 4.8, 4.3, 5.3, 3.2)
    draw_arrow(ax, 4.8, 2.8, 5.3, 2.8)
    draw_arrow(ax, 4.8, 1.3, 5.3, 2.4)
    
    draw_arrow(ax, 7.4, 2.8, 7.7, 2.8)
    
    save_fig(fig, path, "Diagram 5: SCR Architecture")

def render_diagram_6(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 6: Intelligence Fusion Engine Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    # Inputs
    draw_box(ax, "SCADE Conformance Failure\n(S_r = 1 - SCADE)", 0.2, 3.6, 2.2, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "ASTRA Anomaly Risk\n(A_r = Transformer + IF)", 0.2, 1.4, 2.2, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Convex Blend
    draw_box(ax, "Base Risk Convex Blend\nR_base = 0.7*max + 0.3*avg", 3.0, 2.3, 2.2, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Resilience Modifiers
    draw_box(ax, "Resilience Modifiers\n- Graph Propagation (P_risk)\n- Systemic Vulnerability (V_sys)\n- Time Survival Gap (Gap)", 5.6, 2.1, 2.0, 1.6, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    
    # Final outputs
    draw_box(ax, "Final Systemic Threat\nR_final = min(1.0, R_base * Amplification)\n(scadex_final_intelligence.csv)", 8.0, 2.2, 1.8, 1.4, C_HIGHLIGHT, font_size=8, font_weight='bold')
    
    # Connect
    draw_arrow(ax, 2.4, 4.1, 2.9, 3.1)
    draw_arrow(ax, 2.4, 1.9, 2.9, 2.7)
    draw_arrow(ax, 5.2, 2.9, 5.5, 2.9)
    draw_arrow(ax, 7.6, 2.9, 7.9, 2.9)
    
    save_fig(fig, path, "Diagram 6: Intelligence Fusion")

def render_diagram_7(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 7: Forensic Explainability (XAI) Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Fused Case Intelligence\n(final_risk_score)", 0.2, 2.2, 2.0, 1.2, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Root Cause Filter\n(flags cases with risk > 0.75)", 2.8, 2.2, 2.0, 1.2, C_ACCENT, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Explanation Builder\n- Extracts contributing signals\n- Computes math parameter metrics", 5.2, 3.4, 2.2, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Action Recommendation\n- Prescribes recovery actions\n- Sets SLA escalation timelines", 5.2, 1.2, 2.2, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Forensic Auditing Reports\n(reports/case_report_*.md & *.json)", 7.8, 2.2, 2.0, 1.2, C_HIGHLIGHT, font_weight='bold')
    
    # Connect
    draw_arrow(ax, 2.2, 2.8, 2.7, 2.8)
    draw_arrow(ax, 4.8, 3.1, 5.1, 3.8)
    draw_arrow(ax, 4.8, 2.5, 5.1, 1.8)
    draw_arrow(ax, 7.4, 3.8, 7.7, 3.1)
    draw_arrow(ax, 7.4, 1.8, 7.7, 2.5)
    
    save_fig(fig, path, "Diagram 7: Explainability XAI")

def render_diagram_8(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 8: Benchmarking & Ablation Testing Engine", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Ground Truth Labels\n(is_ground_truth_anomaly)", 0.2, 2.2, 2.0, 1.2, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Ablations
    draw_box(ax, "Ablation Run 1\nASTRA Signals Only", 2.8, 4.4, 2.0, 0.9, C_BG, font_size=8)
    draw_box(ax, "Ablation Run 2\nSCADE Signals Only", 2.8, 3.2, 2.0, 0.9, C_BG, font_size=8)
    draw_box(ax, "Ablation Run 3\nFusion (No Resilience)", 2.8, 2.0, 2.0, 0.9, C_BG, font_size=8)
    draw_box(ax, "Ablation Run 4\nFull Unified SCADE-X", 2.8, 0.8, 2.0, 0.9, C_PRIMARY, text_color=C_TEXT_LIGHT, font_size=8, font_weight='bold')
    
    draw_box(ax, "Metrics Evaluator\n- ROC-AUC / PR-AUC\n- Precision, Recall, F1", 5.4, 2.2, 2.0, 1.2, C_ACCENT, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "Validation Performance\n(scadex_benchmark.csv & plots)", 7.8, 2.2, 2.0, 1.2, C_HIGHLIGHT, font_weight='bold')
    
    # Connect
    for i in range(4):
        ay = 4.85 - i * 1.2
        draw_arrow(ax, 2.2, 2.8, 2.7, ay)
        draw_arrow(ax, 4.8, ay, 5.3, 2.8)
    draw_arrow(ax, 7.4, 2.8, 7.7, 2.8)
    
    save_fig(fig, path, "Diagram 8: Benchmarking")

def render_diagram_9(path):
    fig, ax = setup_ax()
    ax.text(0.5, 0.95, "Figure 9: Module Internal Dependency Graph", transform=ax.transAxes, fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    G = nx.DiGraph()
    modules = [
        "Orchestration", "ASTRA Runner", "SCADE Runner", "Schema Normalizer",
        "Resilience Engine", "Fusion Engine", "Explainability Engine", "Benchmarking Engine"
    ]
    G.add_nodes_from(modules)
    edges = [
        ("Orchestration", "ASTRA Runner"),
        ("Orchestration", "SCADE Runner"),
        ("Orchestration", "Schema Normalizer"),
        ("Orchestration", "Resilience Engine"),
        ("Orchestration", "Fusion Engine"),
        ("Orchestration", "Explainability Engine"),
        ("Orchestration", "Benchmarking Engine"),
        ("ASTRA Runner", "Schema Normalizer"),
        ("SCADE Runner", "Schema Normalizer"),
        ("Schema Normalizer", "Resilience Engine"),
        ("Resilience Engine", "Fusion Engine"),
        ("Fusion Engine", "Explainability Engine"),
        ("Fusion Engine", "Benchmarking Engine")
    ]
    G.add_edges_from(edges)
    
    pos = {
        "Orchestration": (0, 0),
        "ASTRA Runner": (-2, -1.5),
        "SCADE Runner": (2, -1.5),
        "Schema Normalizer": (0, -3),
        "Resilience Engine": (0, -4.5),
        "Fusion Engine": (0, -6),
        "Explainability Engine": (-2, -7.5),
        "Benchmarking Engine": (2, -7.5)
    }
    
    # Draw nodes and edges beautifully
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=C_PRIMARY, node_size=1800, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color=C_TEXT_LIGHT, font_size=7, font_weight='bold')
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=edges, edge_color=C_MUTED, width=1.5, arrowsize=15)
    
    save_fig(fig, path, "Diagram 9: Module Dependencies")

def render_diagram_10(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 10: SCADE-X Repository Structure Map", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "SCADE-X Root /", 0.2, 2.4, 1.8, 0.8, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    folders = [
        "astra/  (ASTRA Deep Learning)",
        "scade/  (SCADE Process Mining)",
        "src/    (SCADE-X Orchestration & Core Math)",
        "configs/ (YAML configurations)",
        "data/   (Raw, intermediate & processed files)",
        "outputs/ (Reports, benchmarks & finals)"
    ]
    
    for i, f in enumerate(folders):
        fy = 4.5 - i * 0.8
        draw_box(ax, f, 3.0, fy, 4.0, 0.6, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8, alignment='left')
        draw_arrow(ax, 2.0, 2.8, 2.9, fy + 0.3)
        
    save_fig(fig, path, "Diagram 10: Folder Structure Map")

def render_diagram_11(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 11: Execution Dependency Tree", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    # Chronological call flow layers
    draw_box(ax, "CLI Entry point\n(main.py)", 3.8, 4.8, 2.4, 0.8, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Pipeline Orchestrator\n(scadex_pipeline.py)", 3.8, 3.6, 2.4, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Environment Validator\n(environment_validator.py)", 0.6, 2.4, 2.2, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Subprocess Subsystems\n(astra_runner.py, scade_runner.py)", 3.8, 2.4, 2.4, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Logical Executions\n(resilience_engine.py, etc.)", 7.2, 2.4, 2.2, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Artifact Serialization\n(outputs/ final folders)", 3.8, 1.0, 2.4, 0.8, C_HIGHLIGHT, font_weight='bold')
    
    # Connecting arrows
    draw_arrow(ax, 5.0, 4.8, 5.0, 4.4)
    draw_arrow(ax, 4.0, 3.6, 1.7, 3.2)
    draw_arrow(ax, 5.0, 3.6, 5.0, 3.2)
    draw_arrow(ax, 6.0, 3.6, 8.3, 3.2)
    
    draw_arrow(ax, 1.7, 2.4, 5.0, 1.8)
    draw_arrow(ax, 5.0, 2.4, 5.0, 1.8)
    draw_arrow(ax, 8.3, 2.4, 5.0, 1.8)
    
    save_fig(fig, path, "Diagram 11: Execution Dependency Tree")

def render_diagram_12(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    
    ax.text(5.5, 5.7, "Figure 12: SCADE-X Data Lineage & Schema Flow", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Raw CSV Logs\n(synthetic_supply_chain.csv)", 0.2, 2.2, 1.8, 1.2, C_BG, font_weight='bold')
    
    draw_box(ax, "ASTRA Scores\n(fused_risk_scores.csv)", 2.4, 3.4, 1.8, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "SCADE Conformance\n(results.csv)", 2.4, 1.2, 1.8, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Canonical Mapping\n(unified_case_intelligence.csv)", 4.6, 2.3, 1.8, 1.0, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Vulnerability & Gaps\n(resilience_intelligence.csv)", 6.8, 2.3, 1.8, 1.0, C_HIGHLIGHT, font_size=8)
    
    draw_box(ax, "Final Systemic Matrix\n(scadex_final_intelligence.csv)", 9.0, 2.2, 1.8, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold', font_size=8)
    
    # Lineage Arrows
    draw_arrow(ax, 2.0, 2.8, 2.3, 3.9)
    draw_arrow(ax, 2.0, 2.8, 2.3, 1.7)
    draw_arrow(ax, 4.2, 3.9, 4.5, 2.8)
    draw_arrow(ax, 4.2, 1.7, 4.5, 2.8)
    draw_arrow(ax, 6.4, 2.8, 6.7, 2.8)
    draw_arrow(ax, 8.6, 2.8, 8.9, 2.8)
    
    save_fig(fig, path, "Diagram 12: Data Lineage")

def render_diagram_13(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 13: Runtime Orchestration Flow", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "RuntimeManager\n(Governs Stages, captures timestamps)", 0.2, 2.2, 2.0, 1.2, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Start Stage\n(Allocates CPU context)", 2.8, 3.8, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Run Operation\n(Invokes subprocesses or python code)", 2.8, 2.3, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Intercept Failures\n(Non-fatal log or systemic abort)", 2.8, 0.8, 2.0, 1.0, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    
    draw_box(ax, "Stage Success / Fail\n(Logs durations, writes system audits)", 5.4, 2.2, 2.0, 1.2, C_ACCENT, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "Pipeline Summary\n(Final execution diagnostics)", 7.8, 2.2, 2.0, 1.2, C_HIGHLIGHT, font_weight='bold')
    
    # Flows
    draw_arrow(ax, 2.2, 3.2, 2.7, 4.3)
    draw_arrow(ax, 2.2, 2.8, 2.7, 2.8)
    draw_arrow(ax, 2.2, 2.4, 2.7, 1.3)
    
    draw_arrow(ax, 4.8, 4.3, 5.3, 3.2)
    draw_arrow(ax, 4.8, 2.8, 5.3, 2.8)
    draw_arrow(ax, 4.8, 1.3, 5.3, 2.4)
    
    draw_arrow(ax, 7.4, 2.8, 7.7, 2.8)
    
    save_fig(fig, path, "Diagram 13: Runtime Orchestration")

def render_diagram_14(path):
    fig, ax = setup_ax()
    ax.text(0.5, 0.95, "Figure 14: Directed Graph Disruption Propagation", transform=ax.transAxes, fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    G = nx.DiGraph()
    nodes = ["SUP-006\n(Infected / Anomaly Seed)", "SUP-007", "SUP-010", "SUP-012", "SUP-013\n(Compromised Downstream)"]
    G.add_nodes_from(nodes)
    edges = [
        ("SUP-006\n(Infected / Anomaly Seed)", "SUP-007"),
        ("SUP-006\n(Infected / Anomaly Seed)", "SUP-010"),
        ("SUP-007", "SUP-012"),
        ("SUP-010", "SUP-012"),
        ("SUP-012", "SUP-013\n(Compromised Downstream)")
    ]
    G.add_edges_from(edges)
    
    pos = {
        "SUP-006\n(Infected / Anomaly Seed)": (0, 0),
        "SUP-007": (2, 1.5),
        "SUP-010": (2, -1.5),
        "SUP-012": (4, 0),
        "SUP-013\n(Compromised Downstream)": (6, 0)
    }
    
    node_colors = [C_DANGER, C_SECONDARY, C_SECONDARY, C_HIGHLIGHT, C_PRIMARY]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1500, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color=C_TEXT_LIGHT, font_size=6, font_weight='bold')
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=edges, edge_color=C_HIGHLIGHT, width=1.5, arrowsize=15)
    
    # Legend
    rect_red = mpatches.Patch(color=C_DANGER, label='Seed Anomaly (Risk=1.0)')
    rect_yellow = mpatches.Patch(color=C_HIGHLIGHT, label='Propagated Outflow (Risk=0.3)')
    ax.legend(handles=[rect_red, rect_yellow], loc='upper left')
    
    save_fig(fig, path, "Diagram 14: Risk Propagation")

def render_diagram_15(path):
    fig, ax = setup_ax()
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.text(5, 5.7, "Figure 15: TTR / TTS Concept and Resilience Gap", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    # Plot horizontal timelines
    ax.plot([1, 8], [4, 4], color=C_SECONDARY, linewidth=5, label='Time to Survive (TTS)')
    ax.plot([1, 5], [2.5, 2.5], color=C_ACCENT, linewidth=5, label='Time to Recover (TTR)')
    
    # Disruption line (catastrophe point)
    ax.axvline(x=5, color=C_DANGER, linestyle='--', linewidth=1.5)
    ax.text(5.1, 4.8, "TTR Endpoint (Recovery Completed)", color=C_ACCENT, fontsize=8, fontweight='bold')
    
    ax.axvline(x=8, color=C_PRIMARY, linestyle='--', linewidth=1.5)
    ax.text(8.1, 4.8, "TTS Endpoint (Catastrophic Limit)", color=C_PRIMARY, fontsize=8, fontweight='bold')
    
    # Draw bracket for Resilience Gap
    # Gap exists if TTR > TTS. Let's draw that scenario below
    ax.plot([1, 4], [1, 1], color=C_SECONDARY, linewidth=5, label='TTS (Scenario B)')
    ax.plot([1, 7], [0.5, 0.5], color=C_DANGER, linewidth=5, label='TTR (Scenario B)')
    ax.axvline(x=4, color=C_SECONDARY, linestyle=':', linewidth=1.5)
    ax.axvline(x=7, color=C_DANGER, linestyle=':', linewidth=1.5)
    
    # Highlight Gap
    ax.fill_between([4, 7], 0.2, 0.8, color=C_HIGHLIGHT, alpha=0.3, label='Resilience Gap (Disruption)')
    ax.text(5.5, 0.6, "Resilience Gap\n(TTR > TTS)", color=C_DANGER, fontsize=8, fontweight='bold', ha='center')
    
    ax.text(0.5, 4, "Scenario A\n(Resilient)", fontsize=8, fontweight='bold', ha='left')
    ax.text(0.5, 1, "Scenario B\n(Vulnerable)", fontsize=8, fontweight='bold', ha='left')
    
    save_fig(fig, path, "Diagram 15: TTR/TTS Concept")

def render_diagram_16(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 16: Decision Engine Multi-Perspective Threshold Flowchart", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Fused Case Risk\n(R_final)", 3.8, 4.8, 2.4, 0.8, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    draw_box(ax, "Low Threat\n(R < 0.35)", 0.6, 3.4, 1.8, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Medium Threat\n(0.35 <= R < 0.65)", 2.7, 3.4, 2.2, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "High Threat\n(0.65 <= R < 0.85)", 5.2, 3.4, 2.2, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "Critical Threat\n(R >= 0.85)", 7.8, 3.4, 1.8, 0.8, C_DANGER, text_color=C_TEXT_LIGHT, font_size=8, font_weight='bold')
    
    # Decisions
    draw_box(ax, "Mitigation Action\nMONITOR_ONLY", 0.6, 1.8, 1.8, 0.8, C_BG, font_size=8)
    draw_box(ax, "Mitigation Action\nDIVERSIFY_SOURCING", 2.7, 1.8, 2.2, 0.8, C_BG, font_size=8)
    draw_box(ax, "Mitigation Action\nPROCESS_ISOLATION", 5.2, 1.8, 2.2, 0.8, C_BG, font_size=8)
    draw_box(ax, "Mitigation Action\nREROUTE_SUPPLIER\n(Immediate Escalation)", 7.8, 1.8, 1.8, 0.8, C_HIGHLIGHT, font_size=7.5, font_weight='bold')
    
    # Connect
    draw_arrow(ax, 5.0, 4.8, 1.5, 4.2)
    draw_arrow(ax, 5.0, 4.8, 3.8, 4.2)
    draw_arrow(ax, 5.0, 4.8, 6.3, 4.2)
    draw_arrow(ax, 5.0, 4.8, 8.7, 4.2)
    
    draw_arrow(ax, 1.5, 3.4, 1.5, 2.6)
    draw_arrow(ax, 3.8, 3.4, 3.8, 2.6)
    draw_arrow(ax, 6.3, 3.4, 6.3, 2.6)
    draw_arrow(ax, 8.7, 3.4, 8.7, 2.6)
    
    save_fig(fig, path, "Diagram 16: Decision Engine")

def render_diagram_17(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 17: Final Artifact Export Architecture", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "Intermediate Build Zone\n(data/intermediate/ & data/processed/)", 0.2, 2.2, 2.4, 1.2, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Export Operation
    draw_box(ax, "Pipeline Shutil Copy\n(Validates file integrity & maps to outputs/)", 3.8, 2.2, 2.4, 1.2, C_ACCENT, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Final destinations
    draw_box(ax, "outputs/final_intelligence/\nscadex_final_intelligence.csv", 7.4, 4.3, 2.4, 0.7, C_HIGHLIGHT, font_size=8)
    draw_box(ax, "outputs/resilience/\nresilience_intelligence.csv", 7.4, 3.3, 2.4, 0.7, C_HIGHLIGHT, font_size=8)
    draw_box(ax, "outputs/explanations/\nscadex_explanations.csv", 7.4, 2.3, 2.4, 0.7, C_HIGHLIGHT, font_size=8)
    draw_box(ax, "outputs/benchmark/\nbenchmark_summary.csv", 7.4, 1.3, 2.4, 0.7, C_HIGHLIGHT, font_size=8)
    
    # Connect
    draw_arrow(ax, 2.6, 2.8, 3.7, 2.8)
    draw_arrow(ax, 6.2, 2.8, 7.3, 4.65)
    draw_arrow(ax, 6.2, 2.8, 7.3, 3.65)
    draw_arrow(ax, 6.2, 2.8, 7.3, 2.65)
    draw_arrow(ax, 6.2, 2.8, 7.3, 1.65)
    
    save_fig(fig, path, "Diagram 17: Artifact Export")

def render_diagram_18(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 18: Component Interaction Model", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    # Classes
    draw_box(ax, "SCADEXUnifiedPipeline", 0.2, 4.4, 2.0, 0.8, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "SchemaNormalizer", 2.6, 4.4, 1.8, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "ResilienceEngine", 4.8, 4.4, 1.8, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "IntelligenceFusionEngine", 7.0, 4.4, 2.8, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Lifelines
    ax.plot([1.2, 1.2], [0.5, 4.4], color=C_MUTED, linestyle='--')
    ax.plot([3.5, 3.5], [0.5, 4.4], color=C_MUTED, linestyle='--')
    ax.plot([5.7, 5.7], [0.5, 4.4], color=C_MUTED, linestyle='--')
    ax.plot([8.4, 8.4], [0.5, 4.4], color=C_MUTED, linestyle='--')
    
    # Interactions
    draw_arrow(ax, 1.2, 3.8, 3.5, 3.8, "1. normalize()")
    draw_arrow(ax, 3.5, 3.4, 1.2, 3.4, "unified CSV")
    
    draw_arrow(ax, 1.2, 2.6, 5.7, 2.6, "2. compute_resilience()")
    draw_arrow(ax, 5.7, 2.2, 1.2, 2.2, "resilience CSV")
    
    draw_arrow(ax, 1.2, 1.4, 8.4, 1.4, "3. execute_fusion()")
    draw_arrow(ax, 8.4, 1.0, 1.2, 1.0, "final CSV")
    
    save_fig(fig, path, "Diagram 18: Component Interaction")

def render_diagram_19(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 19: Call Hierarchy Flow", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    draw_box(ax, "main() in main.py", 3.8, 4.8, 2.4, 0.8, C_PRIMARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    draw_box(ax, "SCADEXUnifiedPipeline.execute()", 3.8, 3.6, 2.4, 0.8, C_SECONDARY, text_color=C_TEXT_LIGHT, font_weight='bold')
    
    # Level 3 calls
    draw_box(ax, "ASTRARunner.execute()", 0.5, 2.0, 2.0, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "SCADERunner.execute()", 2.7, 2.0, 2.0, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "ResilienceEngine.compute_resilience()", 5.0, 2.0, 2.2, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    draw_box(ax, "FusionEngine.execute_fusion()", 7.5, 2.0, 2.0, 0.8, C_ACCENT, text_color=C_TEXT_LIGHT, font_size=8)
    
    # Connect
    draw_arrow(ax, 5.0, 4.8, 5.0, 4.4)
    draw_arrow(ax, 5.0, 3.6, 1.5, 2.8)
    draw_arrow(ax, 5.0, 3.6, 3.7, 2.8)
    draw_arrow(ax, 5.0, 3.6, 6.1, 2.8)
    draw_arrow(ax, 5.0, 3.6, 8.5, 2.8)
    
    save_fig(fig, path, "Diagram 19: Call Hierarchy")

def render_diagram_20(path):
    fig, ax = setup_ax()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(5, 5.7, "Figure 20: End-to-End Execution Lifecycle Stages", fontsize=11, fontweight='bold', ha='center', color=C_PRIMARY)
    
    # 5 core stages
    stages = [
        "STAGE 1: INGESTION\n(Extract CSV events)",
        "STAGE 2: ANALYSIS\n(ASTRA & SCADE)",
        "STAGE 3: NORMALISATION\n(Join dataset schemas)",
        "STAGE 4: KINETIC MATH\n(TTR/TTS & Fusion)",
        "STAGE 5: EXPORT\n(XAI MD & word manual)"
    ]
    
    for i, s in enumerate(stages):
        x = 0.2 + i * 1.95
        draw_box(ax, s, x, 2.2, 1.7, 0.8, C_PRIMARY if i == 4 else C_SECONDARY, text_color=C_TEXT_LIGHT, font_size=7.5, font_weight='bold')
        if i < 4:
            draw_arrow(ax, x + 1.7, 2.6, x + 1.95, 2.6)
            
    save_fig(fig, path, "Diagram 20: Execution Lifecycle")

# ==========================================
# MASTER RUNNER
# ==========================================

def main():
    print("Initializing SCADE-X Diagram Generator...")
    base_dir = Path(__file__).resolve().parent
    fig_dir = base_dir / "outputs" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    render_diagram_1(fig_dir / "diagram_1.png")
    render_diagram_2(fig_dir / "diagram_2.png")
    render_diagram_3(fig_dir / "diagram_3.png")
    render_diagram_4(fig_dir / "diagram_4.png")
    render_diagram_5(fig_dir / "diagram_5.png")
    render_diagram_6(fig_dir / "diagram_6.png")
    render_diagram_7(fig_dir / "diagram_7.png")
    render_diagram_8(fig_dir / "diagram_8.png")
    render_diagram_9(fig_dir / "diagram_9.png")
    render_diagram_10(fig_dir / "diagram_10.png")
    render_diagram_11(fig_dir / "diagram_11.png")
    render_diagram_12(fig_dir / "diagram_12.png")
    render_diagram_13(fig_dir / "diagram_13.png")
    render_diagram_14(fig_dir / "diagram_14.png")
    render_diagram_15(fig_dir / "diagram_15.png")
    render_diagram_16(fig_dir / "diagram_16.png")
    render_diagram_17(fig_dir / "diagram_17.png")
    render_diagram_18(fig_dir / "diagram_18.png")
    render_diagram_19(fig_dir / "diagram_19.png")
    render_diagram_20(fig_dir / "diagram_20.png")
    
    print("All 20 SCADE-X diagrams successfully generated!")

if __name__ == "__main__":
    main()

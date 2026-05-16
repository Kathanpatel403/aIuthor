import sys
from pathlib import Path

# Add backend to path so we can import helpers
sys.path.append(str(Path.cwd() / "backend"))

import html
from xhtml2pdf import pisa
from aiuthor.prompts import (
    planner_prompts, researcher_prompts, writer_prompts, 
    humanizer_prompts, editor_prompts, fact_checker_prompts, 
    memory_keeper_prompts, assembler_prompts
)
from aiuthor.tonality.presets import TONALITY_PRESETS

def generate_dossier_pdf():
    prompts = {
        "Planner Agent": planner_prompts.PLANNER_SYSTEM,
        "Researcher Agent": researcher_prompts.RESEARCHER_SYSTEM if hasattr(researcher_prompts, 'RESEARCHER_SYSTEM') else "Dynamic RAG retrieval logic.",
        "Writer Agent": writer_prompts.WRITER_SYSTEM_PREFIX,
        "Humanizer Agent": humanizer_prompts.HUMANIZER_SYSTEM,
        "Editor Agent": editor_prompts.EDITOR_SYSTEM,
        "Fact Checker Agent": fact_checker_prompts.FACT_CHECKER_SYSTEM if hasattr(fact_checker_prompts, 'FACT_CHECKER_SYSTEM') else "Verification logic.",
        "Memory Keeper Agent": memory_keeper_prompts.MEMORY_KEEPER_SYSTEM,
    }

    css = """
        @page { size: letter; margin: 2cm; }
        body { font-family: Helvetica, Arial, sans-serif; line-height: 1.4; color: #333; }
        h1 { color: #4F46E5; font-size: 24pt; border-bottom: 2px solid #4F46E5; padding-bottom: 10pt; }
        h2 { color: #111; font-size: 18pt; margin-top: 20pt; border-left: 4px solid #4F46E5; padding-left: 10pt; }
        pre { background-color: #f4f4f9; padding: 10pt; border: 1px solid #ddd; white-space: pre-wrap; font-size: 9pt; color: #444; }
        .tonality { margin-bottom: 15pt; padding: 10pt; background: #EEF2FF; border-radius: 8pt; }
        .label { font-weight: bold; color: #4F46E5; }
    """

    html_content = f"""
    <html>
    <head><style>{css}</style></head>
    <body>
        <h1>AIuthor: Multi-Agent Prompt Dossier</h1>
        <p>This document contains the core system prompts and tonality configurations used by the AIuthor multi-agent book engine.</p>
    """

    # Add Agent Prompts
    for agent, prompt in prompts.items():
        html_content += f"<h2>{agent}</h2><pre>{html.escape(prompt)}</pre>"

    # Add Tonality Presets
    html_content += "<h1>Tonality Preset Library</h1>"
    for tone_id, config in TONALITY_PRESETS.items():
        html_content += f"""
        <div class="tonality">
            <p><span class="label">Preset:</span> {config['label']}</p>
            <p><span class="label">Vocabulary:</span> {config['vocabulary']}</p>
            <p><span class="label">Rhythm:</span> {config['rhythm_notes']}</p>
            <p><span class="label">Hook:</span> {config['hook_style']}</p>
        </div>
        """

    html_content += "</body></html>"

    output_path = Path.cwd() / "AIuthor_Prompt_Dossier.pdf"
    with open(output_path, "wb") as f:
        pisa.CreatePDF(html_content, dest=f)
    
    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    generate_dossier_pdf()

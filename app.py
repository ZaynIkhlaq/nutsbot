"""NUSTBot - NUST Admissions Assistant."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
import config
from core.pipeline import Pipeline

pipeline = Pipeline()

CSS = """
body {
    background: #191919 !important;
    font-family: ui-sans-serif, -apple-system, system-ui, sans-serif !important;
    margin: 0 !important;
}
.gradio-container {
    background: #212121 !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 5vw !important;
    min-height: 100vh !important;
}
footer, .built-with, .show-api { display: none !important; }

/* Chatbot */
#chatbot {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    max-width: 100% !important;
    width: 100% !important;
}
#chatbot .message-wrap, #chatbot .messages-wrapper {
    max-width: 100% !important;
}
.avatar-container { display: none !important; }
/* User: dark pill */
.user-row .message, .user .message {
    background: #303030 !important;
    border: none !important;
    border-radius: 20px !important;
    color: #e8e8e8 !important;
}
/* Bot: transparent */
.bot-row .message, .bot .message {
    background: transparent !important;
    border: none !important;
    color: #d1d1d1 !important;
}

/* Input bar */
#input-row {
    background: #2f2f2f !important;
    border: 1px solid #424242 !important;
    border-radius: 28px !important;
    padding: 6px 6px 6px 12px !important;
    margin: 12px 0 !important;
    align-items: center !important;
    display: flex !important;
}
#input-row:focus-within { border-color: #555 !important; }
#msg textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #e8e8e8 !important;
    font-size: 15px !important;
    padding: 10px 12px !important;
    resize: none !important;
    border-radius: 20px !important;
}
#msg textarea::placeholder { color: #888 !important; }
#send {
    background: #C5A356 !important;
    border: none !important;
    border-radius: 50% !important;
    width: 38px !important; height: 38px !important;
    min-width: 38px !important; max-width: 38px !important;
    min-height: 38px !important;
    color: #000 !important;
    font-size: 18px !important; font-weight: 700 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
    line-height: 1 !important;
    margin: 0 2px 0 0 !important;
}
#send:hover { background: #d4b366 !important; }

/* Status bar: timer + confidence */
#status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 12px;
    min-height: 28px;
}
#status-bar .pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 12px;
    border-radius: 100px;
    letter-spacing: 0.3px;
}
#status-bar .time-instant { background: #1a3a2a; color: #4ade80; }
#status-bar .time-fast    { background: #1a2a3a; color: #60a5fa; }
#status-bar .time-normal  { background: #2a2a2a; color: #999; }
#status-bar .conf-high    { background: #1a3a2a; color: #4ade80; }
#status-bar .conf-med     { background: #3a2f1a; color: #fbbf24; }
#status-bar .conf-low     { background: #3a1a1a; color: #f87171; }
#disclaimer {
    text-align: center;
    font-size: 11px;
    color: #555;
    padding: 4px 0 14px 0;
}

/* Info panel - top right corner */
#info-panel {
    position: fixed;
    top: 12px;
    right: 16px;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 8px;
}
#info-toggle {
    background: #2a2a2a;
    border: 1px solid #333;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    color: #888;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}
#info-toggle:hover { color: #C5A356; border-color: #C5A356; }
#info-card {
    display: none;
    background: #1e1e1e;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 16px 20px;
    min-width: 280px;
    max-width: 340px;
    color: #ccc;
    font-size: 12px;
    line-height: 1.6;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
#info-card.open { display: block; }
#info-card h3 {
    color: #C5A356;
    font-size: 13px;
    margin: 0 0 8px 0;
    font-weight: 600;
    letter-spacing: 0.5px;
}
#info-card .spec {
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    border-bottom: 1px solid #2a2a2a;
}
#info-card .spec:last-child { border-bottom: none; }
#info-card .spec .label { color: #888; }
#info-card .spec .value { color: #ddd; font-weight: 500; }
#info-card .section { margin-top: 10px; }
#info-card .tag {
    display: inline-block;
    background: #2a2a2a;
    color: #aaa;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    margin: 2px 2px;
}

/* Title - top left */
#title-bar {
    position: fixed;
    top: 14px;
    left: 20px;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 8px;
}
#title-bar .logo {
    width: 26px;
    height: 26px;
    background: #003366;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #C5A356;
    font-weight: 700;
    font-size: 13px;
    font-family: Georgia, serif;
}
#title-bar .name {
    color: #999;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: -0.3px;
}
"""


def _extract_content(msg):
    """Extract string content from a Gradio message (handles str or list)."""
    c = msg.get("content", "")
    if isinstance(c, list):
        # Gradio 6 multimodal: content can be a list of parts
        return " ".join(str(p) for p in c if isinstance(p, str))
    return str(c) if c else ""


CONF_LABELS = {
    "high": ("Verified", "conf-high"),
    "medium": ("Partial match", "conf-med"),
    "low": ("Low confidence", "conf-low"),
}


def _status_html(elapsed: float, confidence: str, from_cache: bool) -> str:
    # Timer pill
    if from_cache:
        time_pill = '<span class="pill time-instant">instant</span>'
    elif elapsed < 2:
        time_pill = f'<span class="pill time-fast">{elapsed:.1f}s</span>'
    else:
        time_pill = f'<span class="pill time-normal">{elapsed:.1f}s</span>'

    # Confidence pill
    label, cls = CONF_LABELS.get(confidence, CONF_LABELS["low"])
    conf_pill = f'<span class="pill {cls}">{label}</span>'

    return f'<div style="display:flex;justify-content:space-between;align-items:center;">{conf_pill}{time_pill}</div>'


def respond(message, history):
    import time

    if not message or not message.strip():
        return history or [], "", ""

    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})

    chat_history = []
    for msg in history[:-2]:
        role = msg.get("role", "")
        content = _extract_content(msg)
        if role in ("user", "assistant") and content:
            chat_history.append({"role": role, "content": content})

    t0 = time.time()

    for _, r in pipeline.query_stream(message, history=chat_history):
        elapsed = time.time() - t0
        history[-1]["content"] = r.answer
        status = _status_html(elapsed, r.confidence, r.from_cache)
        if r.from_cache:
            yield history, "", status
            return
        yield history, "", status


def build():
    with gr.Blocks(title="NUSTBot") as app:

        # Title bar - top left
        gr.HTML(
            '<div id="title-bar">'
            '  <div class="logo">N</div>'
            '  <span class="name">nutsbot</span>'
            '</div>'
        )

        # Info panel - top right
        gr.HTML("""
        <div id="info-panel">
            <div id="info-card">
                <h3>COMPETITION SPECS</h3>
                <div class="spec"><span class="label">Event</span><span class="value">NUST Local Chatbot Competition 2026</span></div>
                <div class="spec"><span class="label">Director</span><span class="value">Dr. Sohail Iqbal</span></div>
                <div class="spec"><span class="label">Demo</span><span class="value">March 31, 2026</span></div>

                <div class="section"><h3>HARDWARE CONSTRAINTS</h3></div>
                <div class="spec"><span class="label">RAM</span><span class="value">8 GB max</span></div>
                <div class="spec"><span class="label">CPU</span><span class="value">Core i5 13th Gen</span></div>
                <div class="spec"><span class="label">GPU</span><span class="value">None</span></div>
                <div class="spec"><span class="label">Internet</span><span class="value">Offline only</span></div>

                <div class="section"><h3>THIS BOT</h3></div>
                <div class="spec"><span class="label">LLM</span><span class="value">Qwen 2.5 1.5B (Q4)</span></div>
                <div class="spec"><span class="label">RAM used</span><span class="value">~2.6 GB</span></div>
                <div class="spec"><span class="label">Data</span><span class="value">nust.edu.pk/faqs</span></div>
                <div class="spec"><span class="label">Chunks</span><span class="value">73 FAQs indexed</span></div>

                <div class="section" style="margin-top:10px;">
                    <span class="tag">FAISS</span>
                    <span class="tag">ONNX</span>
                    <span class="tag">llama.cpp</span>
                    <span class="tag">Gradio</span>
                    <span class="tag">RAG</span>
                    <span class="tag">CPU-only</span>
                </div>
            </div>
            <div id="info-toggle" onclick="document.getElementById('info-card').classList.toggle('open')">i</div>
        </div>
        """)

        chatbot = gr.Chatbot(
            elem_id="chatbot",
            show_label=False,
            height="75vh",
        )

        with gr.Row(elem_id="input-row"):
            msg = gr.Textbox(
                elem_id="msg",
                placeholder="Ask anything...",
                show_label=False,
                container=False,
                scale=9,
                lines=1,
                max_lines=4,
            )
            send = gr.Button("↑", elem_id="send", scale=0, min_width=36)

        status = gr.HTML(value="", elem_id="status-bar")
        gr.HTML('<div id="disclaimer">NUSTBot can make mistakes. Source: nust.edu.pk/faqs</div>')

        msg.submit(respond, [msg, chatbot], [chatbot, msg, status])
        send.click(respond, [msg, chatbot], [chatbot, msg, status])

    return app


if __name__ == "__main__":
    print("Initializing NUSTBot...")
    pipeline.load_all()
    app = build()
    app.launch(server_name="127.0.0.1", server_port=7860, share=False, show_error=True, css=CSS)

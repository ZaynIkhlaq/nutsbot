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

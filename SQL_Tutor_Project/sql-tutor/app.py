"""
SQL Tutor — Gradio Application

Run:
    1. python ingest.py        (first time, or after changing the knowledge base)
    2. python app.py
"""

import gradio as gr
from dotenv import load_dotenv

from answer import answer_question

load_dotenv(override=True)

#  Example starter questions shown beneath the chat 
EXAMPLES = [
    "What is the difference between INNER JOIN and LEFT JOIN?",
    "How do window functions differ from GROUP BY?",
    "When should I use a CTE instead of a subquery?",
    "What does ACID mean in SQL transactions?",
    "How do I find the top 3 earners per department?",
    "What is a covering index and when should I use one?",
    "How does HAVING differ from WHERE?",
    "Can you explain the SQL query execution order?",
]


def format_retrieved_context(docs) -> str:
    """Render retrieved chunks as HTML for display in the side panel."""
    if not docs:
        return "<p><em>No context retrieved.</em></p>"

    html = "<h3 style='color:#2563eb; margin-top:0'>Retrieved Context</h3>\n"
    for i, doc in enumerate(docs, 1):
        category = doc.metadata.get("category", "unknown")
        source = doc.metadata.get("source", "")
        filename = source.split("/")[-1] if source else "—"

        html += f"""
<details {'open' if i == 1 else ''}>
  <summary style='cursor:pointer; font-weight:600; color:#1e40af; padding:4px 0'>
    [{i}] {filename} <span style='color:#6b7280; font-weight:400'>({category})</span>
  </summary>
  <pre style='background:#f1f5f9; padding:10px; border-radius:6px;
              font-size:0.82em; white-space:pre-wrap; margin:4px 0 12px 0'>{doc.page_content}</pre>
</details>"""
    return html


def chat(history: list[dict]):
    """Called after the user message is appended to history."""
    last_message = history[-1]["content"]
    prior = history[:-1]

    answer, docs = answer_question(last_message, prior)
    history.append({"role": "assistant", "content": answer})
    return history, format_retrieved_context(docs)


def submit_message(message: str, history: list[dict]):
    """Append user message, clear the text box, trigger chat."""
    return "", history + [{"role": "user", "content": message}]


def main():
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        font=["Inter", "ui-sans-serif", "system-ui"],
    )

    with gr.Blocks(
        title="SQL Tutor",
        theme=theme,
        css="""
        #header { text-align: center; padding: 16px 0 8px 0; }
        #header h1 { font-size: 1.8rem; font-weight: 700; color: #1e3a8a; margin: 0; }
        #header p  { color: #475569; margin: 4px 0 0 0; font-size: 0.95rem; }
        .context-panel { border-left: 3px solid #bfdbfe; padding-left: 12px; }
        """,
    ) as ui:

        #  Header
        gr.HTML("""
        <div id="header">
          <h1>SQL Tutor</h1>
          <p>Ask anything about SQL — from basics to advanced topics</p>
        </div>
        """)

        with gr.Row():
            #  Left column: chat 
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=520,
                    type="messages",
                    show_copy_button=True,
                    avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=sql"),
                    render_markdown=True,
                    bubble_full_width=False,
                )

                with gr.Row():
                    message_box = gr.Textbox(
                        placeholder="Ask a SQL question, e.g. 'How do I use GROUP BY with HAVING?'",
                        show_label=False,
                        scale=5,
                        lines=1,
                        submit_btn=True,
                    )

                gr.Examples(
                    examples=EXAMPLES,
                    inputs=message_box,
                    label="Example questions — click to load",
                    examples_per_page=4,
                )

            #  Right column: retrieved context 
            with gr.Column(scale=2, elem_classes="context-panel"):
                context_display = gr.HTML(
                    value="<p style='color:#94a3b8; font-style:italic'>"
                          "Retrieved knowledge-base excerpts will appear here "
                          "after your first question.</p>",
                    label="Retrieved Context",
                )

        #  Event wiring 
        # 1. Append user message and clear text box
        # 2. Call the RAG pipeline and update chat + context panel
        submit_event = message_box.submit(
            fn=submit_message,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot],
        )
        submit_event.then(
            fn=chat,
            inputs=chatbot,
            outputs=[chatbot, context_display],
        )

    ui.launch(inbrowser=True, share=True)


if __name__ == "__main__":
    main()

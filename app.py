import gradio as gr
from resume_ai_mvp import generate_resumes

iface = gr.Interface(
    fn=generate_resumes,
    inputs=[
        gr.Textbox(lines=10, label="Resume Points (one per line)"),
        gr.Textbox(lines=5, label="Job Description")
    ],
    outputs=[
        gr.Textbox(label="Relevant Skills"),
        gr.Textbox(label="Professional Resume"),
        gr.Textbox(label="Achievement-Oriented Resume"),
        gr.Textbox(label="Creative Resume")
    ],
    title="AI Resume Generator MVP",
    description="Generate tailored resumes based on your experience and job description. The OpenAI API key should be set in the environment variables."
)

if __name__ == "__main__":
    iface.launch()
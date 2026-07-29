import gradio as gr
from gradio_pdf import PDF

with gr.Blocks() as demo:
    PDF(label="test")

demo.launch()
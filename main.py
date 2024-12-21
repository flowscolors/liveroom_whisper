import gradio as gr
from live_assistant import live_assistant_interface
from danmu_capture import danmu_capture_interface
from connect_analysis import connect_analysis_interface

with gr.Blocks() as app:
    live_assistant_interface()
    danmu_capture_interface()
    connect_analysis_interface()

app.launch()
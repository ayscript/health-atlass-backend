import gradio as gr
import requests
import soundfile as sf
import numpy as np
import tempfile
import os



ASR_URL = "asr space url"
LLM_URL = "llm space url"
TTS_URL =  "tts space url"



def call_asr(audio_path):
    payload = {
        "data": [audio_path]
    }
    r = requests.post(ASR_URL, json=payload, timeout=120)
    return r.json()["data"][0]


def call_llm(text):
    payload = {
        "data": [text]
    }
    r = requests.post(LLM_URL, json=payload, timeout=120)
    return r.json()["data"][0]


def call_tts(text, language):
    payload = {
        "data": [text, language]
    }
    r = requests.post(TTS_URL, json=payload, timeout=120)
    return r.json()["data"][0]





def healthatlas_pipeline(
    mode,
    text_input,
    audio_input,
    tts_language
):
    if mode == "Text":
        if not text_input.strip():
            return "Please enter text", None

        llm_response = call_llm(text_input)

        audio_path = call_tts(llm_response, tts_language)
        return llm_response, audio_path

    else:  # Audio mode
        if audio_input is None:
            return "Please upload audio", None

        # Save uploaded audio
        sr, audio = audio_input
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, audio, sr)
            audio_path = f.name

        transcription = call_asr(audio_path)
        llm_response = call_llm(transcription)
        audio_out = call_tts(llm_response, tts_language)

        return llm_response, audio_out



#gradio user interface
with gr.Blocks(title="HealthAtlas AI") as demo:
    gr.Markdown(
        """
        # 🏥 HealthAtlas  
        Multilingual AI Health Triage Assistant  
        **Languages:** English · Yoruba · Hausa · Igbo
        """
    )

    mode = gr.Radio(
        ["Text", "Audio"],
        value="Text",
        label="Input Mode"
    )

    text_input = gr.Textbox(
        label="Text Input",
        visible=True
    )

    audio_input = gr.Audio(
        label="Audio Input",
        type="numpy",
        visible=False
    )

    tts_language = gr.Dropdown(
        choices=["yoruba", "hausa"],
        value="yoruba",
        label="Speech Output Language"
    )

    output_text = gr.Textbox(
        label="HealthAtlas Response"
    )

    output_audio = gr.Audio(
        label="Spoken Response"
    )

    submit = gr.Button("Submit")

    def toggle_inputs(m):
        return (
            gr.update(visible=m == "Text"),
            gr.update(visible=m == "Audio")
        )

    mode.change(
        toggle_inputs,
        inputs=mode,
        outputs=[text_input, audio_input]
    )

    submit.click(
        healthatlas_pipeline,
        inputs=[mode, text_input, audio_input, tts_language],
        outputs=[output_text, output_audio]
    )

if __name__ == "__main__":
    demo.launch()
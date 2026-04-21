import warnings
warnings.filterwarnings("ignore")

import gradio as gr
from transformers import pipeline
from langdetect import detect, LangDetectException
import torch


# 1. SUPPORTED LANGUAGE PAIRS

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "zh": "Chinese",
}

# Durham College model map: (source_lang, target_lang) → HuggingFace model name
MODEL_MAP = {
    ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("it", "en"): "Helsinki-NLP/opus-mt-it-en",
    ("en", "it"): "Helsinki-NLP/opus-mt-en-it",
    ("pt", "en"): "Helsinki-NLP/opus-mt-roa-en",
    ("en", "pt"): "Helsinki-NLP/opus-mt-en-ROMANCE",
    ("nl", "en"): "Helsinki-NLP/opus-mt-nl-en",
    ("en", "nl"): "Helsinki-NLP/opus-mt-en-nl",
    ("ru", "en"): "Helsinki-NLP/opus-mt-ru-en",
    ("en", "ru"): "Helsinki-NLP/opus-mt-en-ru",
    ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
    ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
}

# Cache for loaded pipelines
_pipeline_cache = {}


# 2. CORE TRANSLATION FUNCTIONS

def detect_language(text: str) -> str:

    try:
        detected = detect(text.strip())
        # langdetect returns 'zh-cn' for Chinese — normalize to 'zh'
        if detected.startswith("zh"):
            return "zh"
        return detected
    except LangDetectException:
        return "en"


def get_pipeline(src_lang: str, tgt_lang: str):

    pair = (src_lang, tgt_lang)

    if pair in _pipeline_cache:
        return _pipeline_cache[pair]

    if pair not in MODEL_MAP:
        supported = [f"{s}→{t}" for s, t in MODEL_MAP.keys()]
        raise ValueError(
            f"Language pair '{src_lang}→{tgt_lang}' is not supported.\n"
            f"Supported pairs: {', '.join(supported)}"
        )

    model_name = MODEL_MAP[pair]
    task_name = f"translation_{src_lang}_to_{tgt_lang}"
    device = 0 if torch.cuda.is_available() else -1

    print(f"  Loading model: {model_name} ...")
    translator = pipeline(task_name, model=model_name, device=device)
    _pipeline_cache[pair] = translator
    print("  Model loaded Successfully")
    return translator


def translate(text: str, src_lang: str, tgt_lang: str) -> str:

    if not text or not text.strip():
        return " Please enter some text to translate."

    # Auto-detect source language
    if src_lang == "auto":
        src_lang = detect_language(text)
        print(f"  Auto-detected language: {src_lang}")

    # No translation needed if same language
    if src_lang == tgt_lang:
        return text

    try:
        translator = get_pipeline(src_lang, tgt_lang)
        result = translator(text.strip(), max_length=512)
        return result[0]["translation_text"]

    except ValueError as ve:
        return f" Error: {str(ve)}"
    except Exception as e:
        return f" Unexpected error: {str(e)}"


def translate_batch(sentences: list[str], src_lang: str, tgt_lang: str) -> list[str]:

    if src_lang == "auto":
        # Detect from first non-empty sentence
        sample = next((s for s in sentences if s.strip()), "")
        src_lang = detect_language(sample)

    try:
        translator = get_pipeline(src_lang, tgt_lang)
        results = translator(sentences, max_length=512)
        return [r["translation_text"] for r in results]
    except Exception as e:
        print(f"Batch translation error: {e}")
        return [""] * len(sentences)


# 3. GRADIO UI

def build_ui():

    # Dropdown choices — "auto" + all supported source languages
    src_choices = [(" Auto-Detect", "auto")] + [
        (f"{LANGUAGE_NAMES[lang]} ({lang.upper()})", lang)
        for lang in LANGUAGE_NAMES
    ]
    tgt_choices = [
        (f"{LANGUAGE_NAMES[lang]} ({lang.upper()})", lang)
        for lang in LANGUAGE_NAMES
    ]

    def gradio_translate(text, src_label, tgt_label):
        detected_info = ""
        src = src_label

        if src == "auto":
            detected = detect_language(text)
            src = detected
            lang_name = LANGUAGE_NAMES.get(detected, detected.upper())
            detected_info = f" Detected: **{lang_name}** ({detected.upper()})\n\n"

        translation = translate(text, src, tgt_label)
        return detected_info + translation

    with gr.Blocks(
        title="DC Language Translator",
        theme=gr.themes.Soft(primary_hue="blue"),
        css="""
            .title-box { text-align: center; margin-bottom: 10px; }
            .translate-btn { background: #2563eb !important; }
            footer { display: none !important; }
        """,
    ) as demo:
        

        gr.HTML("""
            <div class='title-box'>
                <h1>DC Language Translator</h1>
                <p style='color: #6b7280; font-size: 14px;'>
                    Powered by Helsinki-NLP
                </p>
            </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Source")
                src_dropdown = gr.Dropdown(
                    choices=src_choices,
                    value="auto",
                    label="Source Language",
                )
                input_text = gr.Textbox(
                    placeholder="Enter text to translate...",
                    lines=8,
                    label="Input Text",
                )

            with gr.Column(scale=1):
                gr.Markdown("### Translation")
                tgt_dropdown = gr.Dropdown(
                    choices=tgt_choices,
                    value="en",
                    label="Target Language",
                )
                output_text = gr.Textbox(
                    lines=8,
                    label="Translated Text",
                    interactive=False,
                )

        with gr.Row():
            clear_btn = gr.Button(" Clear", variant="secondary")
            translate_btn = gr.Button(" Translate", variant="primary", elem_classes=["translate-btn"])

        gr.Markdown("""
        ---
        **Supported Language Pairs:**  
        FR↔EN · French ↔ English  
        DE↔EN · German ↔ English  
        ES↔EN · Spanish ↔ English  
        IT↔EN · Italian ↔ English  
        PT↔EN · Portuguese ↔ English  
        NL↔EN · Dutch ↔ English  
        RU↔EN · Russian ↔ English  
        ZH↔EN . Chinese ↔ English  
        
        *(Models are downloaded on first use and cached locally)*  
        """)

        # Wire up buttons
        translate_btn.click(
            fn=gradio_translate,
            inputs=[input_text, src_dropdown, tgt_dropdown],
            outputs=output_text,
        )
        clear_btn.click(
            fn=lambda: ("", ""),
            outputs=[input_text, output_text],
        )
        input_text.submit(
            fn=gradio_translate,
            inputs=[input_text, src_dropdown, tgt_dropdown],
            outputs=output_text,
        )

    return demo


# 4. ENTRY POINT

if __name__ == "__main__":
    print("*" * 55)
    print(" DC Language Translator")
    print("*" * 55)
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        inbrowser=True,
    )

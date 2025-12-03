import subprocess
from pathlib import Path
import os

MODEL_TO_FILENAME = {
    "tiny": "ggml-tiny.bin",
    "tiny.en": "ggml-tiny.en.bin",
    "base": "ggml-base.bin",
    "base.en": "ggml-base.en.bin",
    "small": "ggml-small.bin",
    "small.en": "ggml-small.en.bin",
    "medium": "ggml-medium.bin",
    "medium.en": "ggml-medium.en.bin",
    "large": "ggml-large-v1.bin",
    "large-v2": "ggml-large-v2.bin",
    "large-v3": "ggml-large-v3.bin",
    "large-v3-turbo": "ggml-large-v3-turbo.bin",
}


class WhisperCppModel:
    def __init__(self, model: str):
        self.model = model

        if model not in MODEL_TO_FILENAME:
            raise ValueError(f"Model '{model}' is not supported in whisper.cpp adapter.")

    def transcribe(self, audio_path: str, language: str) -> dict[str, str]:
        model_path = None
        naming_options = ["MODEL_PATH", "MODELPATH", "MODEL_DIR", "MODELDIR"]
        for env_var in naming_options:
            model_path = os.getenv(env_var)
            if model_path:
                break
        if not model_path:
            raise EnvironmentError("Model path environment variable not set. Please set either 'MODEL_PATH' or 'MODELPATH'.")   


        whisper_options = [
            "--model",
            f"{model_path}/{MODEL_TO_FILENAME[self.model]}",
            "--language",
            language,
            "--output-file",
            "transcription",
            "--no-timestamps",
            "--output-txt",
        ]

        command = [
            "whisper-cli",
            *whisper_options,
            audio_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Whisper.cpp transcription failed: {result.stderr}")

        # The output text file will have the same name as the audio file but with .txt extension
        output_txt_path = Path("transcription.txt")
        with open(output_txt_path, "r") as f:
            transcription = f.read().strip()

        return {"text": transcription}
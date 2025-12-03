import asyncio
import json
import os
import time
import uuid
import warnings
from enum import Enum
from threading import Event
from typing import (
    Any,
    ByteString,
    Generator,
    Optional,
    Sequence,
    Tuple
)

from languages import (
    LANGUAGE_TO_CODE,
    Languages
)
import soundfile
from whisper_cpp_adapter import WhisperCppModel

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", message="Performing inference on CPU when CUDA is available")

NUM_THREADS = 1
os.environ["OMP_NUM_THREADS"] = str(NUM_THREADS)
os.environ["MKL_NUM_THREADS"] = str(NUM_THREADS)

SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2


class Engines(Enum):
    WHISPER_TINY = "WHISPER_TINY"
    WHISPER_BASE = "WHISPER_BASE"
    WHISPER_SMALL = "WHISPER_SMALL"
    WHISPER_MEDIUM = "WHISPER_MEDIUM"
    WHISPER_LARGE = "WHISPER_LARGE"
    WHISPER_LARGE_V2 = "WHISPER_LARGE_V2"
    WHISPER_LARGE_V3 = "WHISPER_LARGE_V3"
    WHISPER_LARGE_V3_TURBO = "WHISPER_LARGE_V3_TURBO"


class Engine(object):
    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def audio_sec(self) -> float:
        raise NotImplementedError()

    def process_sec(self) -> float:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x: Engines, language: Languages, **kwargs):
        if x is Engines.WHISPER_TINY:
            return WhisperTiny(language=language)
        elif x is Engines.WHISPER_BASE:
            return WhisperBase(language=language)
        elif x is Engines.WHISPER_SMALL:
            return WhisperSmall(language=language)
        elif x is Engines.WHISPER_MEDIUM:
            return WhisperMedium(language=language)
        elif x is Engines.WHISPER_LARGE:
            return WhisperLarge(language=language)
        elif x is Engines.WHISPER_LARGE_V2:
            return WhisperLargeV2(language=language)
        elif x is Engines.WHISPER_LARGE_V3:
            return WhisperLargeV3(language=language)
        elif x is Engines.WHISPER_LARGE_V3_TURBO:
            return WhisperLargeV3Turbo(language=language)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


class Whisper(Engine):
    LANGUAGE_TO_WHISPER_CODE = {
        Languages.EN: "en",
        Languages.DE: "de",
        Languages.ES: "es",
        Languages.FR: "fr",
        Languages.IT: "it",
        Languages.PT_PT: "pt",
        Languages.PT_BR: "pt",
    }

    def __init__(self, cache_extension: str, model: str, language: Languages):
        #self._model = whisper.load_model(model, device="cpu")
        self._model = WhisperCppModel(model=model)
        self._cache_extension = cache_extension
        self._language_code = self.LANGUAGE_TO_WHISPER_CODE[language]
        self._audio_sec = 0.0
        self._proc_sec = 0.0

    def transcribe(self, path: str) -> str:
        info = soundfile.info(path)
        assert info.samplerate == SAMPLE_RATE
        self._audio_sec += info.frames / info.samplerate

        cache_path = path.replace(".flac", self._cache_extension)
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return res

        start_sec = time.time()
        res = self._model.transcribe(path, language=self._language_code)["text"]
        self._proc_sec += time.time() - start_sec

        with open(cache_path, "w") as f:
            f.write(res)

        return res

    def audio_sec(self) -> float:
        return self._audio_sec

    def process_sec(self) -> float:
        return self._proc_sec

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        raise NotImplementedError()


class WhisperTiny(Whisper):
    def __init__(self, language: Languages):
        model = "tiny.en" if language == Languages.EN else "tiny"
        super().__init__(cache_extension=".wspt", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Tiny"


class WhisperBase(Whisper):
    def __init__(self, language: Languages):
        model = "base.en" if language == Languages.EN else "base"
        super().__init__(cache_extension=".wspb", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Base"


class WhisperSmall(Whisper):
    def __init__(self, language: Languages):
        model = "small.en" if language == Languages.EN else "small"
        super().__init__(cache_extension=".wsps", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Small"


class WhisperMedium(Whisper):
    def __init__(self, language: Languages):
        model = "medium.en" if language == Languages.EN else "medium"
        super().__init__(cache_extension=".wspm", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Medium"


class WhisperLarge(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl", model="large-v1", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v1"


class WhisperLargeV2(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl2", model="large-v2", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v2"


class WhisperLargeV3(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl3", model="large-v3", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v3"
    
class WhisperLargeV3Turbo(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl3t", model="large-v3-turbo", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v3-turbo"

__all__ = [
    "Engine",
    "Engines",
] 

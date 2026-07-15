import json
from pathlib import Path

import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder, preprocess_wav
from vosk import KaldiRecognizer, Model, SetLogLevel

SAMPLE_RATE = 16000
RECORD_SECONDS = 3
KNOWN_VOICES_DIR = Path(__file__).parent / "known_voices"
MODEL_DIR = Path(__file__).parent / "vosk-model-small-ru-0.22"

# отредактируйте под свою фразу
PASSPHRASE = "открой ворота"
SPEAKER_THRESHOLD = 0.75  # cosine similarity; выше = строже

SetLogLevel(-1)  # приглушить подробные логи vosk


def record_clip() -> np.ndarray:
    print(f"Говорите ({RECORD_SECONDS} сек)...")
    audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    return audio.flatten()


def transcribe(audio_int16: np.ndarray, model: Model) -> str:
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.AcceptWaveform(audio_int16.tobytes())
    result = json.loads(rec.FinalResult())
    return result.get("text", "")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def build_known_embeddings(encoder: VoiceEncoder) -> dict[str, list[np.ndarray]]:
    known = {}
    if not KNOWN_VOICES_DIR.exists():
        return known

    for person_dir in KNOWN_VOICES_DIR.iterdir():
        if not person_dir.is_dir():
            continue
        embeddings = []
        for wav_path in person_dir.glob("*.wav"):
            wav = preprocess_wav(str(wav_path))
            embeddings.append(encoder.embed_utterance(wav))
        if embeddings:
            known[person_dir.name] = embeddings
            print(f"{person_dir.name}: загружено {len(embeddings)} голосовых образцов")
    return known


def identify_speaker(embedding: np.ndarray, known: dict[str, list[np.ndarray]]) -> tuple[str, float]:
    best_name, best_score = "Unknown", 0.0
    for name, ref_embeddings in known.items():
        score = max(cosine_similarity(embedding, ref) for ref in ref_embeddings)
        if score > best_score:
            best_name, best_score = name, score
    if best_score < SPEAKER_THRESHOLD:
        return "Unknown", best_score
    return best_name, best_score


def main():
    print("Загружаю модели (Vosk + Resemblyzer)...")
    stt_model = Model(str(MODEL_DIR))
    encoder = VoiceEncoder()

    known = build_known_embeddings(encoder)
    if not known:
        print(f"В {KNOWN_VOICES_DIR} нет записей — сначала запустите enroll_voice.py <имя>")

    print(f"\nПароль-фраза: '{PASSPHRASE}' (поменяйте в коде под себя)")
    print("Enter - записать и проверить, 'q' + Enter - выход\n")

    while True:
        cmd = input("> ")
        if cmd.strip().lower() == "q":
            break

        audio = record_clip()

        text = transcribe(audio, stt_model)
        phrase_ok = PASSPHRASE.lower() in text.lower()

        wav_float = preprocess_wav(audio.astype(np.float32) / 32768.0, source_sr=SAMPLE_RATE)
        embedding = encoder.embed_utterance(wav_float)
        name, score = identify_speaker(embedding, known)

        print(f"Распознано: '{text}'")
        print(f"Фраза совпала: {phrase_ok}")
        print(f"Голос: {name} (сходство {score:.2f})")

        if phrase_ok and name != "Unknown":
            print(f"=== ДОСТУП РАЗРЕШЁН: {name} ===\n")
        else:
            print("=== ДОСТУП ЗАПРЕЩЁН ===\n")


if __name__ == "__main__":
    main()

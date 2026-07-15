import argparse
from pathlib import Path

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
RECORD_SECONDS = 3
KNOWN_VOICES_DIR = Path(__file__).parent / "known_voices"


def record_clip() -> "np.ndarray":
    print(f"Говорите сейчас ({RECORD_SECONDS} сек)...")
    audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    return audio


def main():
    parser = argparse.ArgumentParser(description="Записать голосовые образцы для базы")
    parser.add_argument("name", help="имя человека, используется как имя папки")
    parser.add_argument("--clips", type=int, default=5, help="сколько записей сделать")
    args = parser.parse_args()

    person_dir = KNOWN_VOICES_DIR / args.name
    person_dir.mkdir(parents=True, exist_ok=True)

    print(f"Запись голоса для '{args.name}'. Каждый раз проговаривайте вашу фразу-пароль полностью.")
    for i in range(args.clips):
        input(f"[{i + 1}/{args.clips}] Нажмите Enter и говорите...")
        audio = record_clip()
        filename = person_dir / f"clip_{i + 1}.wav"
        sf.write(str(filename), audio, SAMPLE_RATE, subtype="PCM_16")
        print(f"Сохранено: {filename}")

    print(f"Готово, {args.clips} записей сохранено в {person_dir}")


if __name__ == "__main__":
    main()

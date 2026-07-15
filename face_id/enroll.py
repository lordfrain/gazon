import argparse
import time
from pathlib import Path

import cv2

KNOWN_FACES_DIR = Path(__file__).parent / "known_faces"


def main():
    parser = argparse.ArgumentParser(description="Capture reference photos for a person's face DB entry")
    parser.add_argument("name", help="person's name, used as folder name")
    args = parser.parse_args()

    person_dir = KNOWN_FACES_DIR / args.name
    person_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Не удалось открыть веб-камеру (индекс 0)")

    print("Окно камеры открыто. 's' - сохранить кадр, 'q' - выход. Сделайте 5-8 снимков с разных ракурсов.")
    saved = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Не удалось прочитать кадр с камеры")
            break

        display = frame.copy()
        cv2.putText(display, f"{args.name}: saved {saved} | s=save q=quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("enroll", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            filename = person_dir / f"{int(time.time() * 1000)}.jpg"
            cv2.imwrite(str(filename), frame)
            saved += 1
            print(f"Сохранено: {filename}")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Готово, сохранено {saved} фото в {person_dir}")


if __name__ == "__main__":
    main()

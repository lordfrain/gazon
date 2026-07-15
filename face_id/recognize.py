from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

KNOWN_FACES_DIR = Path(__file__).parent / "known_faces"
MATCH_THRESHOLD = 0.5  # cosine similarity; higher = stricter match


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def build_known_embeddings(app: FaceAnalysis) -> dict[str, list[np.ndarray]]:
    known = {}
    if not KNOWN_FACES_DIR.exists():
        return known

    for person_dir in KNOWN_FACES_DIR.iterdir():
        if not person_dir.is_dir():
            continue
        embeddings = []
        for img_path in person_dir.glob("*.jpg"):
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            faces = app.get(img)
            if not faces:
                print(f"Лицо не найдено на {img_path}, пропускаю")
                continue
            embeddings.append(faces[0].embedding)
        if embeddings:
            known[person_dir.name] = embeddings
            print(f"{person_dir.name}: загружено {len(embeddings)} эталонных снимков")
    return known


def identify(embedding: np.ndarray, known: dict[str, list[np.ndarray]]) -> tuple[str, float]:
    best_name, best_score = "Unknown", 0.0
    for name, ref_embeddings in known.items():
        score = max(cosine_similarity(embedding, ref) for ref in ref_embeddings)
        if score > best_score:
            best_name, best_score = name, score
    if best_score < MATCH_THRESHOLD:
        return "Unknown", best_score
    return best_name, best_score


def main():
    print("Загружаю модель InsightFace (первый запуск скачает веса, может занять пару минут)...")
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))

    known = build_known_embeddings(app)
    if not known:
        print(f"В {KNOWN_FACES_DIR} нет фото — сначала запустите enroll.py <имя>")

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise RuntimeError("Не удалось открыть веб-камеру (индекс 0)")

    print("'q' - выход")
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        faces = app.get(frame)
        for face in faces:
            name, score = identify(face.embedding, known)
            x1, y1, x2, y2 = face.bbox.astype(int)
            color = (0, 200, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{name} ({score:.2f})", (x1, max(y1 - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("recognize", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

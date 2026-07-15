import cv2

BACKENDS = [(cv2.CAP_DSHOW, "DSHOW"), (cv2.CAP_MSMF, "MSMF")]

for index in range(4):
    for backend, name in BACKENDS:
        cap = cv2.VideoCapture(index, backend)
        if not cap.isOpened():
            print(f"[{index}][{name}] не открылась")
            cap.release()
            continue

        ok, frame = cap.read()
        if not ok or frame is None:
            print(f"[{index}][{name}] открылась, но кадр не прочитан")
        else:
            print(f"[{index}][{name}] OK, размер {frame.shape}, средняя яркость {frame.mean():.1f} (0 = чёрный кадр)")
        cap.release()

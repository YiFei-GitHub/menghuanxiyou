import cv2
import numpy as np
from ultralytics import YOLO


def detect_video(video_path, model_path, output_path):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 调整分辨率与训练时一致
        frame_resized = cv2.resize(frame, (640, 640))
        results = model(frame_resized, conf=0.7, iou=0.8)

        # 绘制检测结果并还原到原分辨率
        annotated_frame = results[0].plot()
        annotated_frame = cv2.resize(annotated_frame, (width, height))

        out.write(annotated_frame)
        cv2.imshow("Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


# 运行检测
detect_video("mp4/2.mp4", "runs/detect/menghuan_train_v2/weights/best.pt", "2_detection.mp4")
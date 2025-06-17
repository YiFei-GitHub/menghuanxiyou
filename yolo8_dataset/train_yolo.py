import torch  # 新增这一行
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')  # 也可以使用yolov8s.pt, yolov8m.pt等

# 训练模型
results = model.train(
    data='../yolo8_dataset/menghuan_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=8,
    device='cuda' if torch.cuda.is_available() else 'cpu',
    name='screen_detection'
)

# 导出最佳模型
model.export(format='pt')
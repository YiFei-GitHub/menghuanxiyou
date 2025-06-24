from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8s.pt')  # 使用YOLOv8s提升检测能力

# 训练模型
model.train(
    data='menghuan_dataset.yaml',  # 数据集配置文件
    device=0,                    # 使用GPU 0（单GPU） pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    epochs=100,                  # 延长训练轮次
    batch=8,                     # 批量大小
    imgsz=640,                   # 图像尺寸
    augment=True,                # 启用数据增强
    multi_scale=True,            # 多尺度训练
    lr0=0.001,                   # 初始学习率
    name='menghuan_train_v2'      # 训练任务名称

)
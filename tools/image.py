import time
import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple, List, Dict
import ctypes
from ultralytics import YOLO  # 需要安装ultralytics包
import torch
import os


class image:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+

    """
    功能：根据输入的图片名称，查找其在屏幕上的位置
    :param template_path: 模板图片路径
    :param threshold: 匹配阈值(0-1)
    """

    def __init__(self, template_path: str, threshold: float = 0.8):
        self.template_path = "../images/" + template_path
        self.threshold = threshold
        self.template = self._load_template()

    """
        加载模板图片
    """

    def _load_template(self) -> np.ndarray:
        try:
            template = cv2.imread(self.template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise FileNotFoundError(f"模板图片未找到: {self.template_path}")
            return template
        except Exception as e:
            raise RuntimeError(f"加载模板失败: {str(e)}")

    """
        查找图片位置
        :return: (x,y)图片左上角坐标，None表示未找到
    """

    def find_image_position(self) -> Optional[Tuple[int, int]]:
        screen = self.capture_screen()
        result = cv2.matchTemplate(screen, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        return max_loc if max_val >= self.threshold else None

    """
        截取屏幕区域
        :param region: (x1, y1, x2, y2)截图区域，None表示全屏
        :return: OpenCV图像格式(numpy数组)
    """

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        screenshot = pyautogui.screenshot(region=region)
        screen_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screen_bgr


class YOLOImageFinder:
    """
    使用YOLOv8模型在屏幕上查找目标对象

    参数:
    model_path: YOLO模型路径 (可以是预训练模型或自定义模型)
    conf_threshold: 置信度阈值 (0-1)
    device: 使用的设备 ('cuda' 或 'cpu')
    """

    def __init__(self, model_path: str = "yolov8n.pt",
                 conf_threshold: float = 0.5,
                 device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.conf_threshold = conf_threshold
        self.device = device
        self.model = self._load_model(model_path)
        self.class_names = self.model.names if hasattr(self.model, 'names') else {}

    def _load_model(self, model_path: str) -> YOLO:
        """加载YOLO模型，如果本地不存在则自动下载"""
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            print(f"⚠️ 模型文件不存在，将下载预训练模型: {model_path}")
            try:
                # 尝试下载模型
                model = YOLO(model_path)
                model.export(format="pt")  # 确保模型保存到本地
                return model
            except Exception as e:
                raise RuntimeError(f"无法下载模型: {str(e)}")
        return YOLO(model_path).to(self.device)

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """捕获屏幕区域"""
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_targets(self, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        在屏幕上查找目标对象

        返回:
        List of detections, 每个检测结果包含:
            'class_name': 类别名称
            'confidence': 置信度
            'position': (x, y, width, height) 边界框位置
            'center': (cx, cy) 边界框中心坐标
        """
        # 捕获屏幕
        screen = self.capture_screen(region)

        # 使用YOLO进行推理
        results = self.model(screen, conf=self.conf_threshold, verbose=False)

        detections = []
        for result in results:
            # 处理每个检测结果
            for box in result.boxes:
                # 获取边界框坐标 (xyxy格式)
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                # 计算中心点
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # 获取类别ID和名称
                cls_id = int(box.cls)
                class_name = self.class_names.get(cls_id, f"class_{cls_id}")

                # 获取置信度
                conf = float(box.conf)

                detections.append({
                    'class_name': class_name,
                    'confidence': conf,
                    'position': (x1, y1, x2 - x1, y2 - y1),  # (x, y, width, height)
                    'center': (cx, cy)
                })

        return detections

    def find_specific_target(self, target_class: str,
                             region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        查找特定类别的目标并返回中心坐标

        参数:
        target_class: 要查找的目标类别名称

        返回:
        目标中心坐标 (x, y) 或 None (如果未找到)
        """
        detections = self.find_targets(region)

        # 查找指定类别的目标
        for detection in detections:
            if detection['class_name'] == target_class:
                return detection['center']

        return None


if __name__ == "__main__":
    # 保留您原有的测试代码
    time.sleep(1)

    # # 使用原有的image类
    # print("===== 使用传统图像匹配 =====")
    # ImageMatcher = image("taskTracking.png")
    # position = ImageMatcher.find_image_position()  # 查找任务栏坐标
    # if position:
    #     x, y = position
    #     region = (max(0, x - 5), max(0, y - 5), 230, 300)
    #     screen = ImageMatcher.capture_screen(region=region)  # 返回任务栏截图
    #     print(f"目标位置: {position}, 截图区域: {region}")
    # else:
    #     print("未找到目标")

    # 使用YOLOv8进行目标检测
    print("\n===== 使用YOLOv8目标检测 =====")

    # 初始化YOLO查找器 - 使用您训练好的模型
    # 注意：将"your_trained_model.pt"替换为您实际训练好的模型路径
    yolo_finder = YOLOImageFinder(model_path="your_trained_model.pt", conf_threshold=0.7)

    # 查找特定目标 (例如 'taskbar_icon')
    target_position = yolo_finder.find_specific_target("taskbar_icon")

    if target_position:
        x, y = target_position
        print(f"✅ 找到目标位置: ({x}, {y})")

        # 围绕目标位置截图
        region = (max(0, x - 100), max(0, y - 50), 200, 100)
        screen = yolo_finder.capture_screen(region=region)

        # 保存截图
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"yolo_target_{timestamp}.png"
        cv2.imwrite(filename, screen)
        print(f"💾 截图已保存为: {filename}")
    else:
        print("❌ 未找到目标")
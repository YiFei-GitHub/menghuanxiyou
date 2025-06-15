import time

import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple
import ctypes


class image:

    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+


    """
    功能：根据输入的图片名称，查找其在屏幕上的位置
    :param template_path: 模板图片路径
    :param threshold: 匹配阈值(0-1)
    """
    def __init__(self, template_path: str, threshold: float = 0.8):
        self.template_path = "../images/"+template_path
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

        # 显示截图，并确保窗口在可见区域
        # cv2.namedWindow("Screen Capture")
        # cv2.moveWindow("Screen Capture", 100, 100)  # 强制窗口位置
        # cv2.imshow("Screen Capture", screen_bgr)
        # cv2.waitKey(3000)  # 显示3秒
        # cv2.destroyAllWindows()
        #
        # # 保存截图到本地文件
        # timestamp = time.strftime("%Y%m%d_%H%M%S")  # 生成时间戳作为文件名
        # filename = f"screenshot_{timestamp}.png"
        # cv2.imwrite(filename, screen_bgr)
        # print(f"截图已保存为: {filename}")


        return screen_bgr



if __name__ == "__main__":

    time.sleep(1)

    ImageMatcher = image("taskTracking.png")
    position = ImageMatcher.find_image_position()#查找任务栏坐标
    if position:
        x, y = position
        # 围绕目标位置截图（例如：目标左上角向左扩展 100 像素，向上扩展 50 像素）
        region = (
            max(0, x - 5),  # 防止 x-100 越界（小于 0）
            max(0, y - 5),  # 防止 y-50 越界
            230,  # 截图宽度
            300  # 截图高度
        )
        screen = ImageMatcher.capture_screen(region=region)#返回任务栏截图
        print(f"目标位置: {position}, 截图区域: {region}")
    else:
        print("未找到目标")

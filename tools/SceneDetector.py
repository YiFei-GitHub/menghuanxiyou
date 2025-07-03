import cv2
import numpy as np
import pyautogui
import time
import os
import json
from datetime import datetime
from GameWindowUtils import GameWindowUtils  # 导入窗口工具类


class SceneDetector:

    def __init__(self, template_dir="../images/game_templates", debug_dir="debug_screenshots"):
        self.game_hwnd = None
        self.game_rect = None
        self.templates = {}
        self.template_dir = template_dir
        self.debug_dir = debug_dir
        self.current_scene = "未知"
        self.last_match_info = {}
        self.last_print_time = 0
        self.print_interval = 0.5  # 控制台打印间隔（秒）

        # 创建目录
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.debug_dir, exist_ok=True)

        # 加载模板
        self.load_templates()
        self.print_log(f"场景检测器初始化完成，已加载 {len(self.templates)} 个模板")

    def load_templates(self):
        """加载场景模板"""
        try:
            # 遍历模板目录中的所有文件
            for filename in os.listdir(self.template_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # 从文件名获取场景名称（去掉扩展名）
                    scene_name = os.path.splitext(filename)[0]
                    template_path = os.path.join(self.template_dir, filename)

                    # 读取模板图像
                    template = cv2.imread(template_path)
                    if template is not None:
                        self.templates[scene_name] = template
                        self.print_log(f"加载模板: {scene_name} (尺寸: {template.shape[1]}x{template.shape[0]})")

            if not self.templates:
                self.print_log("未找到任何模板图片！请将场景图片放入 'game_templates' 目录", "warning")
        except Exception as e:
            self.print_log(f"加载模板时出错: {str(e)}", "error")


    def print_log(self, message, level="info"):
        """打印带时间戳的日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "warning":
            print(f"[{timestamp}] ⚠️ {message}")
        elif level == "error":
            print(f"[{timestamp}] ❌ {message}")
        else:
            print(f"[{timestamp}] ℹ️ {message}")

    def find_game_window(self):
        """查找游戏窗口 - 使用 GameWindowUtils"""
        try:
            # 使用工具类查找游戏窗口
            hwnd, title = GameWindowUtils.find_game_window()

            if hwnd:
                self.game_hwnd = hwnd

                # 使用工具类获取窗口位置
                rect_info = GameWindowUtils.get_window_rect(hwnd)
                if rect_info:
                    self.game_rect = (
                        rect_info["left"],
                        rect_info["top"],
                        rect_info["width"],
                        rect_info["height"]
                    )
                    self.print_log(f"找到游戏窗口: {title}，窗口位置: {self.game_rect}")
                    return True
                else:
                    self.print_log("获取窗口位置失败", "warning")
                    return False
            else:
                self.print_log("未找到游戏窗口", "warning")
                return False
        except Exception as e:
            self.print_log(f"查找游戏窗口时出错: {str(e)}", "error")
            return False

    def capture_game_screen(self):
        """捕获游戏窗口截图"""
        try:
            if not self.game_rect:
                self.print_log("未设置游戏窗口位置", "warning")
                return None

            # 截取游戏窗口区域
            x, y, width, height = self.game_rect
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        except Exception as e:
            self.print_log(f"捕获屏幕时出错: {str(e)}", "error")
            return None

    def detect_scene(self, screen):
        """检测当前场景（修改版：只要包含模板就算匹配成功）"""
        self.last_match_info = {"scene": "未知", "confidence": 0.0, "details": []}

        if screen is None:
            self.print_log("无法获取屏幕截图", "warning")
            return "未知", 0.0

        if not self.templates:
            self.print_log("没有可用的模板", "warning")
            return "未知", 0.0

        best_match = {"name": "未知", "score": 0}
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        # 遍历所有模板
        for scene_name, template in self.templates.items():
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            h, w = gray_template.shape

            # 模板匹配
            res = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)

            # 寻找所有匹配度超过阈值的区域
            threshold = 0.7  # 降低阈值，允许部分匹配
            locations = np.where(res >= threshold)

            # 计算匹配区域的数量和覆盖面积
            match_count = len(locations[0])
            match_area = match_count * (w * h) / (gray_screen.shape[0] * gray_screen.shape[1])

            # 记录匹配详情
            match_detail = {
                "scene": scene_name,
                "match_count": match_count,
                "match_area": match_area,
                "max_confidence": np.max(res) if match_count > 0 else 0
            }
            self.last_match_info["details"].append(match_detail)

            # 更新最佳匹配（改为基于匹配区域数量和面积）
            score = match_count * match_area  # 综合评分
            if score > best_match["score"]:
                best_match = {"name": scene_name, "score": score, "confidence": match_detail["max_confidence"]}

        # 设置当前场景
        self.last_match_info["scene"] = best_match["name"]
        self.last_match_info["confidence"] = best_match["confidence"]

        # 判断匹配是否成功（只要有匹配区域就算成功）
        if best_match["score"] > 0 and best_match["confidence"] > 0.5:
            self.current_scene = best_match["name"]
        else:
            self.current_scene = "未知"

        return self.current_scene, best_match["confidence"]



    def detect_continuously(self, interval=1):
        """持续检测场景"""
        if not self.find_game_window():
            self.print_log("未找到游戏窗口，请确保梦幻西游已启动", "error")
            return

        self.print_log("开始场景检测，按Ctrl+C停止...")

        try:
            while True:
                current_time = time.time()
                screen = self.capture_game_screen()

                # 等待按键输入后关闭窗口
                #cv2.imshow("游戏截图预览", screen)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                #self.print_log("按任意键关闭预览窗口")

                scene, confidence = self.detect_scene(screen)

                # 控制打印频率
                if current_time - self.last_print_time > self.print_interval:
                    # 显示当前场景
                    self.print_log(f"当前场景: {scene} (置信度: {confidence:.2f})")

                    # 如果置信度低，显示详细信息
                    if confidence < 0.5:
                        self.print_log("低置信度检测结果，请检查模板匹配情况", "warning")
                        for detail in self.last_match_info["details"]:
                            self.print_log(f"  - {detail['scene']}: {detail['confidence']:.2f}")

                    self.last_print_time = current_time

                time.sleep(interval)

        except KeyboardInterrupt:
            self.print_log("检测停止")
        except Exception as e:
            self.print_log(f"检测过程中出错: {str(e)}", "error")

    def run(self):

        while True:
            """主运行函数"""
            print("梦幻西游场景检测")
            self.detect_continuously(1)




if __name__ == "__main__":
    print("正在启动场景检测器...")
    detector = SceneDetector()
    detector.run()

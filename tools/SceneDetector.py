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
        self.debug_mode = False
        self.last_print_time = 0
        self.print_interval = 0.5  # 控制台打印间隔（秒）

        # 创建目录
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.debug_dir, exist_ok=True)

        # 加载模板
        self.load_templates()
        self.print_log(f"场景检测器初始化完成，已加载 {len(self.templates)} 个模板")

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
                    self.print_log(f"找到游戏窗口: {title}")
                    self.print_log(f"窗口位置: {self.game_rect}")
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

    def add_template(self, template_path, scene_name=None):
        """添加新模板"""
        try:
            if not scene_name:
                # 从文件名获取场景名称
                scene_name = os.path.splitext(os.path.basename(template_path))[0]

            # 读取模板图像
            template = cv2.imread(template_path)
            if template is None:
                self.print_log(f"无法读取模板图片: {template_path}", "error")
                return False

            # 保存到模板目录
            save_path = os.path.join(self.template_dir, f"{scene_name}.png")
            cv2.imwrite(save_path, template)

            # 添加到模板字典
            self.templates[scene_name] = template
            self.print_log(f"已添加模板: {scene_name} (尺寸: {template.shape[1]}x{template.shape[0]})")
            return True
        except Exception as e:
            self.print_log(f"添加模板时出错: {str(e)}", "error")
            return False

    def detect_scene(self, screen):
        """检测当前场景"""
        self.last_match_info = {"scene": "未知", "confidence": 0.0, "details": []}

        if screen is None:
            self.print_log("无法获取屏幕截图", "warning")
            return "未知", 0.0

        if not self.templates:
            self.print_log("没有可用的模板", "warning")
            return "未知", 0.0

        best_match = {"name": "未知", "score": 0}

        # 转换为灰度图
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        # 检查每个模板
        for scene_name, template in self.templates.items():
            # 转换为灰度图
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # 获取模板尺寸
            h, w = gray_template.shape

            # 如果模板比屏幕大，调整模板大小
            if h > gray_screen.shape[0] or w > gray_screen.shape[1]:
                scale = min(gray_screen.shape[0] / h, gray_screen.shape[1] / w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                gray_template = cv2.resize(gray_template, (new_w, new_h))
                self.print_log(f"调整模板大小: {scene_name} -> {new_w}x{new_h}", "debug")

            # 模板匹配
            res = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # 记录匹配详情
            match_detail = {
                "scene": scene_name,
                "confidence": max_val,
                "template_size": (w, h),
                "match_location": max_loc
            }
            self.last_match_info["details"].append(match_detail)

            # 更新最佳匹配
            if max_val > best_match["score"]:
                best_match = {"name": scene_name, "score": max_val}

        # 设置当前场景
        self.last_match_info["scene"] = best_match["name"]
        self.last_match_info["confidence"] = best_match["score"]

        if best_match["score"] > 0.7:
            self.current_scene = best_match["name"]

        # 调试模式：保存匹配结果
        if self.debug_mode:
            self.save_debug_info(screen, best_match)

        return self.current_scene, best_match["score"]

    def save_debug_info(self, screen, best_match):
        """保存调试信息"""
        try:
            # 保存当前屏幕截图
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen_path = os.path.join(self.debug_dir, f"screen_{timestamp}.png")
            cv2.imwrite(screen_path, screen)

            # 保存匹配详情
            debug_info = {
                "timestamp": timestamp,
                "detected_scene": best_match["name"],
                "confidence": best_match["score"],
                "all_matches": self.last_match_info["details"]
            }

            # 保存JSON文件
            json_path = os.path.join(self.debug_dir, f"debug_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, ensure_ascii=False, indent=2)

            self.print_log(f"调试信息已保存: {screen_path}, {json_path}")
        except Exception as e:
            self.print_log(f"保存调试信息时出错: {str(e)}", "error")

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

    def analyze_problem(self):
        """分析检测问题"""
        print("\n" + "=" * 40)
        print("问题分析")
        print("=" * 40)

        # 1. 检查游戏窗口
        if not self.game_rect:
            print("❌ 问题: 未找到游戏窗口")
            print("💡 解决方案: 确保游戏已启动且窗口可见")
            return

        # 2. 检查模板
        if not self.templates:
            print("❌ 问题: 没有加载任何模板")
            print("💡 解决方案: 使用 '添加模板' 功能添加场景图片")
            return

        # 3. 捕获测试截图
        screen = self.capture_game_screen()
        if screen is None:
            print("❌ 问题: 无法捕获游戏画面")
            print("💡 解决方案: 检查游戏窗口是否最小化或被遮挡")
            return

        # 保存测试截图
        test_path = os.path.join(self.debug_dir, "test_screen.png")
        cv2.imwrite(test_path, screen)
        print(f"📷 当前游戏画面已保存: {test_path}")

        # 4. 显示模板信息
        print("\n📁 已加载模板列表:")
        for scene_name, template in self.templates.items():
            # 检查模板尺寸是否合适
            screen_h, screen_w = screen.shape[:2]
            temp_h, temp_w = template.shape[:2]

            size_ok = "✅ 正常" if temp_h <= screen_h and temp_w <= screen_w else "⚠️ 可能过大"

            print(f"  - {scene_name}: {temp_w}x{temp_h} ({size_ok})")

        # 5. 建议
        print("\n💡 建议:")
        print("1. 检查模板图片是否与当前游戏画面一致")
        print("2. 确保模板尺寸小于游戏窗口")
        print("3. 尝试添加更多不同角度的模板")
        print("4. 使用 '调试模式' 获取详细匹配信息")

    def run(self):
        """主运行函数"""
        print("\n" + "=" * 40)
        print("梦幻西游场景检测工具")
        print("=" * 40)
        print("1. 持续检测场景")
        print("2. 添加新模板")
        print("3. 启用调试模式 (保存匹配详情)")
        print("4. 分析检测问题")
        print("5. 退出")

        try:
            choice = input("\n请选择操作: ")

            if choice == "1":
                interval = float(input("输入检测间隔(秒，默认1): ") or 1)
                self.detect_continuously(interval)
            elif choice == "2":
                template_path = input("输入模板图片路径: ")
                scene_name = input("输入场景名称(可选，默认为文件名): ") or None
                self.add_template(template_path, scene_name)
            elif choice == "3":
                self.debug_mode = True
                print("✅ 已启用调试模式，所有匹配详情将保存到 debug_screenshots 目录")
                input("按回车键返回...")
            elif choice == "4":
                self.analyze_problem()
                input("\n按回车键返回...")
            elif choice == "5":
                return
            else:
                print("⚠️ 无效选择")
        except KeyboardInterrupt:
            print("\n操作取消")
            return

        # 返回主菜单
        self.run()


if __name__ == "__main__":
    print("正在启动场景检测器...")
    detector = SceneDetector()
    detector.run()
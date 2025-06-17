import pyautogui
import time
import math
import cv2
import numpy as np
import pygetwindow as gw
import random
import win32gui
import win32ui
import win32con
from ultralytics import YOLO


class mouse:
    pyautogui.FAILSAFE = True

    # 类级配置参数
    CORRECTION_ENABLED = True  # 全局开关
    INITIAL_STEP_RATIO = 0.9  # 增大第一步移动比例
    MICRO_ADJUST_RATIO = 0.3  # 增大微调移动比例
    MAX_ATTEMPTS = 20  # 减少最大微调次数
    ERROR_THRESHOLD = 20  # 增大可接受误差阈值
    STEP_DELAY = 0.05  # 增加移动后等待时间
    MAX_JITTER = 5  # 最大随机抖动像素

    # 游戏窗口信息
    GAME_WINDOW = None
    CURSOR_TEMPLATE_PATH = '../images/game_cursor.png'
    last_position = None  # 上次成功获取的位置

    @classmethod
    def get_game_window(cls):
        """获取游戏窗口位置信息"""
        if cls.GAME_WINDOW is None:
            print("正在定位游戏窗口...")
            try:
                # 尝试查找游戏窗口（这里以"梦幻西游"为例）
                window = gw.getWindowsWithTitle("梦幻西游")[0]
                print(window)
                # 增加安全边距
                border_margin = 20
                cls.GAME_WINDOW = {
                    'left': window.left + border_margin,
                    'top': window.top + border_margin,
                    'width': window.width - border_margin * 2,
                    'height': window.height - border_margin * 2,
                    'right': window.left + window.width - border_margin,
                    'bottom': window.top + window.height - border_margin
                }
                print(f"游戏窗口位置(含边距): 左={cls.GAME_WINDOW['left']}, 上={cls.GAME_WINDOW['top']}, "
                      f"宽={cls.GAME_WINDOW['width']}, 高={cls.GAME_WINDOW['height']}")
            except IndexError:
                print("⚠️ 未找到游戏窗口! 使用全屏模式")
                screen_w, screen_h = pyautogui.size()
                border_margin = 20
                cls.GAME_WINDOW = {
                    'left': border_margin,
                    'top': border_margin,
                    'width': screen_w - border_margin * 2,
                    'height': screen_h - border_margin * 2,
                    'right': screen_w - border_margin,
                    'bottom': screen_h - border_margin
                }
        return cls.GAME_WINDOW

    @classmethod
    def get_window_screenshot(cls, hwnd):
        """获取指定窗口的截图"""
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        signedIntsArray = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (height, width, 4)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    @classmethod
    def get_game_cursor_position(cls, retry_count=3):
        """
        获取游戏内鼠标实际位置，增加重试机制
        返回: (x, y) 屏幕坐标
        """
        for attempt in range(retry_count):
            try:
                # 获取游戏窗口区域
                window = cls.get_game_window()
                region = (
                    window['left'],
                    window['top'],
                    window['width'],
                    window['height']
                )

                # 截取游戏窗口区域
                # print("截取游戏窗口区域...")
                screenshot = pyautogui.screenshot(region=region)
                screenshot_np = np.array(screenshot)
                screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

                # 加载游戏鼠标特征图
                # print(f"加载光标模板: {cls.CURSOR_TEMPLATE_PATH}")
                cursor_template = cv2.imread(cls.CURSOR_TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
                if cursor_template is None:
                    print(f"❌ 错误: 找不到光标图片 {cls.CURSOR_TEMPLATE_PATH}")
                    return pyautogui.position()  # 回退到系统位置

                # 模板匹配
                # print("执行模板匹配...")
                result = cv2.matchTemplate(
                    screenshot_gray,
                    cursor_template,
                    cv2.TM_CCOEFF_NORMED
                )

                # 获取最佳匹配位置
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                # print(f"模板匹配结果: 最大匹配度={max_val:.4f}")

                # 设置匹配阈值
                if max_val < 0.65:
                    print(f"⚠️ 警告: 匹配度低({max_val:.4f})，可能未找到光标")
                    continue  # 继续重试

                # 计算光标中心位置（相对游戏窗口）
                cursor_w, cursor_h = cursor_template.shape[::-1]
                game_x = max_loc[0] + cursor_w // 2
                game_y = max_loc[1] + cursor_h // 2

                # 转换为屏幕绝对坐标
                screen_x = window['left'] + game_x
                screen_y = window['top'] + game_y

                print(f"游戏内鼠标位置: X={screen_x}, Y={screen_y}")
                cls.last_position = (screen_x, screen_y)  # 更新最后成功位置
                return (screen_x, screen_y)

            except Exception as e:
                print(f"❌ 获取游戏鼠标位置时出错: {str(e)}")

        # 所有重试都失败后
        if cls.last_position:
            print(f"使用上次成功位置: {cls.last_position}")
            return cls.last_position
        else:
            print("回退到系统鼠标位置")
            return pyautogui.position()

    @classmethod
    def _clamp_to_window(cls, x, y):
        """确保坐标在游戏窗口范围内"""
        window = cls.get_game_window()
        clamped_x = max(window['left'], min(x, window['right'] - 1))
        clamped_y = max(window['top'], min(y, window['bottom'] - 1))
        return clamped_x, clamped_y

    @classmethod
    def _add_jitter(cls, x, y):
        """添加微小随机抖动，防止游戏检测"""
        jitter_x = random.randint(-cls.MAX_JITTER, cls.MAX_JITTER)
        jitter_y = random.randint(-cls.MAX_JITTER, cls.MAX_JITTER)
        return x + jitter_x, y + jitter_y

    @classmethod
    def move_to(cls, x, y, duration=0.3, correction=True):
        """
        带偏移修正的鼠标移动 - 优化版本
        Args:
            x, y: 目标坐标
            duration: 基础移动持续时间
            correction: 是否启用偏移修正
        """
        if not cls.CORRECTION_ENABLED or not correction:
            print(f"直接移动至: X={x}, Y={y}")
            clamped_x, clamped_y = cls._clamp_to_window(x, y)
            pyautogui.moveTo(clamped_x, clamped_y, duration=duration)
            return

        print("=" * 50)
        print(f"开始偏移修正移动: 目标位置 X={x}, Y={y}")

        # 第一步：获取当前位置并计算移动
        print("获取当前游戏鼠标位置...")
        current_x, current_y = cls.get_game_cursor_position()
        print(f"当前位置: X={current_x}, Y={current_y}")

        dx = x - current_x
        dy = y - current_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        print(f"初始距离: {distance:.2f}像素")

        # 计算第一步目标位置
        step1_x = current_x + dx * cls.INITIAL_STEP_RATIO
        step1_y = current_y + dy * cls.INITIAL_STEP_RATIO

        # 确保第一步位置在窗口内
        step1_x, step1_y = cls._clamp_to_window(step1_x, step1_y)
        print(f"第一步移动至: X={step1_x:.1f}, Y={step1_y:.1f} (移动{cls.INITIAL_STEP_RATIO * 100}%距离)")

        # 执行第一步移动（带随机抖动）
        target_x, target_y = cls._add_jitter(step1_x, step1_y)
        pyautogui.moveTo(target_x, target_y, duration=duration)
        time.sleep(cls.STEP_DELAY)
        print("第一步移动完成")

        # 第二步：迭代微调
        for attempt in range(1, cls.MAX_ATTEMPTS + 1):
            print(f"\n微调尝试 #{attempt}/{cls.MAX_ATTEMPTS}")

            # 获取当前游戏鼠标位置
            current_x, current_y = cls.get_game_cursor_position()
            print(f"当前位置: X={current_x}, Y={current_y}")

            dx = x - current_x
            dy = y - current_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            print(f"当前距离目标: {distance:.2f}像素")

            # 检查是否达到精度要求
            if distance <= cls.ERROR_THRESHOLD:
                print(f"✓ 达到精度要求! 最终误差: {distance:.2f}像素")
                return

            # 动态调整微调比例 - 距离越大移动比例越大
            dynamic_ratio = min(cls.MICRO_ADJUST_RATIO, max(0.1, distance / 500))

            # 计算微调步长
            step_x = dx * dynamic_ratio
            step_y = dy * dynamic_ratio
            print(f"微调移动: ΔX={step_x:.1f}, ΔY={step_y:.1f} (移动{dynamic_ratio * 100}%剩余距离)")

            # 微调移动
            adjust_duration = max(0.05, duration * 0.5)  # 更短的微调时间
            target_x = current_x + step_x
            target_y = current_y + step_y

            # 确保目标位置在窗口内
            target_x, target_y = cls._clamp_to_window(target_x, target_y)

            # 添加随机抖动
            target_x, target_y = cls._add_jitter(target_x, target_y)

            print(f"移动至: X={target_x:.1f}, Y={target_y:.1f}")
            pyautogui.moveTo(target_x, target_y, duration=adjust_duration)
            time.sleep(cls.STEP_DELAY)

        # 最终位置记录
        final_x, final_y = cls.get_game_cursor_position()
        final_error = math.sqrt((x - final_x) ** 2 + (y - final_y) ** 2)
        print(f"✗ 未达到理想精度! 最终误差: {final_error:.2f}像素")
        print("=" * 50)

    @classmethod
    def click(cls, button='left', clicks=1, interval=0.1):
        """执行鼠标点击，增加随机间隔"""
        print(f"点击鼠标: {button}键 x {clicks}")
        for _ in range(clicks):
            pyautogui.click(button=button)
            time.sleep(interval + random.uniform(0, 0.05))

    @classmethod
    def move_and_click(cls, x, y, button='left', clicks=1):
        """移动并点击（自动使用偏移修正）"""
        print(f"\n{'=' * 30} 移动并点击 {'=' * 30}")
        print(f"目标位置: X={x}, Y={y}")
        cls.move_to(x, y, correction=True)
        cls.click(button, clicks)
        print(f"{'=' * 30} 操作完成 {'=' * 30}\n")

    @classmethod
    def configure(cls, **kwargs):
        """动态配置偏移修正参数"""
        valid_params = [
            'INITIAL_STEP_RATIO', 'MICRO_ADJUST_RATIO',
            'MAX_ATTEMPTS', 'ERROR_THRESHOLD', 'STEP_DELAY'
        ]

        for key, value in kwargs.items():
            if key in valid_params and hasattr(cls, key):
                setattr(cls, key, value)
                print(f"⚙️ 参数更新: {key} = {value}")

    @classmethod
    def move_and_click_with_detection(cls, hwnd, model, target_class, confidence=0.4, offset_x=0, offset_y=0,
                                      click_type='left', success_image=None, loop_count=1, mouse_shape_image=None,
                                      click_error=3):
        """结合目标检测的移动和点击操作"""
        if hwnd is None:
            print("错误: 未获取到窗口句柄")
            return False

        window = cls.get_game_window()
        left = window['left']
        top = window['top']
        window_width = window['width']
        window_height = window['height']

        for _ in range(loop_count):
            # 截取窗口图像
            screenshot = cls.get_window_screenshot(hwnd)

            # 使用YOLO模型进行检测
            results = model(screenshot, conf=confidence)

            # 查找目标类别
            found = False
            for result in results:
                boxes = result.boxes.cpu().numpy()
                for box in boxes:
                    if int(box.cls[0]) == target_class:
                        # 获取检测框坐标
                        x1, y1, x2, y2 = box.xyxy[0].astype(int)

                        # 计算中心点并添加偏移
                        center_x = (x1 + x2) // 2 + offset_x
                        center_y = (y1 + y2) // 2 + offset_y

                        # 转换为屏幕坐标
                        screen_x = left + center_x
                        screen_y = top + center_y

                        # 移动并点击
                        print(f"找到目标类别 {target_class}, 移动到位置: ({screen_x}, {screen_y})")
                        cls.move_to(screen_x, screen_y)
                        cls.click(button=click_type)

                        # 检查点击后是否成功
                        if success_image:
                            time.sleep(0.5)  # 等待操作完成
                            post_screenshot = cls.get_window_screenshot(hwnd)
                            if cls._check_success(post_screenshot, success_image):
                                print("操作成功!")
                                return True
                            else:
                                print("操作未成功，继续尝试")
                        else:
                            print("操作完成")
                            return True

                        found = True
                        break

                if found:
                    break

            if not found:
                print(f"未找到目标类别 {target_class}")
                return False

        return False

    @classmethod
    def _check_success(cls, screenshot, success_image):
        """检查操作是否成功（基于图像匹配）"""
        # 这里应该实现图像匹配逻辑，检查screenshot中是否包含success_image
        # 简化实现，实际使用时需要完善
        return True


if __name__ == "__main__":
    print("鼠标控制器初始化...")
    time.sleep(1)

    # 加载 YOLO 模型
    model = YOLO('../images/best.pt')  # 请替换为实际的模型路径

    # 获取游戏窗口句柄
    try:
        hwnd = gw.getWindowsWithTitle("梦幻西游")[0]._hWnd
    except IndexError:
        print("⚠️ 未找到游戏窗口!")
        hwnd = None

    # 示例使用
    if hwnd:
        print("\n测试带检测的移动和点击操作...")
        target_class = 1  # 请替换为实际的目标类别
        mouse.move_and_click_with_detection(hwnd, model, target_class)

        # 动态调整参数
        print("\n调整参数...")
        mouse.configure(
            INITIAL_STEP_RATIO=0.8,
            ERROR_THRESHOLD=15,
            STEP_DELAY=0.1
        )
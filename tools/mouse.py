import pyautogui
import time
import logging
import math
import cv2
import numpy as np
import pygetwindow as gw


class mouse:
    pyautogui.FAILSAFE = True

    # 类级配置参数
    CORRECTION_ENABLED = True  # 全局开关
    INITIAL_STEP_RATIO = 0.85  # 第一步移动比例
    MICRO_ADJUST_RATIO = 0.4  # 微调移动比例
    MAX_ATTEMPTS = 5  # 最大微调次数
    ERROR_THRESHOLD = 3  # 可接受误差阈值(像素)
    STEP_DELAY = 0.15  # 移动后等待时间

    # 游戏窗口信息
    GAME_WINDOW = None
    CURSOR_TEMPLATE_PATH = 'game_cursor.png'

    @classmethod
    def get_game_window(cls):
        """获取游戏窗口位置信息"""
        if cls.GAME_WINDOW is None:
            print("正在定位游戏窗口...")
            try:
                # 尝试查找游戏窗口（这里以"梦幻西游"为例）
                window = gw.getWindowsWithTitle("梦幻西游")[0]
                cls.GAME_WINDOW = {
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height
                }
                print(f"游戏窗口位置: 左={window.left}, 上={window.top}, 宽={window.width}, 高={window.height}")
            except IndexError:
                print("⚠️ 未找到游戏窗口! 使用全屏模式")
                screen_w, screen_h = pyautogui.size()
                cls.GAME_WINDOW = {
                    'left': 0,
                    'top': 0,
                    'width': screen_w,
                    'height': screen_h
                }
        return cls.GAME_WINDOW

    @classmethod
    def get_game_cursor_position(cls):
        """
        获取游戏内鼠标实际位置
        返回: (x, y) 屏幕坐标
        """
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
            print("截取游戏窗口区域...")
            screenshot = pyautogui.screenshot(region=region)
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            # 加载游戏鼠标特征图
            print(f"加载光标模板: {cls.CURSOR_TEMPLATE_PATH}")
            cursor_template = cv2.imread(cls.CURSOR_TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
            if cursor_template is None:
                print(f"❌ 错误: 找不到光标图片 {cls.CURSOR_TEMPLATE_PATH}")
                return pyautogui.position()  # 回退到系统位置

            # 模板匹配
            print("执行模板匹配...")
            result = cv2.matchTemplate(
                screenshot_gray,
                cursor_template,
                cv2.TM_CCOEFF_NORMED
            )

            # 获取最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"模板匹配结果: 最大匹配度={max_val:.4f}")

            # 设置匹配阈值
            if max_val < 0.7:
                print(f"⚠️ 警告: 匹配度低({max_val:.4f})，可能未找到光标，使用系统位置")
                return pyautogui.position()  # 回退到系统位置

            # 计算光标中心位置（相对游戏窗口）
            cursor_w, cursor_h = cursor_template.shape[::-1]
            game_x = max_loc[0] + cursor_w // 2
            game_y = max_loc[1] + cursor_h // 2

            # 转换为屏幕绝对坐标
            screen_x = window['left'] + game_x
            screen_y = window['top'] + game_y

            print(f"游戏内鼠标位置: X={screen_x}, Y={screen_y}")
            return (screen_x, screen_y)

        except Exception as e:
            print(f"❌ 获取游戏鼠标位置时出错: {str(e)}")
            print("回退到系统鼠标位置")
            return pyautogui.position()

    @classmethod
    def capture_cursor_template(cls, save_path='game_cursor.png'):
        """捕获当前光标作为模板"""
        print("正在捕获光标模板...")
        # 获取当前鼠标位置
        x, y = pyautogui.position()

        # 定义光标捕获区域（以鼠标为中心）
        size = 30  # 捕获区域大小
        region = (x - size // 2, y - size // 2, size, size)

        # 截取光标区域
        cursor_img = pyautogui.screenshot(region=region)
        cursor_img.save(save_path)
        cls.CURSOR_TEMPLATE_PATH = save_path
        print(f"✓ 光标模板已保存至: {save_path}")
        return save_path

    @classmethod
    def move_to(cls, x, y, duration=0.3, correction=True):
        """
        带偏移修正的鼠标移动
        Args:
            x, y: 目标坐标
            duration: 基础移动持续时间
            correction: 是否启用偏移修正
        """
        if not cls.CORRECTION_ENABLED or not correction:
            print(f"直接移动至: X={x}, Y={y}")
            pyautogui.moveTo(x, y, duration=duration)
            return

        print("=" * 50)
        print(f"开始偏移修正移动: 目标位置 X={x}, Y={y}")

        # 第一步：获取当前位置并计算85%移动
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
        print(f"第一步移动至: X={step1_x:.1f}, Y={step1_y:.1f} (移动{cls.INITIAL_STEP_RATIO * 100}%距离)")

        # 执行第一步移动
        pyautogui.moveTo(step1_x, step1_y, duration=duration)
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

            # 计算微调步长
            step_x = dx * cls.MICRO_ADJUST_RATIO
            step_y = dy * cls.MICRO_ADJUST_RATIO
            print(f"微调移动: ΔX={step_x:.1f}, ΔY={step_y:.1f} (移动{cls.MICRO_ADJUST_RATIO * 100}%剩余距离)")

            # 微调移动
            adjust_duration = max(0.05, duration * 0.5)  # 更短的微调时间
            target_x = current_x + step_x
            target_y = current_y + step_y
            print(f"移动至: X={target_x:.1f}, Y={target_y:.1f}")
            pyautogui.moveTo(target_x, target_y, duration=adjust_duration)
            time.sleep(cls.STEP_DELAY)

        # 最终位置记录
        final_x, final_y = cls.get_game_cursor_position()
        final_error = math.sqrt((x - final_x) ** 2 + (y - final_y) ** 2)
        print(f"✗ 未达到理想精度! 最终误差: {final_error:.2f}像素")
        print("=" * 50)

    @classmethod
    def click(cls, button='left'):
        """执行鼠标点击"""
        print(f"点击鼠标: {button}键")
        pyautogui.click(button=button)

    @classmethod
    def move_and_click(cls, x, y, button='left'):
        """移动并点击（自动使用偏移修正）"""
        print(f"\n{'=' * 30} 移动并点击 {'=' * 30}")
        print(f"目标位置: X={x}, Y={y}")
        cls.move_to(x, y, correction=True)
        cls.click(button)
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


if __name__ == "__main__":
    print("鼠标控制器初始化...")
    time.sleep(1)

    # 示例使用
    print("\n测试移动操作...")
    target_x, target_y = 500, 300
    mouse.move_to(target_x, target_y)  # 带修正的移动

    # 动态调整参数
    print("\n调整参数...")
    mouse.configure(
        INITIAL_STEP_RATIO=0.8,
        ERROR_THRESHOLD=2,
        STEP_DELAY=0.2
    )

    # 带修正的移动并点击
    # print("\n测试移动并点击操作...")
    # mouse.move_and_click(700, 400)
    #
    # print("\n所有操作完成!")
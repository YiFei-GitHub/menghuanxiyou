import pyautogui
import time
import logging
import math


class mouse:

    pyautogui.FAILSAFE = True

    # 类级配置参数
    CORRECTION_ENABLED = True  # 全局开关
    INITIAL_STEP_RATIO = 0.85  # 第一步移动比例
    MICRO_ADJUST_RATIO = 0.4  # 微调移动比例
    MAX_ATTEMPTS = 5  # 最大微调次数
    ERROR_THRESHOLD = 3  # 可接受误差阈值(像素)
    STEP_DELAY = 0.15  # 移动后等待时间

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
            pyautogui.moveTo(x, y, duration=duration)
            return

        # 第一步：获取当前位置并计算85%移动
        current_x, current_y = cls.get_game_cursor_position()
        dx = x - current_x
        dy = y - current_y

        # 计算第一步目标位置
        step1_x = current_x + dx * cls.INITIAL_STEP_RATIO
        step1_y = current_y + dy * cls.INITIAL_STEP_RATIO

        # 执行第一步移动
        pyautogui.moveTo(step1_x, step1_y, duration=duration)
        time.sleep(cls.STEP_DELAY)

        # 第二步：迭代微调
        for attempt in range(cls.MAX_ATTEMPTS):
            current_x, current_y = cls.get_game_cursor_position()
            dx = x - current_x
            dy = y - current_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # 检查是否达到精度要求
            if distance <= cls.ERROR_THRESHOLD:
                logging.debug(f"偏移修正完成 误差: {distance:.1f}像素")
                return

            # 计算微调步长
            step_x = dx * cls.MICRO_ADJUST_RATIO
            step_y = dy * cls.MICRO_ADJUST_RATIO

            # 微调移动
            adjust_duration = max(0.05, duration * 0.5)  # 更短的微调时间
            pyautogui.moveTo(current_x + step_x, current_y + step_y, duration=adjust_duration)
            time.sleep(cls.STEP_DELAY)

        # 最终位置记录
        final_x, final_y = cls.get_game_cursor_position()
        final_error = math.sqrt((x - final_x) ** 2 + (y - final_y) ** 2)
        logging.info(f"偏移修正完成 最终误差: {final_error:.1f}像素")

    @classmethod
    def click(cls, button='left'):
        """执行鼠标点击"""
        pyautogui.click(button=button)

    @classmethod
    def move_and_click(cls, x, y, button='left'):

        """移动并点击（自动使用偏移修正）"""
        cls.move_to(x, y, correction=True)
        cls.click(button)

    @classmethod
    def get_game_cursor_position(cls):
        """
        获取游戏内鼠标实际位置（需实现）
        返回: (x, y)
        """
        # 这里需要您的具体实现
        # 示例：使用图像识别定位游戏鼠标
        return pyautogui.position()  # 临时使用系统位置

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
                logging.info(f"参数更新: {key} = {value}")


if __name__ == "__main__":

    time.sleep(2)

    # 示例使用
    target_x, target_y = 500, 300
    mouse.move_to(target_x, target_y)  # 带修正的移动


    # 带修正的移动并点击
    mouse.move_and_click(700, 400)
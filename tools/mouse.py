import pyautogui
import time
import logging

class mouse:
    # 类属性，用于存储安全延迟时间
    safety_delay = 1.0
    logger = logging.getLogger("MouseController")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 添加控制台输出
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 启用PyAutoGUI的安全特性，将鼠标移动到左上角可终止程序
    pyautogui.FAILSAFE = True

    logger.info(f"鼠标控制器已初始化，安全延迟: {safety_delay}秒")

    @classmethod
    def _get_screen_size(cls):
        """获取屏幕尺寸"""
        return pyautogui.size()

    @classmethod
    def move_to(cls, x, y, duration=0.5):
        """
        移动鼠标到指定位置
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动持续时间（秒）
        """
        cls._apply_safety_delay()
        cls.logger.info(f"移动鼠标到坐标 ({x}, {y})，持续时间: {duration}秒")
        pyautogui.moveTo(x, y, duration=duration)

    @classmethod
    def click(cls, button='left'):
        """
        点击鼠标按钮
        Args:
            button: 按钮类型，'left'（左键）、'right'（右键）或'middle'（中键）
        """
        cls._apply_safety_delay()
        cls.logger.info(f"点击鼠标 {button} 键")
        pyautogui.click(button=button)

    @classmethod
    def move_and_click(cls, x, y, button='left', duration=0.5, offset_range=5):
        """
         移动鼠标到指定位置附近并点击
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            button: 按钮类型
            duration: 移动持续时间（秒）
            offset_range: 随机偏移的最大范围（像素）
        """
        # 计算随机偏移量
        import random
        x_offset = random.randint(-offset_range, offset_range)
        y_offset = random.randint(-offset_range, offset_range)

        # 应用偏移量到目标坐标
        adjusted_x = (x + x_offset)
        adjusted_y = (y + y_offset)

        print(f"目标坐标: ({x}, {y})，实际移动到: ({adjusted_x}, {adjusted_y})，偏移量: ({x_offset}, {y_offset})")

        cls.move_to(adjusted_x, adjusted_y, duration)
        cls.click(button)

    @classmethod
    def _apply_safety_delay(cls):
        """应用安全延迟"""
        if cls.safety_delay > 0:
            cls.logger.info(f"等待安全延迟: {cls.safety_delay}秒")
            time.sleep(cls.safety_delay)


# 设置日志
logging.basicConfig(level=logging.INFO)
import pyautogui
import time
import logging

class mouse:

     # 启用PyAutoGUI的安全特性，将鼠标移动到左上角可终止程序
    pyautogui.FAILSAFE = True

    @classmethod
    def move_to(cls, x, y, duration=0.5):
        """
        移动鼠标到指定位置
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动持续时间（秒）
        """
        pyautogui.moveTo(x, y, duration=duration)

    @classmethod
    def click(cls, button='left'):
        """
        点击鼠标按钮   button: 按钮类型，'left'（左键）、'right'（右键）或'middle'（中键）
        """
        pyautogui.click(button=button)




    """
     移动鼠标到指定位置附近并点击
    Args:
        x: 目标X坐标
        y: 目标Y坐标
        button: 按钮类型
    """
    @classmethod
    def move_and_click(cls, x, y, button='left'):

        # 计算随机偏移量
        import random
        offset_range = 1  # offset_range: 随机偏移的最大范围（像素）
        x_offset = random.randint(-offset_range, offset_range)
        y_offset = random.randint(-offset_range, offset_range)


        # 应用偏移量到目标坐标
        adjusted_x = (x + x_offset)
        adjusted_y = (y + y_offset)

        print(f"目标坐标: ({x}, {y})，实际移动到: ({adjusted_x}, {adjusted_y})，偏移量: ({x_offset}, {y_offset})")

        cls.move_to(adjusted_x, adjusted_y)
        cls.click(button)

if __name__ == "__main__":

    time.sleep(1)


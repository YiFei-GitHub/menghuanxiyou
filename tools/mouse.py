import pyautogui
import time
import logging

class mouse:

     # 启用PyAutoGUI的安全特性，将鼠标移动到左上角可终止程序
    pyautogui.FAILSAFE = True

    """
        移动鼠标到指定位置
         x: 目标X坐标
         y: 目标Y坐标
        duration: 移动持续时间（秒）
    """
    @classmethod
    def move_to(cls, x, y, duration=0.5):
        pyautogui.moveTo(x, y, duration=duration)



    """
    点击鼠标按钮   button: 按钮类型，'left'（左键）、'right'（右键）或'middle'（中键）
    """
    @classmethod
    def click(cls, button='left'):

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
        cls.move_to(x, y)
        cls.click(button)


if __name__ == "__main__":

    time.sleep(1)


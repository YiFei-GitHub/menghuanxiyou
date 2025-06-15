import pyautogui
import time
import cv2
import numpy as np
import pytesseract
from tools.image import image
from tools.mouse import mouse

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def back_to_master():
    """回到师门，按下F8"""
    print("回到师门...")
    pyautogui.press('f8')
    time.sleep(2)  # 等待界面加载


def find_and_click_master():
    # 创建 image 类的实例，使用师傅的图片
    ImageMatcher = image("master.png", threshold=0.6)  # 假设师傅的图片名为 master.png
    position = ImageMatcher.find_image_position()

    if position:
        x, y = position
        print(f"找到《师父》，坐标: ({x}, {y})")
        mouse.move_and_click(x-15, y+10,'left',2,2)
        time.sleep(1)
        print(f"鼠标位置，坐标: ({pyautogui.position().x}, {pyautogui.position().y})")
        return True
    else:
        print("未找到目标图片")
        find_and_click_master();
        return False


def click_task_button():
    """点击任务按钮"""
    print("点击任务按钮...")
    # 创建 image 类的实例，使用师傅的图片
    ImageMatcher = image("speak-task.png", threshold=0.9)
    position = ImageMatcher.find_image_position()

    if position:
        x, y = position
        print(f"找到《任务按钮》，坐标: ({x}, {y})")
        mouse.move_and_click(x-15, y+15,'left',2,2)
        time.sleep(1)
        print(f"鼠标位置，坐标: ({pyautogui.position().x}, {pyautogui.position().y})")
        return True
    else:
        print("未找到目标图片")
        return False
    time.sleep(1)

def recognize_task():
    """识别任务追踪栏里面的任务项"""
    print("识别任务项...")
    # 截取任务追踪栏的屏幕区域
    task_area = (100, 200, 300, 400)  # 根据实际情况调整
    screenshot = pyautogui.screenshot(region=task_area)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 这里可以使用OCR或者模板匹配等方法来识别任务项
    # 示例代码，仅打印截图
    cv2.imshow('Task Area', screenshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        time.sleep(2)
        back_to_master()
        find_and_click_master()
        time.sleep(10)
        click_task_button()
        # recognize_task()
        print("师门任务流程完成!")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")

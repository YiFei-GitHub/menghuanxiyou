import win32gui
import win32ui
import win32con
import cv2
import numpy as np
from pynput import mouse
from ultralytics import YOLO
import time

# 用于标记模块是否被加载
MODULE_LOADED = True

# 加载 YOLO 模型
#model = YOLO("H:\yol\yolo\v11\runs\detect\train37\weights\best.pt")
model = YOLO("../yolo8_dataset/runs/detect/menghuan_train_v2/weights/best.pt")

def find_window():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "梦幻西游" in title:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    if hwnds:
        return hwnds[0]
    return None


def get_window_screenshot(hwnd):
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


def draw_detection_boxes(screenshot, results):
    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            class_id = int(box.cls[0])
            conf = round(box.conf[0], 2)
            # 获取类别名
            class_name = model.names[class_id]
            x1, y1, x2, y2 = box.xyxy[0].astype(int)

            # 在图像上绘制检测框
            cv2.rectangle(screenshot, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 修改标签，按照（类别名 + ID）格式
            label = f"({class_name} + ID: {class_id})"
            cv2.putText(screenshot, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return screenshot


def start_detection():
    hwnd = find_window()
    if hwnd is None:
        print("未找到标题中包含'梦幻西游'的窗口")
        return

    cv2.namedWindow("Detection Window", cv2.WINDOW_NORMAL)

    while True:
        screenshot = get_window_screenshot(hwnd)
        results = model(screenshot)
        screenshot_with_boxes = draw_detection_boxes(screenshot, results)

        cv2.imshow("Detection Window", screenshot_with_boxes)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
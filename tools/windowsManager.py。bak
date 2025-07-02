import win32gui
import win32con
import win32api
import time
import re


def find_all_visible_windows():
    """查找并返回所有可见窗口的句柄和标题"""
    windows = []

    def enum_callback(hwnd, windows_list):
        """窗口枚举回调函数"""
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows_list.append((hwnd, win32gui.GetWindowText(hwnd)))
        return True

    win32gui.EnumWindows(enum_callback, windows)
    return windows


def move_game_window():
    """
    查找梦幻西游游戏窗口并移动到屏幕左上角
    窗口标题匹配模式: "梦幻西游 ONLINE.*"
    """
    # 窗口标题匹配模式
    window_pattern = re.compile(r"梦幻西游 ONLINE.*")
    windows = find_all_visible_windows()
    target_hwnd = None

    # 查找匹配的游戏窗口
    for hwnd, title in windows:
        if window_pattern.match(title):
            print(f"找到游戏窗口: {title}")
            target_hwnd = hwnd
            break

    # 未找到窗口的处理
    if not target_hwnd:
        print("错误: 未找到游戏窗口")
        print("当前可见窗口列表:")
        for _, title in windows:
            print(f"  - {title}")
        return False

    try:
        # 检查并恢复最小化窗口
        if win32gui.IsIconic(target_hwnd):
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)  # 给窗口恢复的时间

        # 获取窗口当前位置和大小
        left, top, right, bottom = win32gui.GetWindowRect(target_hwnd)
        current_width = right - left
        current_height = bottom - top

        # 移动窗口到左上角(0,0)，保持原有大小
        win32gui.SetWindowPos(
            target_hwnd,
            win32con.HWND_TOP,  # 置于顶层
            0, 0,  # 左上角位置
            current_width, current_height,  # 保持原有大小
            win32con.SWP_SHOWWINDOW
        )

        print(f"窗口已移动到左上角(0,0)，大小保持不变({current_width}x{current_height})")
        return True

    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("开始定位并移动梦幻西游窗口...")
    if move_game_window():
        print("操作成功完成!")
    else:
        print("操作未完成，请检查问题后重试")
import win32gui
import win32con
import time


def find_all_windows():
    """查找所有窗口并打印标题和句柄"""

    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        return True

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows


def print_all_windows():
    """打印所有可见窗口的标题和句柄"""
    windows = find_all_windows()
    print("当前可见窗口列表：")
    for hwnd, title in windows:
        print(f"句柄: {hwnd}, 标题: {title}")


def move_game_window(window_title=None):
    """查找并移动游戏窗口到屏幕左上角"""
    if window_title is None:
        # 游戏窗口标题，可能需要根据实际情况调整
        window_titles = ["梦幻西游 ONLINE"]
    else:
        window_titles = [window_title]

    # 尝试查找游戏窗口
    hwnd = None
    for title in window_titles:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            print(f"找到窗口: {title}")
            break

    if not hwnd:
        print("未找到游戏窗口，请确保游戏已启动")
        # 打印所有可见窗口帮助调试
        print("\n尝试查找以下窗口标题：")
        for title in window_titles:
            print(f"- {title}")
        print("\n当前可见窗口列表：")
        windows = find_all_windows()
        for _, title in windows:
            print(f"- {title}")
        return

    # 获取窗口当前状态
    window_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

    # 如果窗口是最小化状态，先恢复
    if window_style & win32con.WS_MINIMIZE:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.5)  # 等待窗口恢复

    # 获取屏幕分辨率
    screen_width = win32gui.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32gui.GetSystemMetrics(win32con.SM_CYSCREEN)

    # 设置窗口位置和大小
    x = 0
    y = 0
    width = int(screen_width * 0.75)
    height = int(screen_height * 0.8)

    # 移动窗口
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,  # 窗口置顶
        x, y, width, height,
        win32con.SWP_SHOWWINDOW  # 确保窗口可见
    )

    print(f"窗口已移动到位置: ({x}, {y})，大小: {width}x{height}")


if __name__ == "__main__":
    move_game_window()
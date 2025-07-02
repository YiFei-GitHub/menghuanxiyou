import win32gui
import win32con
import time


def move_game_window():
    """查找并移动梦幻西游游戏窗口到屏幕左上角"""
    # 游戏窗口标题，可能需要根据实际情况调整
    window_titles = ["梦幻西游 ONLINE", "梦幻西游", "Westward Journey"]

    # 尝试查找游戏窗口
    hwnd = None
    for title in window_titles:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            print(f"找到窗口: {title}")
            break

    if not hwnd:
        print("未找到梦幻西游游戏窗口，请确保游戏已启动")
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
    # 这里将窗口移动到左上角(0,0)，并设置为屏幕宽度的3/4和高度的4/5
    # 你可以根据需要调整这些值
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
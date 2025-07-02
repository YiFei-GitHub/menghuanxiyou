import win32gui
import win32con
import re


class GameWindowUtils:

    @staticmethod
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

    @staticmethod
    def find_game_window(pattern=r"梦幻西游 ONLINE.*"):
        """
        查找梦幻西游游戏窗口

        参数:
            pattern (str): 窗口标题匹配的正则表达式模式

        返回:
            tuple: (hwnd, title) 窗口句柄和标题，如果没有找到返回 (None, None)
        """
        windows = GameWindowUtils.find_all_visible_windows()
        window_pattern = re.compile(pattern)

        for hwnd, title in windows:
            if window_pattern.match(title):
                print(f"找到游戏窗口: {title}")
                return hwnd, title

        # 如果没找到，打印所有窗口标题帮助调试
        print("未找到游戏窗口，当前可见窗口列表:")
        for _, title in windows:
            print(f"  - {title}")

        return None, None

    @staticmethod
    def move_window_to_top_left(hwnd):
        """
        将指定窗口移动到屏幕左上角(0,0)位置，保持原有大小

        参数:
            hwnd: 窗口句柄

        返回:
            bool: 操作是否成功
        """
        if not hwnd:
            print("错误: 无效的窗口句柄")
            return False

        try:
            # 检查并恢复最小化窗口
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)  # 给窗口恢复的时间

            # 获取窗口当前位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            current_width = right - left
            current_height = bottom - top

            # 移动窗口到左上角(0,0)，保持原有大小
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,  # 置于顶层
                0, 0,  # 左上角位置
                current_width, current_height,  # 保持原有大小
                win32con.SWP_SHOWWINDOW
            )

            print(f"窗口已移动到左上角(0,0)，大小保持不变({current_width}x{current_height})")
            return True

        except Exception as e:
            print(f"移动窗口时出错: {str(e)}")
            return False

    @staticmethod
    def activate_window(hwnd):
        """激活并聚焦指定窗口"""
        if not hwnd:
            return False

        try:
            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            # 将窗口置于前台
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            print(f"激活窗口时出错: {str(e)}")
            return False

    @staticmethod
    def get_window_rect(hwnd):
        """获取窗口位置和大小"""
        if not hwnd:
            return None

        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            return {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
                "width": right - left,
                "height": bottom - top
            }
        except Exception as e:
            print(f"获取窗口位置时出错: {str(e)}")
            return None

    @staticmethod
    def set_window_size(hwnd, width, height):
        """设置窗口大小"""
        if not hwnd:
            return False

        try:
            # 获取当前窗口位置
            left, top, _, _ = win32gui.GetWindowRect(hwnd)

            # 设置新大小
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                left, top, width, height,
                win32con.SWP_SHOWWINDOW
            )
            print(f"窗口大小已设置为: {width}x{height}")
            return True
        except Exception as e:
            print(f"设置窗口大小时出错: {str(e)}")
            return False


# 使用示例
if __name__ == "__main__":
    print("开始定位并移动梦幻西游窗口...")

    # 查找游戏窗口
    hwnd, title = GameWindowUtils.find_game_window()

    if hwnd:
        # 激活窗口
        GameWindowUtils.activate_window(hwnd)

        # 获取窗口信息
        rect = GameWindowUtils.get_window_rect(hwnd)
        if rect:
            print(f"窗口位置: 左={rect['left']}, 上={rect['top']}, 宽={rect['width']}, 高={rect['height']}")

        # 移动窗口到左上角
        if GameWindowUtils.move_window_to_top_left(hwnd):
            print("操作成功完成!")
        else:
            print("移动窗口失败")
    else:
        print("未找到游戏窗口")
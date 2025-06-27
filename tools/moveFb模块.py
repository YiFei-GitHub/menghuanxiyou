import cv2
import numpy as np
import pyautogui
from ultralytics import YOLO
import time
import win32gui
from 检测框模块 import get_window_screenshot,start_detection,draw_detection_boxes
import 检测框模块
import threading

def movefb(hwnd, left, top, window_width, window_height, model, 要点击的目标类, offset_x=0, offset_y=0, 置信度=0.4,
           click_type='left', success_image=None, 如果不成功循环执行的次数=1, mouse_shape_image=None, click_error=45):
    loop_count = 0
    class_names = model.names  # 获取类别名称映射
    while loop_count < 如果不成功循环执行的次数:
        # 获取窗口截图
        screenshot = get_window_screenshot(hwnd)

        # 保存截图用于调试
        timestamp = int(time.time())
        screenshot_path = f"debug_screenshot_{timestamp}.png"
        cv2.imwrite(screenshot_path, screenshot)
        print(f"保存截图: {screenshot_path} ({screenshot.shape[1]}x{screenshot.shape[0]})")

        # 进行目标检测
        results = model(screenshot)

        found_target = False
        detected_classes = []
        dart_center_x, dart_center_y = None, None
        target_center_x, target_center_y = None, None

        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                class_id = int(box.cls[0])
                conf = box.conf[0]
                class_name = class_names[class_id]  # 获取类别名称
                detected_classes.append(class_id)
                print(f"检测到目标，类别 ID: {class_id}，类别名称: {class_name}，相似度: {conf}")

                if class_id == 0:  # 检测飞镖（类别 0）
                    x1, y1, x2, y2 = box.xyxy[0].astype(int)
                    dart_center_x = int((x1 + x2) / 2) - 20  # 飞镖尖端 x 坐标
                    dart_center_y = int((y1 + y2) / 2) - 20  # 飞镖尖端 y 坐标
                    print(f"检测到飞镖，类别 ID: {class_id}，坐标x{dart_center_x}，坐标y{dart_center_y}")

                if class_id == 要点击的目标类 and conf >= 置信度:
                    found_target = True
                    x1, y1, x2, y2 = box.xyxy[0].astype(int)
                    target_center_x = int((x1 + x2) / 2) + offset_x + 1  # 目标中心 x 坐标
                    target_center_y = int((y1 + y2) / 2) + offset_y + 1  # 目标中心 y 坐标

        # 检测不到类别 0 时，尝试使用图像匹配检测鼠标形状变化
        if dart_center_x is None and dart_center_y is None and mouse_shape_image:
            print(f"进入图片检测到飞镖逻辑")
            template = cv2.imread(mouse_shape_image, 0)
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= 置信度:
                if found_target and target_center_x is not None and target_center_y is not None:
                    target_screen_x = left + target_center_x
                    target_screen_y = top + target_center_y
                    pyautogui.moveTo(target_screen_x, target_screen_y)
                    pyautogui.click(button=click_type)
                    # 检查任务是否成功
                    if isinstance(success_image, int):
                        # 如果 success_image 是类别 ID
                        new_screenshot = get_window_screenshot(hwnd)
                        new_results = model(new_screenshot)
                        success = False
                        for new_result in new_results:
                            new_boxes = new_result.boxes.cpu().numpy()
                            for new_box in new_boxes:
                                new_class_id = int(new_box.cls[0])
                                new_class_name = class_names[new_class_id]  # 获取类别名称
                                new_conf = new_box.conf[0]
                                if new_class_id == success_image:
                                    success = True
                                    print(
                                        f"检测到成功类别，类别 ID: {new_class_id}，类别名称: {new_class_name}，相似度: {new_conf}")
                                    break
                            if success:
                                break
                        print(f"任务成功条件（类别 ID）是否满足: {success}")
                        if success:
                            return True
                    elif success_image:
                        # 如果 success_image 是图片路径
                        template = cv2.imread(success_image, 0)
                        new_screenshot = get_window_screenshot(hwnd)
                        new_screenshot_gray = cv2.cvtColor(new_screenshot, cv2.COLOR_BGR2GRAY)
                        result = cv2.matchTemplate(new_screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        success = max_val >= 置信度
                        print(f"任务成功条件（图片匹配）是否满足: {success}")
                        if success:
                            return True
                    else:
                        # 默认被点击的类别消失就是任务成功
                        new_screenshot = get_window_screenshot(hwnd)
                        new_results = model(new_screenshot)
                        new_found = False
                        for new_result in new_results:
                            new_boxes = new_result.boxes.cpu().numpy()
                            for new_box in new_boxes:
                                new_class_id = int(new_box.cls[0])
                                new_class_name = class_names[new_class_id]  # 获取类别名称
                                new_conf = new_box.conf[0]
                                if new_class_id == 要点击的目标类:
                                    new_found = True
                                    print(
                                        f"检测到目标类别，类别 ID: {new_class_id}，类别名称: {new_class_name}，相似度: {new_conf}")
                                    break
                            if new_found:
                                break
                        success = not new_found
                        print(f"任务成功条件（目标类别消失）是否满足: {success}")
                        if success:
                            return True
                continue

        # 目标 - 飞镖 - 精确点击
        if found_target and target_center_x is not None and target_center_y is not None:
            print(f"✅ 符合预期，准备点击了")
            print(f"目标位置 (窗口坐标): x={target_center_x}, y={target_center_y}")

            # 先移动鼠标到目标位置
            target_screen_x = left + target_center_x
            target_screen_y = top + target_center_y
            print(f"移动鼠标到屏幕位置: x={target_screen_x}, y={target_screen_y}")
            pyautogui.moveTo(target_screen_x, target_screen_y)

            # 添加循环计数器用于日志
            loop_count = 0
            last_dart_position = None

            # 检测和计算飞镖和目标的距离，根据距离和方向再度移动鼠标
            while True:
                loop_count += 1
                print(f"\n--- 调整循环 #{loop_count} ---")

                # 获取截图
                screenshot = get_window_screenshot(hwnd)
                print(f"截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")

                # 进行目标检测
                print("开始检测飞镖...")
                results = model(screenshot)
                dart_center_x, dart_center_y = None, None

                for result in results:
                    boxes = result.boxes.cpu().numpy()
                    print(f"检测到 {len(boxes)} 个框")

                    for box in boxes:
                        class_id = int(box.cls[0])
                        conf = box.conf[0]
                        print(f"  框: 类别={class_id}, 置信度={conf:.2f}")

                        if class_id == 0:
                            x1, y1, x2, y2 = box.xyxy[0].astype(int)
                            print(f"  飞镖位置: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

                            # 计算飞镖尖端位置
                            dart_center_x = int((x1 + x2) / 2) - 20
                            dart_center_y = int((y1 + y2) / 2) - 20
                            print(f"  飞镖尖端位置: x={dart_center_x}, y={dart_center_y}")
                            break

                # 检查是否检测到飞镖
                if dart_center_x is not None and dart_center_y is not None:
                    last_dart_position = (dart_center_x, dart_center_y)
                    print(f"✅ 检测到飞镖位置: x={dart_center_x}, y={dart_center_y}")

                    # 计算飞镖尖端与目标中心的距离
                    dx = target_center_x - dart_center_x
                    dy = target_center_y - dart_center_y
                    distance = np.sqrt(dx ** 2 + dy ** 2)
                    print(f"飞镖与目标距离: {distance:.2f} (阈值: {click_error})")

                    if distance < click_error:
                        print(f"✅ 距离满足条件 (< {click_error})，跳出调整循环")
                        break

                    # 获取当前鼠标位置
                    current_x, current_y = pyautogui.position()
                    print(f"当前鼠标位置: x={current_x}, y={current_y}")

                    # 计算新位置
                    new_x = current_x + dx
                    new_y = current_y + dy
                    print(f"计算新位置: x={new_x}, y={new_y}")

                    # 限制鼠标在窗口内移动
                    new_x_clamped = max(left - 50, min(new_x, left + window_width + 50))
                    new_y_clamped = max(top - 50, min(new_y, top + window_height + 50))
                    print(f"限制后位置: x={new_x_clamped}, y={new_y_clamped}")

                    # 计算实际移动量
                    dx_move = new_x_clamped - current_x
                    dy_move = new_y_clamped - current_y
                    print(f"实际移动量: dx={dx_move}, dy={dy_move}")

                    # 移动鼠标
                    if dx_move != 0 or dy_move != 0:
                        print(f"移动鼠标: dx={dx_move}, dy={dy_move}")
                        pyautogui.moveRel(dx_move, dy_move)
                    else:
                        print("无需移动鼠标")
                else:
                    print("❌ 未检测到飞镖")

                    # 如果之前有记录飞镖位置，使用最后已知位置
                    if last_dart_position:
                        dart_center_x, dart_center_y = last_dart_position
                        print(f"使用最后已知飞镖位置: x={dart_center_x}, y={dart_center_y}")
                    else:
                        print("无飞镖位置记录，继续尝试检测")
            # 执行点击
            print("执行点击操作")
            pyautogui.click(button=click_type)
            print("✅ 点击完成")

        if found_target:
            # 检查任务是否成功
            if isinstance(success_image, int):
                # 如果 success_image 是类别 ID
                new_screenshot = get_window_screenshot(hwnd)
                new_results = model(new_screenshot)
                success = False
                for new_result in new_results:
                    new_boxes = new_result.boxes.cpu().numpy()
                    for new_box in new_boxes:
                        new_class_id = int(new_box.cls[0])
                        new_class_name = class_names[new_class_id]  # 获取类别名称
                        new_conf = new_box.conf[0]
                        if new_class_id == success_image:
                            success = True
                            print(
                                f"检测到成功类别，类别 ID: {new_class_id}，类别名称: {new_class_name}，相似度: {new_conf}")
                            break
                    if success:
                        break
                print(f"任务成功条件（类别 ID）是否满足: {success}")
                if success:
                    return True
            elif success_image:
                # 如果 success_image 是图片路径
                template = cv2.imread(success_image, 0)
                new_screenshot = get_window_screenshot(hwnd)
                new_screenshot_gray = cv2.cvtColor(new_screenshot, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(new_screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                success = max_val >= 置信度
                print(f"任务成功条件（图片匹配）是否满足: {success}")
                if success:
                    return True
            else:
                # 默认被点击的类别消失就是任务成功
                new_screenshot = get_window_screenshot(hwnd)
                new_results = model(new_screenshot)
                new_found = False
                for new_result in new_results:
                    new_boxes = new_result.boxes.cpu().numpy()
                    for new_box in new_boxes:
                        new_class_id = int(new_box.cls[0])
                        new_class_name = class_names[new_class_id]  # 获取类别名称
                        new_conf = new_box.conf[0]
                        if new_class_id == 要点击的目标类:
                            new_found = True
                            print(
                                f"检测到目标类别，类别 ID: {new_class_id}，类别名称: {new_class_name}，相似度: {new_conf}")
                            break
                    if new_found:
                        break
                success = not new_found
                print(f"任务成功条件（目标类别消失）是否满足: {success}")
                if success:
                    return True

        loop_count += 1
        time.sleep(0.05)

    return False


hwnd = 检测框模块.find_window()
if hwnd is None:
    print("未找到标题中包含'梦幻西游'的窗口")
else:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    window_width = right - left
    window_height = bottom - top


def test_movefb_function():
    """测试movefb函数的移动功能"""
    try:
        print("=" * 50)
        print("开始测试movefb函数...")

        # 1. 加载YOLO模型
        model_path = "../yolo8_dataset/runs/detect/menghuan_train_v246/weights/best.pt"
        print(f"尝试加载模型: {model_path}")
        model = YOLO(model_path)

        if model is None:
            print("❌ 模型加载失败，请检查路径")
            return False
        else:
            print("✅ 模型加载成功")
            print(f"模型类别: {model.names}")

        # 模型预热
        print("进行模型预热...")
        dummy_image = np.zeros((256, 640, 3), dtype=np.uint8)
        _ = model(dummy_image)
        print("模型预热完成")

        # 2. 获取目标窗口
        print("获取目标窗口...")
        hwnd = 检测框模块.find_window()
        if not hwnd:
            print("❌ 未找到标题中包含'梦幻西游'的窗口，请确保窗口已打开")
            return False

        # 获取窗口位置和大小
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        window_width = right - left
        window_height = bottom - top
        print(f"✅ 找到梦幻西游窗口")
        print(f"  位置: ({left}, {top})")
        print(f"  大小: {window_width}x{window_height}")

        # 3. 验证窗口截图
        print("测试窗口截图功能...")
        test_screenshot = get_window_screenshot(hwnd)
        if test_screenshot is None:
            print("❌ 获取窗口截图失败")
            return False

        cv2.imwrite("window_screenshot.png", test_screenshot)
        print("✅ 保存窗口截图: window_screenshot.png")

        # 4. 设置测试参数
        print("设置测试参数...")
        要点击的目标类 = 1
        offset_x, offset_y = -2, -2
        置信度 = 0.7  # 降低置信度阈值
        click_type = 'left'
        如果不成功循环执行的次数 = 10  # 减少循环次数用于测试
        success_image = None

        # 5. 调用movefb函数
        print("开始调用movefb函数进行测试...")
        start_time = time.time()

        result = movefb(
            hwnd=hwnd,
            left=left,
            top=top,
            window_width=window_width,
            window_height=window_height,
            model=model,
            要点击的目标类=要点击的目标类,
            offset_x=offset_x,
            offset_y=offset_y,
            置信度=置信度,
            click_type=click_type,
            success_image=success_image,
            如果不成功循环执行的次数=如果不成功循环执行的次数
        )

        # 6. 输出测试结果
        end_time = time.time()
        print(f"测试完成，耗时: {end_time - start_time:.2f}秒")

        if result:
            print("✅ 测试成功: movefb函数执行成功")
        else:
            print("❌ 测试失败: movefb函数执行失败")

        return result

    except Exception as e:
        import traceback
        print(f"❌ 测试过程中出错: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":

    # detection_thread = threading.Thread(target=start_detection, daemon=True)
    # detection_thread.start()
    # print("检测线程已启动（守护线程）")
    start_detection();
    test_movefb_function()
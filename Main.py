from tools.mouse import mouse

def main():

    """测试鼠标控制模块的主函数"""
    print("开始测试鼠标控制模块...")

    try:
        # 直接使用类调用 move_and_click 方法
        mouse.move_and_click(800, 500,'left')

        print("测试完成!")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
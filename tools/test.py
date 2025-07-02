import threading
import time

# 创建互斥锁
lock = threading.Lock()

def print_odd():
    """打印奇数的线程函数"""
    for i in range(1, 10, 2):
        with lock:
            print(f"线程1: {i}")
        time.sleep(0.2)  # 控制输出速度

def print_even():
    """打印偶数的线程函数"""
    for i in range(2, 11, 2):
        with lock:
            print(f"线程2: {i}")
        time.sleep(0.3)  # 不同的间隔时间

if __name__ == "__main__":
    # 创建线程
    t1 = threading.Thread(target=print_odd)
    t2 = threading.Thread(target=print_even)

    # 启动线程
    t1.start()
    t2.start()

    # 等待线程完成
    t1.join()
    t2.join()

    print("所有输出完成")
import cv2
import os


def extract_frames(video_path, output_folder, frames_per_second=1):
    """
    从视频中每秒提取指定数量的帧并保存为图片

    参数:
        video_path (str): 视频文件路径
        output_folder (str): 输出图片的文件夹
        frames_per_second (int): 每秒提取的帧数(默认为1)
    """
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("无法打开视频文件")
        return

    # 获取视频帧率
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(round(fps / frames_per_second))

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # 每秒保存一帧
        if frame_count % frame_interval == 0:
            # 构造输出文件名
            output_path = os.path.join(output_folder, f"{saved_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            print(f"已保存: {output_path}")

        frame_count += 1

    cap.release()
    print(f"处理完成! 共保存 {saved_count} 张图片")


# 使用示例
if __name__ == "__main__":
    video_file = "6.mp4"  # 替换为你的视频文件路径
    output_dir = video_file+"output"  # 输出文件夹

    extract_frames(video_file, output_dir)
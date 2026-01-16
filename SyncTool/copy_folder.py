import os
import shutil
import sys

def copy_folder(src_folder: str, dst_folder: str):
    """
    将 src_folder 内的所有内容复制到 dst_folder，支持递归、覆盖、处理只读文件
    """
    if not os.path.exists(src_folder):
        print(f"源文件夹不存在: {src_folder}")
        return

    if not os.path.isdir(src_folder):
        print(f"源路径不是文件夹: {src_folder}")
        return

    os.makedirs(dst_folder, exist_ok=True)

    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dst_path = os.path.join(dst_folder, item)

        try:
            if os.path.isdir(src_path):
                # 递归复制子目录
                copy_folder(src_path, dst_path)
            else:
                # 复制文件，先处理只读和已存在的目标
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                if os.path.exists(dst_path):
                    os.chmod(dst_path, 0o666)
                    os.remove(dst_path)
                shutil.copy2(src_path, dst_path)
                print(f"已复制文件: {src_path} -> {dst_path}")
        except Exception as e:
            print(f"复制失败: {src_path} -> {dst_path}，错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python copy_folder.py <源文件夹路径> <目标文件夹路径>")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    copy_folder(src, dst)

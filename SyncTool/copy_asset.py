import os
import shutil
import sys

def copy_asset(src_asset: str, dst_asset: str):
    """
    复制单个资产文件，如果存在对应的 .meta 文件也一并复制
    """
    # 检查源文件是否存在
    if not os.path.isfile(src_asset):
        print(f"源资产文件不存在: {src_asset}")
        return

    # 创建目标目录（如果不存在）
    dst_dir = os.path.dirname(dst_asset)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # 复制主文件
    try:
        shutil.copy2(src_asset, dst_asset)
        print(f"已复制资产文件: {src_asset} -> {dst_asset}")
    except Exception as e:
        print(f"复制资产文件失败: {src_asset}, 错误: {e}")

    # 复制 .meta 文件
    src_meta = src_asset + ".meta"
    dst_meta = dst_asset + ".meta"

    if os.path.isfile(src_meta):
        try:
            shutil.copy2(src_meta, dst_meta)
            print(f"已复制 Meta 文件: {src_meta} -> {dst_meta}")
        except Exception as e:
            print(f"复制 Meta 文件失败: {src_meta}, 错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python copy_asset.py <源资产文件> <目标资产文件>")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    copy_asset(src, dst)

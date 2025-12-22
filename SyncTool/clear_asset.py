import os
import sys

def clear_asset(asset_file: str):
    """
    删除指定资产文件，如果存在对应的 .meta 文件也一并删除
    """
    # 删除主文件
    if os.path.isfile(asset_file):
        try:
            os.remove(asset_file)
            print(f"已删除资产文件: {asset_file}")
        except Exception as e:
            print(f"删除资产文件失败: {asset_file}, 错误: {e}")
    else:
        print(f"资产文件不存在: {asset_file}")

    # 检查并删除 .meta 文件
    meta_file = asset_file + ".meta"
    if os.path.isfile(meta_file):
        try:
            os.remove(meta_file)
            print(f"已删除资产 Meta 文件: {meta_file}")
        except Exception as e:
            print(f"删除 Meta 文件失败: {meta_file}, 错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python clear_asset.py <资产文件路径>")
        sys.exit(1)

    target_asset = sys.argv[1]
    clear_asset(target_asset)

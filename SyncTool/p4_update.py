import subprocess
import sys
import os
import argparse

P4_EXECUTABLE = r"C:\Program Files\Perforce\p4.exe"

def p4_update(path: str, client: str = None):
    """
    使用 p4 命令更新指定 depot 路径
    """

    # 在脚本里设置固定的服务器和用户
    os.environ["P4PORT"] = "p4-world.funplus.com.cn:1666"
    os.environ["P4USER"] = "worldx_robot"

    # 如果传入了 client 参数，就覆盖环境变量
    if client:
        os.environ["P4CLIENT"] = client
    else:
        # 如果没传，就尝试读取已有环境变量
        client_env = os.environ.get("P4CLIENT")
        if not client_env:
            print("错误：未指定工作区 (--client)，且环境变量中没有 P4CLIENT。")
            sys.exit(1)
    try:
        # 调用 p4 sync 命令
        result = subprocess.run([P4_EXECUTABLE, "sync",
                                 "-f", f"{path}#head"],
                                capture_output=True,
                                text=True,
                                check=True,
                                env=os.environ)
        print("更新成功！输出如下：")
        print(path)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("更新失败！错误信息如下：")
        print(e.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="调用 p4 更新指定路径")
    parser.add_argument("path", help="要更新的 depot 路径或本地路径")
    parser.add_argument("--client", help="Perforce 工作区名 (P4CLIENT)，可选")

    args = parser.parse_args()
    p4_update(args.path, args.client)

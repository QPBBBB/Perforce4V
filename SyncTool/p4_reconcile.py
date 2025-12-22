import subprocess
import sys
import os
import argparse

P4 = r"C:\Program Files\Perforce\p4.exe"

def create_changelist(description: str):
    """
    创建一个新的 changelist，并返回 changelist 号
    """
    # p4 change -o 输出 changelist 模板
    template = subprocess.run([P4, "change", "-o"], capture_output=True, text=True, check=True).stdout

    # 修改描述
    new_spec = template.replace("<enter description here>", description)

    # 创建 changelist
    result = subprocess.run([P4, "change", "-i"], input=new_spec, capture_output=True, text=True, check=True)
    output = result.stdout.strip()

    # 输出类似 "Change 12345 created."
    if output.startswith("Change"):
        change_num = output.split()[1]
        return change_num
    else:
        raise RuntimeError(f"创建 changelist 失败: {output}")

def p4_reconcile(path: str, client: str = None) -> str:
    os.environ["P4PORT"] = "p4-world.funplus.com.cn:1666"
    os.environ["P4USER"] = "worldx_robot"

    if client:
        os.environ["P4CLIENT"] = client
    elif not os.environ.get("P4CLIENT"):
        print("错误：未指定工作区 (--client)，且环境变量中没有 P4CLIENT。")
        sys.exit(1)

    # 自动加上 "..."
    if not path.endswith("..."):
        if path.endswith("\\") or path.endswith("/"):
            path = path + "..."
        else:
            path = path + "/..."

    # 去掉前两个目录
    parts = path.split("\\")
    if len(parts) > 2:
        trimmed_path = "\\".join(parts[2:])
    else:
        trimmed_path = path

    # 构造 changelist 描述
    description = f"p4-bypass xrobot ver_0.01 to release mergepath : {trimmed_path}  "

    # 创建新的 changelist
    change_num = create_changelist(description)
    print(f"新建 changelist: {change_num}，描述: {description}")

    try:
        # 执行 reconcile 并指定 changelist
        result = subprocess.run(
            [P4, "reconcile", "-c", change_num, path],
            capture_output=True,
            text=True,
            check=True
        )
        print("Reconcile 成功！输出如下：")
        print(result.stdout)

        # 打印 changelist 内容
        opened = subprocess.run([P4, "opened", "-c", change_num], capture_output=True, text=True)
        print(f"Changelist {change_num} 内容：")
        print(opened.stdout)

    except subprocess.CalledProcessError as e:
        print("Reconcile 失败！")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)

    return change_num


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="调用 p4 reconcile 并放入新建 changelist")
    parser.add_argument("path", help="要 Reconcile 的文件夹路径 (本地路径或 depot 路径)")
    parser.add_argument("--client", help="Perforce 工作区名 (P4CLIENT)，可选")

    args = parser.parse_args()
    p4_reconcile(args.path, args.client)

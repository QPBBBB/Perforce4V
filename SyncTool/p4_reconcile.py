import subprocess
import sys
import os
import argparse

P4 = r"C:\Program Files\Perforce\p4.exe"


def create_changelist(description: str):
    """
    创建一个新的 changelist，并返回 changelist 号
    """
    template = subprocess.run(
        [P4, "change", "-o"],
        capture_output=True,
        text=True,
        check=True,
        env=os.environ
    ).stdout

    new_spec = template.replace("<enter description here>", description)

    result = subprocess.run(
        [P4, "change", "-i"],
        input=new_spec,
        capture_output=True,
        text=True,
        check=True,
        env=os.environ
    )

    output = result.stdout.strip()

    if output.startswith("Change"):
        return output.split()[1]

    raise RuntimeError(f"创建 changelist 失败: {output}")


def p4_reconcile(path: str, client: str = None) -> str:
    # 设置环境变量
    os.environ["P4PORT"] = "p4-world.funplus.com.cn:1666"
    os.environ["P4USER"] = "worldx_robot"

    if client:
        os.environ["P4CLIENT"] = client
    elif not os.environ.get("P4CLIENT"):
        print("错误：未指定工作区 (--client)，且环境变量中没有 P4CLIENT。")
        sys.exit(1)

    # 统一路径格式
    path = os.path.normpath(path)

    # 自动补上 \...
    if not path.endswith("..."):
        path = os.path.join(path, "...")

    # ---------------------------
    # 🔄 1. Refresh：先 sync 一次
    # ---------------------------
    print("执行 refresh (p4 sync)...")
    subprocess.run(
        [P4, "sync", "-f", path],
        text=True,
        env=os.environ
    )

    # ---------------------------
    # 2. 创建 changelist
    # ---------------------------
    description = f"p4-bypass xrobot ver_0.01 to release sync path : {path}"
    change_num = create_changelist(description)
    print(f"新建 changelist: {change_num}")

    # ---------------------------
    # 3. 执行 reconcile
    # ---------------------------
    try:
        result = subprocess.run(
            [P4, "reconcile", "-c", change_num, path],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )

        print("Reconcile 成功！输出如下：")
        print(result.stdout)

        opened = subprocess.run(
            [P4, "opened", "-c", change_num],
            capture_output=True,
            text=True,
            env=os.environ
        )

        print(f"Changelist {change_num} 内容：")
        print(opened.stdout)

    except subprocess.CalledProcessError as e:
        print("Reconcile 失败！")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)

    return change_num


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="调用 p4 reconcile 并放入新建 changelist")
    parser.add_argument("path", help="要 Reconcile 的文件夹路径 (本地路径)")
    parser.add_argument("--client", help="Perforce 工作区名 (P4CLIENT)，可选")

    args = parser.parse_args()
    p4_reconcile(args.path, args.client)

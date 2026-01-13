import subprocess
import sys
import os
import argparse

P4 = r"C:\Program Files\Perforce\p4.exe"

def create_changelist(description: str, workspace: str):
    """
    创建一个新的 changelist，并返回 changelist 号
    """
    try:
        # 获取 changelist 模板
        template = subprocess.run(
            [P4, "-c", workspace, "change", "-o"],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        ).stdout
    except subprocess.CalledProcessError as e:
        print(f"获取 changelist 模板失败（workspace: {workspace}）")
        print(e.stderr or e.stdout)
        raise

    # 替换描述
    new_spec = template.replace("<enter description here>", description)

    try:
        # 创建 changelist
        result = subprocess.run(
            [P4, "-c", workspace, "change", "-i"],
            input=new_spec,
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
    except subprocess.CalledProcessError as e:
        print("创建 changelist 失败")
        print(e.stderr or e.stdout)
        raise

    output = result.stdout.strip()

    if output.startswith("Change"):
        return output.split()[1]

    raise RuntimeError(f"创建 changelist 失败: {output}")

def show_status(path: str):
    """
    打印指定路径下的 Perforce 本地变更状态（新增、修改、删除）
    不返回任何变量
    """
    path = os.path.normpath(path)
    if not path.endswith("..."):
        path = os.path.join(path, "...")

    try:
        result = subprocess.run(
            [P4, "status", path],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        output = result.stdout.strip()
        if output:
            print("检测到以下本地变更：")
            print(output)
        else:
            print("没有检测到本地变更。")

    except subprocess.CalledProcessError as e:
        print("获取状态失败！")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)



def p4_reconcile(path: str, client: str = None, one: bool = False, changelist_num: str = None) -> str:
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
    show_status(path)
    # # ---------------------------
    # # 🔄 1. Refresh：先 sync 一次
    # # ---------------------------
    # print("执行 refresh (p4 sync)...")
    # subprocess.run(
    #     [P4, "sync", "-f", path],
    #     text=True,
    #     env=os.environ
    # )

    # ---------------------------
    # 2. 创建 changelist
    # ---------------------------
    description = f"p4-bypass p4-admin-bypass xrobot ver_0.01 to release sync path : {path}"
    if one:
        change_num = changelist_num
    else:
        change_num = create_changelist(description,client)
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

    show_status(path)
    return change_num


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="调用 p4 reconcile 并放入新建 changelist")
    parser.add_argument("path", help="要 Reconcile 的文件夹路径 (本地路径)")
    parser.add_argument("--client", help="Perforce 工作区名 (P4CLIENT)，可选")

    args = parser.parse_args()
    p4_reconcile(args.path, args.client)

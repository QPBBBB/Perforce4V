import subprocess
import sys
import os
import argparse

P4 = r"C:\Program Files\Perforce\p4.exe"

def p4_submit(worldspace: str, change_num: str, client: str = None):
    """
    使用 p4 submit 提交指定 changelist
    """

    # 固定服务器和用户
    os.environ["P4PORT"] = "p4-world.funplus.com.cn:1666"
    os.environ["P4USER"] = "worldx_robot"

    # 设置 client
    if client:
        os.environ["P4CLIENT"] = client
    elif not os.environ.get("P4CLIENT"):
        print("错误：未指定工作区 (--client)，且环境变量中没有 P4CLIENT。")
        sys.exit(1)

    # -----------------------------
    # 🔄 1. 提交前先 revert 未修改文件
    # -----------------------------
    print(f"Reverting unchanged files in changelist {change_num} ...")

    try:
        revert_result = subprocess.run(
            [P4, "revert", "-a", "-c", change_num],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        print("Revert unchanged files 输出：")
        print(revert_result.stdout)
    except subprocess.CalledProcessError as e:
        print("Revert unchanged files 失败：")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        # 不退出，让用户决定是否继续
        # sys.exit(1)

    # -----------------------------
    # 2. 构造提交描述
    # -----------------------------
    description = f"p4-bypass Worldspace:{worldspace} Change:{change_num}"

    # 获取 changelist spec
    try:
        spec = subprocess.run(
            [P4, "change", "-o", change_num],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        ).stdout
    except subprocess.CalledProcessError as e:
        print("获取 changelist 失败：", e.stderr)
        sys.exit(1)

    # 替换描述
    new_spec = []
    for line in spec.splitlines():
        if line.startswith("Description:"):
            new_spec.append("Description:\n\t" + description)
        else:
            new_spec.append(line)
    new_spec_text = "\n".join(new_spec)

    # 更新 changelist 描述
    try:
        subprocess.run(
            [P4, "change", "-i"],
            input=new_spec_text,
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
    except subprocess.CalledProcessError as e:
        print("更新 changelist 描述失败：", e.stderr)
        sys.exit(1)

    # -----------------------------
    # 3. 提交 changelist
    # -----------------------------
    try:
        result = subprocess.run(
            [P4, "submit", "-c", change_num],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        print("提交成功！输出如下：")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("提交失败！")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动提交指定 changelist")
    parser.add_argument("worldspace", help="worldspace 名称")
    parser.add_argument("change", help="要提交的 changelist 单号")
    parser.add_argument("--client", help="Perforce 工作区名 (P4CLIENT)，可选")

    args = parser.parse_args()
    p4_submit(args.worldspace, args.change, args.client)

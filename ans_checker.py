import os
import sys
import subprocess
import tkinter
import tkinter.filedialog
from collections import deque
import json
"""
0.Jupyterがインストールされていることが前提
1.変換元のipynbを選択する
2.実行場所に変換したファイルが生成される
"""


def ipynbconvert():
    # 初回テンプレート作成
    if not os.path.isfile("outonly.tpl"):
        print("テンプレートファイルを作成します")
        with open("./outonly.tpl", mode="w", encoding="utf-8") as f:
            data = """
{% extends 'display_priority.tpl' %}
{%- block header -%}
SUBMIT
{% endblock header %}

{% block in_prompt %}
INPUT```
{{cell.source}}
```
{%- endblock in_prompt %}

{% block output_prompt %}
{%- endblock output_prompt %}

{%- block input %}
{% endblock input %}

{% block error %}
{% endblock error %}

{% block traceback_line %}
{{ line | indent | strip_ansi }}
{% endblock traceback_line %}

{% block execute_result %}
{% block data_priority scoped %}
{{ super() }}
{%- endblock %}
{%- endblock execute_result%}

{% block stream %}
OUTPUT```
{{output.text}}
```
{% endblock stream %}

{% block data_text scoped %}
OUTPUT```
{{ output.data['text/plain']  }}
```
{% endblock data_text %}

{% block markdowncell scoped %}
{%- if "課題" in cell.source.split("\\n")[0] -%}
BLOCK
{{cell.source.split("\\n")[0]}}
{% endif %}
{%- endblock markdowncell %}



{% block data_html scoped %}
{{ output.data['text/html'] }}
{% endblock data_html %}

{% block data_markdown scoped %}
{{ output.data['text/markdown'] }}
{% endblock data_markdown %}

{% block unknowncell scoped %}
unknown type  {{ cell.type }}
{% endblock unknowncell %}
            """
            f.write(data)
            print("作成しました")

    # ファイル選択ダイアログの表示
    root = tkinter.Tk()
    root.withdraw()
    filetype = [("", "*.ipynb")]
    origin_file = tkinter.filedialog.askopenfilename(
        filetypes=filetype, initialdir="./")

    if origin_file == "":
        print("ファイル未入力")
        sys.exit()

    # 変換処理
    proc = subprocess.run(["jupyter", "nbconvert", "--to", "markdown",
                           origin_file, "--template=outonly.tpl", "--stdout"], stdout=subprocess.PIPE)

    convert_out = proc.stdout.decode("utf8")
    if convert_out[:6] != "SUBMIT":
        print("変換失敗")
        sys.exit()
    else:
        # このままだとまずそう
        return convert_out.split("\n")


def read_input(f):
    s = ""
    for l in f:
        if l == "```":
            break
        s += l+"\n"
    return s


def read_output(f):
    s = ""
    for l in f:
        if l == "```":
            break
        if l == "":
            # 空行は無視
            continue
        s += l+"\n"
    return s


def make_block(f_queue):
    block_dict = {"input": "", "output": ""}
    # inputを取得
    while True:
        if not f_queue:
            break
        line = f_queue.popleft()

        if line == "INPUT```":
            block_dict["input"] += read_input(f_queue)
        if line == "OUTPUT```":
            block_dict["output"] += read_output(f_queue)
        if line == "BLOCK":
            f_queue.appendleft(line)
            break

    return block_dict

# 入力データから入出力データを作成


def make_dict(conv_data):
    input_dict = dict()
    f_queue = deque(conv_data)

    while True:
        if not f_queue:
            break
        line = f_queue.popleft()

        if line == "\n":
            continue
        if line == "BLOCK":
            # 課題ブロックの作成
            title = f_queue.popleft()
            block_dict = make_block(f_queue)

            input_dict[title] = block_dict
    return input_dict


def load_model_data():
    print("模範解答のipynbを入力")
    model_data = ipynbconvert()
    model_dict = make_dict(model_data)
    with open("./modelanswer.json", mode="w", encoding="utf-8") as f:
        json.dump(model_dict, f, indent=4, ensure_ascii=False)


def load_submit_data():
    print("提出されたファイルを選択")
    submit_data = ipynbconvert()
    submit_dict = make_dict(submit_data)
    return submit_dict


# まだ
def compare(data1, data2):
    keys = data1.keys()
    q_num = len(keys)
    match_num = 0
    for k in keys:
        # 比較
        if data1[k]["output"] == data2[k]["output"]:
            # 柔軟な比較ができるか？
            match_num += 1
    print(f"{match_num}/{q_num}")


if __name__ == "__main__":
    if not os.path.isfile("./modelanswer.json"):
        load_model_data()

    with open("./modelanswer.json", mode="r", encoding="utf-8") as f:
        model_dict = json.load(f)
    submit_dict = load_submit_data()
    compare(model_dict, submit_dict)

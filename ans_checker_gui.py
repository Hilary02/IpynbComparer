import os
import tkinter as tk
import tkinter.filedialog
import json
import subprocess
import make_dict

left_data = None
right_data = None


def log(s):
    logarea.insert("end", f"{s}\n")


def ipynb2splitlist(file_path):

    # 初回テンプレート作成
    if not os.path.isfile("outonly.tpl"):
        log("テンプレートファイルを作成します")
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
            log("作成しました")

    # 変換処理
    proc = subprocess.run(["jupyter", "nbconvert", "--to", "markdown",
                           file_path, "--template=outonly.tpl", "--stdout"], stdout=subprocess.PIPE)

    convert_out = proc.stdout.decode("utf8")
    if "SUBMIT" in convert_out:
        return True, convert_out.split("\n")
    else:
        return False, []


def selectfile2dict(file_path):
    if os.path.splitext(file_path)[-1] == ".ipynb":
        b, split_li = ipynb2splitlist(file_path)
        if b == False:
            return False
        kadai_dict = make_dict.make_dict(split_li)
        return kadai_dict

    elif os.path.splitext(file_path)[-1] == ".json":
        with open(file_path, mode="r", encoding="utf-8") as f:
            kadai_dict = json.load(f)
        return kadai_dict
    return False


def make_model_data():
    log("模範解答を選択してください")
    file_path = tk.filedialog.askopenfilename(
        filetypes=[("模範解答", "*.ipynb")], initialdir="./")

    model_dict = selectfile2dict(file_path)
    if not model_dict:
        log("模範解答の処理に失敗しました")
    else:
        with open("./modelanswer.json", mode="w", encoding="utf-8") as f:
            json.dump(model_dict, f, indent=4, ensure_ascii=False)
            log("modelanswer.jsonを保存しました")


def file_select_f1():
    global left_data
    log("左に表示するデータを選択")
    file_path = tk.filedialog.askopenfilename(
        filetypes=[("Jupyter", "*.ipynb"), ("Json", "*.json")], initialdir="./")
    kadai_dict = selectfile2dict(file_path)

    if kadai_dict:
        file_name = file_path.split("/")[-1]
        f1la1["text"] = f"ファイル名：{file_name}"
        left_data = kadai_dict
        log("読み込み成功")
        selector_reset()
        compare()
    else:
        log("読み込み失敗")


def file_select_f2():
    global right_data
    log("右に表示するデータを選択")
    file_path = tk.filedialog.askopenfilename(
        filetypes=[("Jupyter", "*.ipynb"), ("Json", "*.json")], initialdir="./")
    kadai_dict = selectfile2dict(file_path)

    if kadai_dict:
        file_name = file_path.split("/")[-1]
        f2la1["text"] = f"ファイル名：{file_name}"
        right_data = kadai_dict
        log("読み込み成功")
        compare()
    else:
        log("読み込み失敗")


def selector_reset():
    for i in range(selector.size()):
        selector.delete(tk.END)
    for k in left_data.keys():
        selector.insert(tk.END, k)


def kadai_selected(event):
    if len(selector.curselection()) == 0:
        return
    i = selector.curselection()

    if not left_data:
        log("左側のデータが未選択")
        return

    f1tx1.delete("1.0", "end")
    f1tx1.insert("end", left_data[selector.get(i)]["input"])
    f1tx2.delete("1.0", "end")
    f1tx2.insert("end", left_data[selector.get(i)]["output"])

    if not right_data:
        log("右側のデータが未選択")
        return

    f2tx1.delete("1.0", "end")
    f2tx1.insert("end", right_data[selector.get(i)]["input"])
    f2tx2.delete("1.0", "end")
    f2tx2.insert("end", right_data[selector.get(i)]["output"])


def compare():
    if not left_data or not right_data:
        return False

    keys = left_data.keys()
    q_num = len(keys)
    match_list = [False]*q_num
    match_num = 0
    score.delete("1.0", "end")

    try:
        for i, k in enumerate(keys):
            if left_data[k]["output"] == right_data[k]["output"]:
                # 柔軟な比較ができるか？
                match_num += 1
                match_list[i] = True
    except Exception as e:
        log("左右の形式が一致しません")
        return False

    score.insert("end", f"{match_num}/{q_num}")

    colors = ("red", "green")
    for i, b in enumerate(match_list):
        selector.itemconfigure(i, foreground="white", background=colors[b])
    return f"{match_num}/{q_num}"


# dousiyo
if __name__ == "__main__":
    root = tk.Tk()
    root.title("nbcompare")
    root.geometry("1200x600")

    # 左課題表示画面
    f1 = tk.Frame(root, relief=tk.GROOVE, bd=2)
    f1la1 = tk.Label(f1, text="ファイル名")
    f1la1.grid(row=0, column=0, padx=2, pady=2, sticky=tk.N + tk.W)
    # ボタン
    f1bt1 = tkinter.Button(f1, text="ファイル選択", command=file_select_f1)
    f1bt1.grid(row=0, column=1, padx=2, pady=2, sticky=tk.N + tk.E)

    f1la2 = tk.Label(f1, text="コード")
    f1la2.grid(row=1, column=0, padx=2, pady=2, columnspan=2, sticky=tk.W)
    f1tx1 = tk.Text(f1, padx=5, pady=5, width=60,
                    height=15, font=('Consolas', 11))
    f1tx1.grid(row=2, column=0, padx=2, pady=2, columnspan=2)
    f1la3 = tk.Label(f1, text="出力")
    f1la3.grid(row=3, column=0, padx=2, pady=2, columnspan=2, sticky=tk.W)
    f1tx2 = tk.Text(f1, padx=5, pady=5, width=50,
                    height=8, font=('Consolas', 12))
    f1tx2.grid(row=4, column=0, padx=2, pady=2,
               columnspan=2, sticky=tk.N + tk.W)

    f1.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # 中央課題表示画面
    f2 = tk.Frame(root, relief=tk.GROOVE, bd=2)
    f2la1 = tk.Label(f2, text="ファイル名")
    f2la1.grid(row=0, column=0, padx=2, pady=2, sticky=tk.N + tk.W)
    # ボタン
    f2bt1 = tkinter.Button(f2, text="ファイル選択", command=file_select_f2)
    f2bt1.grid(row=0, column=1, padx=2, pady=2, sticky=tk.N + tk.E)

    f2la2 = tk.Label(f2, text="コード")
    f2la2.grid(row=1, column=0, padx=2, pady=2, columnspan=2, sticky=tk.W)
    f2tx1 = tk.Text(f2, padx=5, pady=5, width=60,
                    height=15, font=('Consolas', 11))
    f2tx1.grid(row=2, column=0, padx=2, pady=2, columnspan=2)
    f2la3 = tk.Label(f2, text="出力")
    f2la3.grid(row=3, column=0, padx=2, pady=2, columnspan=2, sticky=tk.W)
    f2tx2 = tk.Text(f2, padx=5, pady=5, width=50,
                    height=8, font=('Consolas', 12))
    f2tx2.grid(row=4, column=0, padx=2, pady=2,
               columnspan=2, sticky=tk.N + tk.W)

    f2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # 右情報表示画面
    f3 = tk.Frame(root, bd=2)
    f3la1 = tk.Label(f3, text="課題一覧")
    f3la1.pack(side=tk.TOP)
    # 課題選択リストの作成
    selector = tkinter.Listbox(f3, selectmode=tkinter.SINGLE)
    selector.insert(0, "選択なし")
    selector.bind('<<ListboxSelect>>', kadai_selected)
    selector.pack(side=tk.TOP, fill=tk.X, expand=0)
    f3la2 = tk.Label(f3, text="一致率")
    f3la2.pack(side=tk.TOP)
    score = tk.Text(f3, padx=5, pady=5, width=20,
                    height=1, font=('Consolas', 18))
    score.pack(side=tk.TOP)
    f3la3 = tk.Label(f3, text="ログ")
    f3la3.pack(side=tk.TOP)
    logarea = tk.Text(f3, padx=5, pady=5, width=30,
                      height=20, font=('Consolas', 9))
    logarea.pack(side=tk.TOP)
    f3.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # 初回入力処理
    if not os.path.isfile("./modelanswer.json"):
        log("模範回答データがありません")
        make_model_data()

    # 自動読み込み
    try:
        log("模範回答データを読み込みます")
        with open("./modelanswer.json", mode="r", encoding="utf-8") as f:
            left_data = json.load(f)
            f1la1["text"] = "ファイル名：modelanswer.json"
            selector_reset()
    except Exception as e:
        log("模範回答データが見つかりません")

    file_select_f2()

    root.mainloop()

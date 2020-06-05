import os
import tkinter as tk
import tkinter.filedialog
import json
import subprocess
import make_dict


def ipynb2splitlist(file_path):

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

    # 変換処理
    proc = subprocess.run(["jupyter", "nbconvert", "--to", "markdown",
                           file_path, "--template=outonly.tpl", "--stdout"], stdout=subprocess.PIPE)

    convert_out = proc.stdout.decode("utf8")
    if convert_out[:6] == "SUBMIT":
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


def file_select_f1():
    file_path = tk.filedialog.askopenfilename(
        filetypes=[("Jupyter", "*.ipynb"), ("Json", "*.json")], initialdir="./")
    kadai_dict = selectfile2dict(file_path)

    if kadai_dict:
        file_name = file_path.split("/")[-1]
        f1la1["text"] = f"ファイル名：{file_name}"
        left_data = kadai_dict
    else:
        bef_text = f1la1["text"]
        f1la1["text"] = f"入力失敗：{file_name}"


def file_select_f2():
    origin_file = tk.filedialog.askopenfilename(
        filetypes=[("", "*.ipynb", ".json")], initialdir="./")

    if origin_file == "":
        print("ファイル未入力")
    file_name = origin_file.split("/")[-1]
    f2la1["text"] = f"ファイル名：{file_name}"


def kadai_selected(event):
    for i in selector.curselection():
        print(selector.get(i))
    f2tx1.delete("1.0", "end")
    f2tx1.insert("end", selector.get(i))


with open("./modelanswer.json", mode="r", encoding="utf-8") as f:
    model_dict = json.load(f)


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
f1tx1 = tk.Text(f1, padx=5, pady=5, width=60, height=15, font=('Consolas', 11))
f1tx1.grid(row=2, column=0, padx=2, pady=2, columnspan=2)
f1la3 = tk.Label(f1, text="出力")
f1la3.grid(row=3, column=0, padx=2, pady=2, columnspan=2, sticky=tk.W)
f1tx2 = tk.Text(f1, padx=5, pady=5, width=50, height=8, font=('Consolas', 12))
f1tx2.grid(row=4, column=0, padx=2, pady=2, columnspan=2, sticky=tk.N + tk.W)

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
f2tx1 = tk.Text(f2, padx=5, pady=5, width=60, height=15, font=('Consolas', 11))
f2tx1.grid(row=2, column=0, padx=2, pady=2, columnspan=2)
f2la3 = tk.Label(f2, text="出力")
f2la3.grid(row=3, column=0, padx=2, pady=2, columnspan=2, sticky=tk.W)
f2tx2 = tk.Text(f2, padx=5, pady=5, width=50, height=8, font=('Consolas', 12))
f2tx2.grid(row=4, column=0, padx=2, pady=2, columnspan=2, sticky=tk.N + tk.W)

f2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


# 右情報表示画面
f3 = tk.Frame(root, bd=2)
f3la1 = tk.Label(f3, text="課題一覧")
f3la1.pack(side=tk.TOP)
# 課題選択の作成
selector = tkinter.Listbox(f3, selectmode=tkinter.SINGLE)
colors = ('red', 'orange', 'yellow', 'green', 'blue', 'navy', 'purple')
for i, k in enumerate(model_dict.keys()):
    selector.insert(i, k)
    selector.itemconfigure(i, foreground='white', background=colors[i % 2])
selector.bind('<<ListboxSelect>>', kadai_selected)
selector.pack(side=tk.TOP, fill=tk.X, expand=0)
f3la2 = tk.Label(f3, text="一致率")
f3la2.pack(side=tk.TOP)
score = tk.Text(f3, padx=5, pady=5, width=20, height=3)
score.pack(side=tk.TOP)
f3.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


def insert(event):
    entry1.configure(state='normal')
    entry1.insert('end', 'hello')
    entry1.configure(state='readonly')


root.mainloop()

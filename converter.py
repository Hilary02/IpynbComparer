import os
import sys
import subprocess
import urllib.request
import tkinter
import tkinter.filedialog
"""
0.Jupyterがインストールされていることが前提
1.変換元のipynbを選択する
2.実行場所に変換したファイルが生成される
"""

# 初回テンプレート作成
if not os.path.isfile("outonly.tpl"):
    print("テンプレートファイルを作成します")
    with open("./outonly.tpl", mode="w", encoding="utf-8") as f:
        data = """
{% extends 'display_priority.tpl' %}

{% block in_prompt %}
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
{%- endblock execute_result
 %}

{% block stream %}
```
{{output.text}}
```
{% endblock stream %}

{% block data_text scoped %}
```
{{ output.data['text/plain']  }}
```
{% endblock data_text %}

{% block markdowncell scoped %}
{%- if "課題" in cell.source.split("\\n")[0] -%}
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
    sys.exit()

# 変換処理
subprocess.run(["jupyter", "nbconvert", "--to", "markdown",
                origin_file, "--template=outonly.tpl", f"--output-dir=./"])

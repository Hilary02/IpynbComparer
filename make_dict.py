import os
import subprocess
from collections import deque
import json


class ProblemFileReader():
    """
    課題ファイルを読み込み，課題とその回答部分を抜き出して返す
    """

    @staticmethod
    def split_ipynb(file_path):
        """
        引数に渡されたipynbを行ごとに分割して返す
        ipynbが処理できないとFalseを返す
        """

        # 初回テンプレート作成
        if not os.path.isfile("outonly.tpl"):
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

        # 変換処理
        proc = subprocess.run(["jupyter", "nbconvert", "--to", "markdown",
                               file_path, "--template=outonly.tpl", "--stdout"], stdout=subprocess.PIPE)

        convert_out = proc.stdout.decode("utf8")

        if "SUBMIT" in convert_out:
            return True, convert_out.split("\n")
        else:
            return False, []

    @staticmethod
    def makedict(file_path):
        """
        ipynbまたはjsonを読み込み，辞書形式にして返す
        jsonならそのまま辞書に．ipynbは一度変換してから処理．
        """
        if os.path.splitext(file_path)[-1] == ".ipynb":
            b, splited_prob = ProblemFileReader.split_ipynb(file_path)
            if b == False:
                return False
            problem_dict = DictConverter.convert(splited_prob)
            return problem_dict

        elif os.path.splitext(file_path)[-1] == ".json":
            with open(file_path, mode="r", encoding="utf-8") as f:
                problem_dict = json.load(f)
            return problem_dict
        return False


class DictConverter():
    """
    課題と回答が抽出されたリストを解析して辞書型にまとめる
    """
    @staticmethod
    def get_input(f):
        s = ""
        for l in f:
            if l == "```":
                break
            s += l+"\n"
        return s

    @staticmethod
    def get_output(f):
        s = ""
        for l in f:
            if l == "```":
                break
            if l == "":
                # 空行は無視
                continue
            s += l.rstrip(" ")+"\n"
        return s

    @staticmethod
    def make_block(f_queue):
        block_dict = {"input": "", "output": ""}
        # inputを取得
        while True:
            if not f_queue:
                break
            line = f_queue.popleft()

            if line == "INPUT```":
                block_dict["input"] += DictConverter.get_input(f_queue)
            if line == "OUTPUT```":
                block_dict["output"] += DictConverter.get_output(f_queue)
            if line == "BLOCK":
                f_queue.appendleft(line)
                break

        return block_dict

    @staticmethod
    def convert(conv_data):
        """
        スプリットされたデータから辞書を作成
        """
        problem_dict = dict()
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
                block_dict = DictConverter.make_block(f_queue)

                problem_dict[title] = block_dict
        return problem_dict

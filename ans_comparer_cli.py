import json
from make_dict import ProblemFileReader
from argparse import ArgumentParser


def make_model_data(file_path):
    print("modelanswer.jsonを更新します")
    model_dict = ProblemFileReader.makedict(file_path)

    if model_dict:
        with open("./modelanswer.json", mode="w", encoding="utf-8") as f:
            json.dump(model_dict, f, indent=4, ensure_ascii=False)
            print("modelanswer.jsonを更新しました")
    else:
        print("模範解答の処理に失敗しました")


def strip_margin(s):
    """
    文字列の各行から空白，空行などを除去した文字列を返す
    """
    strip_str = ""
    for l in s.split("\n"):
        strip_line = l.strip(" '\"")
        if strip_line:
            strip_str += l.strip(" '\"") + "\n"

    return strip_str


def loose_compare(str1, str2):
    strip_str1 = strip_margin(str1)
    strip_str2 = strip_margin(str2)
    return strip_str1 == strip_str2


def strict_compare(str1, str2):
    return str1 == str2


def compare(data1, data2, is_strict):
    if not data1 or not data2:
        return False

    keys = data1.keys()
    q_num = len(keys)
    match_list = [False]*q_num
    match_num = 0

    compare_method = loose_compare
    if is_strict:
        compare_method = strict_compare

    try:
        for i, k in enumerate(keys):
            if compare_method(data1[k]["output"], data2[k]["output"]):
                match_num += 1
                match_list[i] = True

    except Exception as e:
        print("左右の形式が一致しません")
        return False

    return f"{match_num}"


def parser():
    argparser = ArgumentParser(
        prog=__file__, usage="python %(prog)s fname [--model <file>] [--help] [--strict]")
    argparser.add_argument("fname", type=str, help="比較対象ファイル[.ipynb]")
    argparser.add_argument("-m", "--model", type=str,
                           dest="model_file", help="模範解答ファイル[.ipynb | .json] 未入力のとき前回のものと比較")
    argparser.add_argument("-s", "--strict",
                           action="store_true",
                           help="回答を文字の完全一致で比較 default:空白や空行を無視")

    args = argparser.parse_args()

    if args.model_file:
        # 模範解答ファイルが新規入力された
        make_model_data(args.model_file)

    submit_dict = ProblemFileReader.makedict(args.fname)
    model_dict = ProblemFileReader.makedict("modelanswer.json")
    result = compare(submit_dict, model_dict, args.strict)
    print("file name,result")
    print(f"{args.fname},{result}")


if __name__ == "__main__":
    parser()
    pass

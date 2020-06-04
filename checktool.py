from collections import deque
import json
# 模範解答から解凍データを作成
# 記録しておく


def read_input(f):
    s = ""
    for l in f:
        if l == "```":
            break
        s += l
    return s


def read_output(f):
    s = ""
    for l in f:
        if l == "```":
            break
        if l == "\n":
            # 空行は無視
            continue
        s += l
    return s


def make_block(f_queue):
    block_dict = dict("input": "", "output": "")
    # inputを取得
    while True:
        if f_queue.empty():
            break
        line = f_queue.pop()

        if line == "INPUT```":
            dict["input"] = read_input()
        if line == "OUTPUT```":
            dict["output"] = read_output()
        if line == "BLOCK":
            f_queue.appendleft(line)
            break

    return block_dict

# 入力データから入出力データを作成


def make_json():
    with open("",) as f:
        input_dict = dict()
        f_queue = deque(f.readlines())

        while:
            if f_queue.empty():
                break
            line = f_queue.pop()

            if line == "\n":
                continue
            if line == "BLOCK":
                # 課題ブロックの作成
                title = f_queue.pop()
                block_dict = make_block(f_queue)

                input_dict[title] = block_dict


def diff(submit: dict):
    data1 = model
    data2 = submit

    q_num = 9
    keys = data1.keys()
    match_num = 0
    for k in keys:
        # 比較
        if data1[k][output] == data2[k][output]:
            # 柔軟な比較ができるか？
            match_num += 1
    print(f"{match_num}/{q_num}")


if __name__ == "__main__":
    # 模範解答作成
    if not os.path.isfile("modelanswer.json"):
        print("模範回答のipynbを入力してください")

    with open('./modelanswer.json') as f:
        model = json.load(f)

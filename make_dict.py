from collections import deque


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

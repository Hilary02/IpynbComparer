from collections import deque


class DictConverter():
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

# -*- coding: utf-8 -*-
import re
import string
import fitz
import utils
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder

# print(fitz.__doc__)

# 书签信息
# tocs=doc.get_toc()
# for toc in tocs:
#     print(toc)

reverse_dict = {}


class Text_font_info:
    """
    pdf的text的信息类
        """
    # 动态映射字典  类共享变量
    forward_dict = {}

    def __init__(self, text, font_size, is_bold):
        self.text = text
        self.font_size = font_size
        self.is_bold = is_bold

    # 动态映射
    def set_mapping(self):
        """
        设置双向动态映射dict
        @return:
        """
        key = (self.font_size, self.is_bold)
        if key not in Text_font_info.forward_dict:
            value = alphabet_list[len(Text_font_info.forward_dict) % len(alphabet_list)]  # todo:避免报错的写法后期更换
            # Text_font_info.mapping_dict[key] = f"Map{len(Text_font_info.mapping_dict) + 1}"
            Text_font_info.forward_dict[key] = value
            reverse_dict[value] = key

    def get_forward_dict(self):
        """

        @return:
        """
        key = (self.font_size, self.is_bold)
        return Text_font_info.forward_dict[key]


def get_reverse_dict(flag):
    """

    @return:
    """
    return reverse_dict[flag]


def extract_text_font_info(pdf_path):
    """
    从 PDF 文件中提取pdf的text的信息类
    参数:
        file_path (str): PDF 文件的路径
    返回:
        list: 包含提取的pdf的text的信息类的列表
    """
    doc = fitz.Document(pdf_path)
    text_font_infos = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("dict", flags=11)["blocks"]
        for block in blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    font_size = span["size"]
                    font_name = span["font"]
                    is_bold = "bold" in font_name.lower()
                    text = span["text"]
                    text_font_infos.append(Text_font_info(text, font_size, is_bold))
                    # print(f'Text: {text}, Font: {font_name}, Size: {font_size}, Bold: {is_bold}')
    return text_font_infos


def merged_text_font_infos(text_font_infos):
    """
    将每一行的text相同字体信息的进行合并
    参数:
        text_font_infos (list)
    返回:
        list: 包含合并之后的pdf的text的信息类的列表
    """
    merged_data_list = []
    # 初始化字典来跟踪相同大小的文本块
    current_block = None
    # 遍历解析后的数据并将相同大小以及是否加粗的文本合并,同时设置map
    for data in text_font_infos:
        # 第一步需要检查当前data块的text是否为空，因为这样的text容易引发前后块的分割
        if data.text == ' ' or data.text == '  ':
            continue
        elif current_block is None:
            current_block = data
        # 合并size和bold一样的块
        elif data.font_size == current_block.font_size and data.is_bold == current_block.is_bold:
            current_block.text += data.text
        else:
            if current_block.text != ' ' and current_block.text != '  ':
                current_block.set_mapping()
                merged_data_list.append(current_block)
            current_block = data
    # 循环结束后处理最后一个 current_block
    if current_block and current_block.text != ' ' and current_block.text != '  ':
        merged_data_list.append(current_block)
    return merged_data_list


def sliding_window(input_str, window_size, step_size):
    """
    使用滑动窗口切分字符串为列表。
    @param input_str: (str) 输入的字符串。
    @param window_size: (int) 窗口的大小。
    @param step_size: (int) 滑动窗口的步长。
    @return: List[str] 切分后的字符串列表。
    """
    if window_size <= 0 or step_size <= 0:
        raise ValueError("窗口大小和步长应为正整数")
    # 使用列表推导式生成滑动窗口
    windows = [input_str[i:i + window_size] for i in range(0, len(input_str) - window_size + 1, step_size)]
    return windows


def judge_strs(input_strings):
    """
    判断是否符合标准进行筛选#todo:特殊规则设定?
    @param input_string: list string
    @return: list string
    """
    for input_string in input_strings:
        pre = reverse_dict.get(input_string[0])
        beh = reverse_dict.get(input_string[1])
        if pre[0] > beh[0]:
            pass
        elif pre[0] == beh[0]:
            if not pre[1] and beh[1]:
                input_strings.remove(input_string)
            else:
                pass
        else:
            input_strings.remove(input_string)


def judge_str(input_string):
    """
    判断是否符合标准进行筛选#todo:特殊规则设定?
    @param input_string:  string
    @return:  string
    """
    first = reverse_dict.get(input_string[0])
    second = reverse_dict.get(input_string[1])
    if first > second:
        return False
    else:
        return True


def find_start_positions(main_string, sub_string):
    """
    从字符串中查找子串的所有起始位置
    @param main_string: 主字符串
    @param sub_string: 要查找的子字符串
    @return: 包含所有子串起始位置的列表
    """
    start_positions = []
    # 设置起始搜索位置
    start_index = 0
    # 循环搜索子串
    while True:
        index = main_string.find(sub_string, start_index)
        if index == -1:
            break
        start_positions.append(index)
        start_index = index + 1
    return start_positions


if __name__ == "__main__":
    # self.text = text
    # self.font_size = font_size
    # self.is_bold = is_bold
    # 生成包含小写和大写字母的列表
    # alphabet_list = list(string.ascii_lowercase + string.ascii_uppercase)
    font_size_set = set([])
    alphabet_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                     'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                     'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    file_path = "日志参考1.pdf"
    # extract_text_font_infos
    text_font_infos = extract_text_font_info(file_path)
    # merge
    merged_data_list = merged_text_font_infos(text_font_infos)
    pdf_alphabet_str = ""
    print(f"合并文本块长度: {len(merged_data_list)}")
    for item in merged_data_list:
        item.set_mapping()
        pdf_alphabet_str += item.get_forward_dict()
        # print(f"字体大小{item.font_size}")
        # print(item.text)
        # print('\n' + '-' * 80)
    print("文本块的alphabet字符串：")
    print(pdf_alphabet_str)
    print('-' * 100)
    str_list = sliding_window(pdf_alphabet_str, window_size=3, step_size=1)
    # 筛除不符合条件的str
    # judge_strs(str_list)
    # 对于reverse_dict排序得到顺序
    sorted_reverse_dict_list = sorted(reverse_dict.keys(), key=lambda k: (reverse_dict[k][0], not reverse_dict[k][1]),
                                      reverse=True)
    print("文字块排序从大到小结果：")
    print(sorted_reverse_dict_list)
    print('-' * 100)

    # print(str_list)
    # 寻找频繁的3字母pattern
    converted_data = [[char for char in item] for item in str_list]

    print("切分以及筛查之后的数据集：")
    print(converted_data)
    print('-' * 100)

    te = TransactionEncoder()
    te_ary = te.fit(converted_data).transform(converted_data)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    frequent_patterns = fpgrowth(df, min_support=0.01, use_colnames=True)

    # print("fpgrowth挖掘结果：")
    # print(frequent_patterns[['itemsets', 'support']])
    # print('-'*100)

    frequent_patterns_item = frequent_patterns['itemsets'].tolist()
    frequent_patterns_support = frequent_patterns['support'].tolist()
    fp_result = {}
    for key, value in zip(frequent_patterns_item, frequent_patterns_support):
        key = ''.join(key)
        if 2 <= len(key) <= 3 and value >= 0.02:
            fp_result[key] = value
    fp_result = dict(sorted(fp_result.items(), key=lambda item: item[1], reverse=True))

    print("fpgrowth挖掘结果：")
    for item in fp_result:
        print(f"item:{item}   support score:{fp_result.get(item)}")
    print('-' * 100)

    keys_list = list(fp_result.keys())
    # todo:修改为更加合理的方式吗
    while True:
        substring = input()
        if substring == 'exit':
            break
        elif judge_str(substring):
            print("不符合大标题-小标题||正文格式")
            continue
        positions = find_start_positions(pdf_alphabet_str, substring)
        print(f"子串 '{substring}' 的起始位置为:", positions)
        for position in positions:
            if position + len(substring) < len(merged_data_list):
                print('-' * 80)
                for i in range(len(substring)):
                    print(merged_data_list[position + i].text)
        print('\n')



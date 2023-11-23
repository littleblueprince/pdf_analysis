# -*- coding: utf-8 -*-
import re
import string
import fitz
import utils


# print(fitz.__doc__)

# 书签信息
# tocs=doc.get_toc()
# for toc in tocs:
#     print(toc)


class Text_font_info:
    """
    pdf的text的信息类
        """
    # 动态映射字典  类共享变量
    mapping_dict = {}

    def __init__(self, text, font_size, is_bold):
        self.text = text
        self.font_size = font_size
        self.is_bold = is_bold
        if self.font_size not in font_size_set:
            font_size_set.add(self.font_size)

    # 动态映射
    def get_mapping(self):
        """
        动态映射
        @return:
        """
        key = (self.font_size, self.is_bold)
        if key not in Text_font_info.mapping_dict:
            # Text_font_info.mapping_dict[key] = f"Map{len(Text_font_info.mapping_dict) + 1}"
            Text_font_info.mapping_dict[key] = alphabet_list[len(Text_font_info.mapping_dict) + 1]
        return Text_font_info.mapping_dict[key]


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
                current_block.get_mapping()
                merged_data_list.append(current_block)
            current_block = data
    # 循环结束后处理最后一个 current_block
    if current_block and current_block.text != ' ' and current_block.text != '  ':
        merged_data_list.append(current_block)
    return merged_data_list


def find_repeated_patterns(s, min_length, start_char):
    """
    找到重复模式接口
    @param s:
    @param min_length:
    @return:
    """
    repeated_patterns = {}
    # 遍历所有可能的子字符串长度
    for pattern_length in range(min_length, len(s) // 2 + 1):
        pattern_counts = {}
        pattern_positions = {}
        # 遍历字符串，提取所有长度为 pattern_length 的子字符串
        for i in range(len(s) - pattern_length + 1):
            pattern = s[i:i + pattern_length]
            if pattern in pattern_counts:
                pattern_counts[pattern] += 1
                pattern_positions[pattern].append(i)
            else:
                pattern_counts[pattern] = 1
                pattern_positions[pattern] = [i]
        # 筛选出重复出现的模式
        for pattern, positions in pattern_positions.items():
            if pattern_counts[pattern] > 1 and pattern[0] is start_char:
                repeated_patterns[pattern] = positions
    return repeated_patterns


def find_top_k(input_set, k):
    # 将集合转换为列表，并按降序排序
    sorted_list = sorted(input_set, reverse=True)
    # 获取前 k 个元素
    top_k_elements = sorted_list[:k]
    return top_k_elements


def split_string_by_list(input_str, delimiters):
    """
    将输入字符串基于特定字符分割为字符串列表。
    @param input_str: 要分割的输入字符串
    @param delimiter: 分割字符串的特定字符
    @return: 字符串列表
    """
    if not input_str:
        return []
        # 使用 re 模块的 split 函数，通过正则表达式匹配任何一个分隔符
    pattern = '|'.join(map(re.escape, delimiters))
    result_list = re.split(pattern, input_str)
    # 移除可能的空字符串
    result_list = [item for item in result_list if item]
    return result_list


if __name__ == "__main__":
    # self.text = text
    # self.font_size = font_size
    # self.is_bold = is_bold
    # 生成包含小写和大写字母的列表
    # alphabet_list = list(string.ascii_lowercase + string.ascii_uppercase)
    font_size_set = set([])
    alphabet_list = ['@', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                     't',
                     'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                     'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    file_path = "示例.pdf"
    # extract_text_font_infos
    text_font_infos = extract_text_font_info(file_path)
    # merge
    merged_data_list = merged_text_font_infos(text_font_infos)
    pdf_alphabet_str = ""
    print(f"合并文本块长度: {len(merged_data_list)}")
    for item in merged_data_list:
        pdf_alphabet_str += item.get_mapping()
        # print(f"字体大小{item.font_size}")
        # print(item.text)
        # print('\n' + '-' * 80)

    print(pdf_alphabet_str)
    print(utils.has_adjacent_duplicates(pdf_alphabet_str))
    top_k_font_size_list = find_top_k(font_size_set, 3)
    print(top_k_font_size_list)
    # for item in merged_data_list:
    #     if item.font_size in top_k_font_size_list:
    #         print(item.text)

    # # 特定的字母
    # target_letters = {'f', 'g'}
    # # 保留特定字母的新字符串
    # filtered_str = ''.join(char for char in pdf_alphabet_str if char in target_letters)
    # print(filtered_str)

    delimiters = []
    for item in merged_data_list:
        if item.font_size in top_k_font_size_list and item.get_mapping() not in delimiters:
            delimiters.append(item.get_mapping())
    print(delimiters)
    result = split_string_by_list(pdf_alphabet_str, delimiters)
    print(result)

    # 抽取所有重复出现的模式（长度不确定）
    # repeated_patterns = find_repeated_patterns(filtered_str, 5, 'f')
    # for item in repeated_patterns:
    #     print(f"重复模式为:{item},其位置为:{repeated_patterns[item]}")
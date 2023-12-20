# -*- coding: utf-8 -*-
import pdfplumber
import fitz
from anytree import Node, RenderTree, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter, DotExporter
from anytree.importer import DictImporter
from ast import literal_eval


# print(fitz.__doc__)

# 书签信息
# tocs=doc.get_toc()
# for toc in tocs:
#     print(toc)


class Text_font_info:
    """
    pdf的text的信息类
        """

    def __init__(self, text, font_name, font_size, is_bold):
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.is_bold = is_bold
        self.flag = False


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
                    text_font_infos.append(Text_font_info(text, font_name, font_size, is_bold))
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
    # 遍历解析后的数据并将相同大小的文本合并
    for data in text_font_infos:
        if current_block is None:
            current_block = data
        elif data.font_size == current_block.font_size and data.is_bold == current_block.is_bold:
            current_block.text += data.text
        else:
            if current_block.text != ' ' and current_block.text != '  ':
                merged_data_list.append(current_block)
            current_block = data
    # 循环结束后处理最后一个 current_block
    if current_block and current_block.text != ' ' and current_block.text != '  ':
        merged_data_list.append(current_block)
    # for list in merged_data_list:
    #     print(list.text)
    #     print('-'*80)
    return merged_data_list


def extract_text_to_tree(file_path):
    """
    提取 PDF 文件中的文本内容，将其划分为树状结构
    参数:
        file_path (str): PDF 文件的路径
    返回:
        返回树的根节点(Node)
    """
    # 初始信息以及次数统计
    text_font_infos = extract_text_font_info(file_path)
    # merge
    merged_data_list = merged_text_font_infos(text_font_infos)
    # 提取
    root = Node(Text_font_info('pdf', "font_name", 999, True))
    current_data = None
    last_node = None
    for merged_data in merged_data_list:
        if current_data == None:  # 初始化
            current_data = Text_font_info(merged_data.text, merged_data.font_name, merged_data.font_size,
                                          merged_data.is_bold)
            last_node = Node(current_data, parent=root)
        else:
            current_data = Text_font_info(merged_data.text, merged_data.font_name, merged_data.font_size,
                                          merged_data.is_bold)
            if last_node.name.font_size > current_data.font_size:
                last_node = Node(current_data, parent=last_node)
            elif last_node.name.font_size == current_data.font_size:
                last_node = Node(current_data, parent=last_node.parent)
            else:  # 找不到下级,需要上级
                search_node = last_node.parent
                while search_node.parent != None and search_node.name.font_size <= current_data.font_size:
                    search_node = search_node.parent
                last_node = Node(current_data, parent=search_node)
        # print(merged_data.text)
        # print(merged_data.font_size)
        # print(merged_data.is_bold)
        # print('-' * 80)
    return root


# 辅助存储和读取的两个函数
def node_to_dict(node):
    # return {"text": node.text, "font_size": node.font_size, "is_bold": node.is_bold}
    return node.text


def dict_to_node(data):
    # return Text_font_info(data["text"], data["font_name"],data["font_size"], data["is_bold"])
    return data["text"]


def tree_to_txt(tree_root, filename):
    """
       将 PDF 树状结构信息存储到txt中
       参数:
            tree_root (Node) :根节点
            file_path (str): txt文件的路径
       返回:

       """
    exporter = DictExporter(
        attriter=lambda attrs: [(key, node_to_dict(value)) if key == 'name' else (key, value) for key, value in
                                attrs])

    tree_dict = exporter.export(tree_root)
    # print(tree_dict)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(tree_dict))


def txt_to_tree(filename):
    """
       从txt文件中读取出树文件
       参数:
            filename (str): txt文件的路径
       返回:

       """
    with open(filename, 'r', encoding='utf-8') as file:
        tree_str = file.read()
        tree_dict = literal_eval(tree_str)

    importer = DictImporter()

    tree_root = importer.import_(tree_dict)
    return tree_root


def get_tree_text_length(root_node):
    """
       获取某节点及其子节点的所有text总和长度
       参数:
            root_node (Text_font_info): 节点
       返回:
            长度
       """
    text_length = 0
    for node in PreOrderIter(root_node):
        text_length = text_length + len(node.name.text)
    return text_length


def find_body_font_size(root_node):
    """
           遍历树然后查找最多字符出现的字体大小
           参数:
                root_node (Text_font_info): 节点
           返回:
                body_font_size  正文字体大小
           """
    font_size_dict = {}
    for node in PreOrderIter(root_node):
        if node.name.font_size in font_size_dict:
            font_size_dict[node.name.font_size] = len(node.name.text) + font_size_dict[node.name.font_size]
        else:
            font_size_dict[node.name.font_size] = len(node.name.text)
    max_font_size = None  # 初始化一个变量来保存最大值
    max_font_size_key = None  # 初始化一个变量来保存最大值对应的键
    for key, font_size in font_size_dict.items():
        if max_font_size is None or font_size > max_font_size:
            max_font_size = font_size
            max_font_size_key = key
    return max_font_size_key


def set_special_flag(root_node, body_font_size):
    """
           寻找特殊的重复出现的标题
           参数:
                root_node (Text_font_info): 节点
                body_font_size (double) :正文字体
           返回:
           """
    # 在每一层中查找重复出现的text
    for children in LevelOrderGroupIter(root):
        font_text_count = {}
        # 第一次遍历统计次数
        for child in children:
            if child.name.text in font_text_count:
                font_text_count[child.name.text] = 1 + font_text_count[child.name.text]
            else:
                font_text_count[child.name.text] = 1
        # 第二次遍历对flag进行标记
        for child in children:
            if font_text_count.get(child.name.text) > 1 and child.name.font_size > body_font_size:
                child.name.flag = True


def traverse_upwards(node):
    """
            参数:
                    node (Text_font_info): 节点
            返回:
            """
    if node.parent is not None:
        if node.parent.name.flag == False:
            node.parent.name.flag = True
        traverse_upwards(node.parent)


def set_normal_flag(root_node):
    """
           参数:
                root_node (Text_font_info): 节点
           返回:
           """
    # 层序遍历
    for children in LevelOrderGroupIter(root):
        for child in children:
            if child.name.flag:
                traverse_upwards(child)


def canonical_tree(root_node, body_font_size):
    """
           参数:
                root_node (Text_font_info): 节点
                body_font_size (double) :正文字体
           返回:
           """
    # 层序遍历
    for children in LevelOrderGroupIter(root_node):
        for child in children:
            if child.name.flag is False and child.name.font_size < body_font_size:
                child.parent = None


if __name__ == "__main__":
    # self.text = text
    # self.font_name = font_name
    # self.font_size = font_size
    # self.is_bold = is_bold

    root = extract_text_to_tree('关于发布本市建设工程概算相关费率的通知 沪建标定联[2023]486号（含附件）.pdf')
    # for pre, _, node in RenderTree(root):
    #     print(f"{pre}{node.name.text} {node.name.font_size}")
    get_tree_text_length(root)

    body_font_size = find_body_font_size(root)
    set_special_flag(root, body_font_size)
    set_normal_flag(root)
    canonical_tree(root, body_font_size)

    # 渲染展示整个树结构
    tree = RenderTree(root)
    for pre, fill, node in RenderTree(root):
        print(f"{pre}{node.name.text}")

    # 存储到txt
    tree_to_txt(root, 'tree.txt')

    # 从txt文件读取
    loaded_tree = txt_to_tree('tree.txt')

    # 渲染树
    # tree_str = "\n".join([f"{pre}{node.name.text}  {node.name.font_size}  {node.name.is_bold}" for pre, fill, node in
    #                       RenderTree(root)])
    tree_str = "\n".join([f"{pre}{node.name.text}" for pre, fill, node in
                          RenderTree(root)])

    # 将渲染结果保存到文件
    with open("RenderTree.txt", "w", encoding='utf-8') as file:
        file.write(tree_str)

    # 将树存储为DOT格式
    # dot_exporter = DotExporter(root)
    # dot_exporter.to_dotfile('tree.dot')
    # dot_exporter.to_picture('tree.png') #todo:添加图片可视化存储

    # for pre, _, node in RenderTree(loaded_tree):
    #     print(f"{pre}{node.name}")

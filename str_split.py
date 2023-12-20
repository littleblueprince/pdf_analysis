# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 14:35
# @Author  : blue
# @Description :
# 读取txt的str然后根据滑动窗口分割为二维数组


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


input_file_path = 'output_pdf_str.txt'

try:
    with open(input_file_path, 'r') as file:
        file_content = file.read()
        print("txt的str内容:")
        print(file_content)
        # 指定保存到文本文件的路径
        output_file_path = 'character_array_W6.txt'
        input_strings = sliding_window(file_content, 5, 1)
        two_dimensional_array = [list(s) for s in input_strings]
        # 格式化字符串，添加空格和换行符
        formatted_string = '\n'.join([' '.join(row) for row in two_dimensional_array])
        # 将处理后的字符串保存到文本文件
        with open(output_file_path, 'w') as file:
            file.write(formatted_string)

        print(f"Processed string saved to {output_file_path}")

except FileNotFoundError:
    print(f"文件 '{input_file_path}' 未找到")
except Exception as e:
    print(f"出现错误{e}")

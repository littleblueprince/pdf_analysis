def merge_adjacent_duplicates(input_str):
    """
    将临近的重复字母合并
    @param input_str:
    @return:
    """
    merged_str = ""
    i = 0
    while i < len(input_str):
        merged_str += input_str[i]
        while i + 1 < len(input_str) and input_str[i] == input_str[i + 1]:
            i += 1
        i += 1
    return merged_str


def has_adjacent_duplicates(input_str):
    """
    检查字符串中是否存在相邻的重复字符  存在则返回True
    @param input_str:
    @return:
    """
    for i in range(len(input_str) - 1):
        if input_str[i] == input_str[i + 1]:
            return True
    return False

def get_values_in_range(input_list, start, end):
    """
    获取列表中从 start 到 end（包括 start 和 end）索引的元素。
    """
    if start < 0 or end >= len(input_list) or start > end:
        return "Invalid index range or list length."

    return input_list[start: end + 1]

if __name__ == "__main__":
    # 示例用法
    input_str = "bccdebfbfbfbgbggbgghggiijgggggggg"
    result = has_adjacent_duplicates(input_str)
    print(result)

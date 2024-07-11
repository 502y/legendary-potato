import os
import re


def extract_custom_headers_and_sources(header_file, included_files=None, included_sources=None):
    if included_files is None:
        included_files = set()
    if included_sources is None:
        included_sources = set()

    # 用于匹配非官方库的正则表达式
    custom_header_pattern = re.compile(r'#include\s+"(.+?)"')

    with open(header_file, 'r') as file:
        content = file.read()

    # 查找所有匹配的非官方库文件
    custom_headers = custom_header_pattern.findall(content)

    for header in custom_headers:
        # 如果该文件尚未处理，递归解析该文件
        if header not in included_files:
            header_path = os.path.join(os.path.dirname(header_file), header)
            included_files.add(header_path)
            if os.path.exists(header_path):
                extract_custom_headers_and_sources(header_path, included_files, included_sources)
            else:
                print(f"Warning: {header_path} does not exist.")

            # 尝试找到对应的实现文件
            source_file = os.path.splitext(header_path)[0] + '.c'
            if os.path.exists(source_file):
                included_sources.add(source_file)

    return included_files, included_sources

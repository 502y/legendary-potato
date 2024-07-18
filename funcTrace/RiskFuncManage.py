import re
import json

from funcTrace.AstTreeJson import AST_Tree_json
from funcTrace.CodeCheck import CppCheck
from utils.database.database_util import *

str_total = ""
num_high = 0
num_medium = 0
num_low = 0
str_high = ""
str_medium = ""
str_low = ""
num_unused = 0
str_unused = "无效函数列表：\n"
num_leak = 0
str_leak = "内存泄露函数列表：\n"
str_risk_h = "高风险函数列表：\n\t"
str_risk_m = "中风险函数列表：\n\t"
str_risk_l = "低风险函数列表：\n\t"

high_labels = []
medium_labels = []
low_labels = []
high_sizes = []
medium_sizes = []
low_sizes = []


class FunctionManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.db = Database()
        self.str_total = ""
        self.num_high = 0
        self.num_medium = 0
        self.num_low = 0
        self.str_high = ""
        self.str_medium = ""
        self.str_low = ""
        self.num_unused = 0
        self.str_unused = "无效函数列表：\n"
        self.num_leak = 0
        self.str_leak = "内存泄露函数列表：\n"
        self.str_risk_h = "高风险函数列表：\n\t"
        self.str_risk_m = "中风险函数列表：\n\t"
        self.str_risk_l = "低风险函数列表：\n\t"
        self.high_labels = []
        self.medium_labels = []
        self.low_labels = []
        self.high_sizes = []
        self.medium_sizes = []
        self.low_sizes = []

    def riskFunction(self):
        str_risk = ""
        all_threats = self.db.get_all_threat()
        global str_high
        global str_medium
        global str_low
        global num_high
        global num_medium
        global num_low
        global str_unused
        global num_unused
        global str_leak
        global num_leak
        global str_risk_h
        global str_risk_m
        global str_risk_l
        global high_labels
        global high_sizes
        global medium_labels
        global medium_sizes
        global low_labels
        global low_sizes
        for line in all_threats:
            if (line[1] == 0) or (line[1] == 1) or (line[1] == 2):
                num_total = 0
                if line[1] == 0:
                    num_total = num_high
                    str_high = ""
                if line[1] == 1:
                    num_total = num_medium
                    str_medium = ""
                if line[1] == 2:
                    num_total = num_low
                    str_low = ""
                self.generate_ast(self.file_path)
                self.analyze_ast(self.ast_instance, self.file_path, str(line[0]), line[1])
                if line[1] == 0:
                    if num_total < num_high:
                        high_labels.append(str(line[0]))
                        high_sizes.append(num_high - num_total)
                        str_risk_h = str_risk_h + str(line[0]) + ":\t" + str(line[2]) + "\n\t" + str_high + "\n\t"
                if line[1] == 1:
                    if num_total < num_medium:
                        medium_labels.append(str(line[0]))
                        medium_sizes.append(num_medium - num_total)
                        str_risk_m = str_risk_m + str(line[0]) + ":\t" + str(line[2]) + "\n\t" + str_medium + "\n\t"
                if line[1] == 2:
                    if num_total < num_low:
                        low_labels.append(str(line[0]))
                        low_sizes.append(num_low - num_total)
                        str_risk_l = str_risk_l + str(line[0]) + ":\t" + str(line[2]) + "\n\t" + str_low + "\n\t"

        checker = CppCheck(self.file_path).checkMemoryLeaks()
        if checker:
            for line in checker:
                if line is not None:
                    # pattern = r'"path": "(?P<path>(?:[a-zA-Z]:)?\\\\[^"]*(?:\\\\[^"]*)*)", "location": "(?P<location>\d+,\d+)", "content": "(?P<content>.+?),", "code": "(?P<code>.+?)"'
                    # match = re.match(pattern, str(line))
                    # if match:
                    #     path = match.group(1)
                    #     location_line = match.group(2)
                    #     location_column = match.group(3)
                    #     content = match.group(4)
                    # else:
                    #     path = None
                    #     location_line = None
                    #     location_column = None
                    #     content = None
                    message = str(line).replace("'", '"')
                    try:
                        data = json.loads(message)
                        path = data.get("path")
                        location = data.get("location")
                        content = data.get("content")
                        code = data.get("code")
                        location_parts = location.split(',')
                        location_line = str(location_parts[0])
                        location_column = str(location_parts[1])
                    except json.JSONDecodeError as e:
                        path = None
                        content = None
                        location_line = None
                        location_column = None

                    leak_unused_content = content
                    if leak_unused_content in leak_dict:
                        num_leak += 1
                        str_leak = str_leak + "位于 " + str(path) + " 文件\t第" + str(location_line) + "行 第" + str(
                            location_column) + "列\n"
                    if leak_unused_content in unused_dict:
                        num_unused += 1
                        str_unused = str_unused + "位于 " + str(path) + " 文件\t第" + str(location_line) + "行 第" + str(
                            location_column) + "列\n"

        str_risk = str_risk_h + "\n" + str_risk_m + "\n" + str_risk_l + "\n" + str_leak + "\n" + str_unused + "\n"
        str_risk = "统计结果：\n" + "\t高等风险函数数量\t" + str(num_high) + "\n" + "\t中等风险函数数量\t" + str(
            num_medium) + "\n" + "\t低风险函数数量\t" + str(num_low) + "\n" + "\t内存泄露函数数量\t" + str(
            num_leak) + "\n" + "\t无效函数数量\t\t" + str(num_unused) + "\n" + str_risk
        return "=" * 70 + "\n" + self.file_path + "\n" + str_risk



    def generate_ast(self, path):
        ast_obj = AST_Tree_json(path)
        try:
            self.ast_instance = ast_obj.get_AST_Root(path)
        except Exception as e:
            print(e)

    def analyze_ast(self, ast_ins, file, str_, num_):
        while True:
            # AST对象存在、能够获取其文件路径
            if ast_ins and hasattr(ast_ins.extent.start, "file") and ast_ins.extent.start.file is not None:
                # 对象属于正在查看的文件且不为根对象
                if ast_ins.extent.start.file.name == file and ast_ins.spelling != file:
                    # 对象存在有效类型且无需忽略
                    if ast_ins.kind is not None and str(ast_ins.spelling) == str_:
                        # 对象存在行数且包含有效解析
                        if ast_ins.location is not None and not is_empty_or_whitespace(
                                ast_ins.spelling):
                            global str_total
                            if str_total != str(ast_ins.location):
                                if num_ == 0:
                                    global num_high
                                    num_high += 1
                                    global str_high
                                    str_high = str_high + self.form_output(str(ast_ins.location)) + "\n\t"
                                    str_total = str(ast_ins.location)
                                if num_ == 1:
                                    global num_medium
                                    num_medium += 1
                                    global str_medium
                                    str_medium = str_medium + self.form_output(str(ast_ins.location)) + "\n\t"
                                    str_total = str(ast_ins.location)
                                if num_ == 2:
                                    global num_low
                                    num_low += 1
                                    global str_low
                                    str_low = str_low + self.form_output(str(ast_ins.location)) + "\n\t"
                                    str_total = str(ast_ins.location)

            if not any(ast_ins.get_children()):
                break
            for child in ast_ins.get_children():
                self.analyze_ast(child, file, str_, num_)
            break

    def form_output(self, str_):
        pattern = r"<SourceLocation file '(?P<file_path>.+?)', line (?P<line>\d+), column (?P<column>\d+)>"
        # 使用正则表达式匹配
        match = re.match(pattern, str_)
        if match:
            file_path = match.group('file_path')
            line = match.group('line')
            column = match.group('column')
            return "位于 " + str(file_path) + " 文件\t第" + str(line) + "行 第" + str(column) + "列"
        return str_

    def get_fig_sizes_1(self):
        return [num_high, num_medium, num_low, num_leak, num_unused]

    def get_fig_labels_1(self):
        return ["HighRiskFunction", "MediumRiskFunction", "LowRiskFunction", "LeakFunction", "UnusedFunction"]

    def get_fig_sizes_high(self):
        global high_sizes
        return high_sizes

    def get_fig_sizes_medium(self):
        global medium_sizes
        return medium_sizes

    def get_fig_sizes_low(self):
        global low_sizes
        return low_sizes

    def get_fig_labels_high(self):
        global high_labels
        return high_labels

    def get_fig_labels_medium(self):
        global medium_labels
        return medium_labels

    def get_fig_labels_low(self):
        global low_labels
        return low_labels

    def free_manager(self):
        global str_high
        global str_medium
        global str_low
        global num_high
        global num_medium
        global num_low
        global str_unused
        global num_unused
        global str_leak
        global num_leak
        global str_risk_h
        global str_risk_m
        global str_risk_l
        global high_labels
        global high_sizes
        global medium_labels
        global medium_sizes
        global low_labels
        global low_sizes
        global str_total
        str_total = ""
        num_high = 0
        num_medium = 0
        num_low = 0
        str_high = ""
        str_medium = ""
        str_low = ""
        num_unused = 0
        str_unused = "无效函数列表：\n"
        num_leak = 0
        str_leak = "内存泄露函数列表：\n"
        str_risk_h = "高风险函数列表：\n\t"
        str_risk_m = "中风险函数列表：\n\t"
        str_risk_l = "低风险函数列表：\n\t"
        high_labels = []
        medium_labels = []
        low_labels = []
        high_sizes = []
        medium_sizes = []
        low_sizes = []


leak_dict = {
    "constParameter",
    "constVariablePointer",
    "leak",
    "nullPointer",
    "possibleNullDereference",
    "uninitConditionVar",
    "uninitStructField",
    "uninitMemberVar",
    "uninitVariable",
    "uninitvar",
    "arrayIndexOutOfBounds",
    "uninitGlobalVar",
    "uninitLocalVar",
}

unused_dict = {
    "unreadVariable",
    "unusedFunction",
    "unreachableCode",
    "unusedFunctionParameter",
    "unusedStructMember"
}

if __name__ == "__main__":
    # file_path = r'C:\Users\86177\Desktop\大作业\登录系统（会员管理）\登录系统.cpp'
    file_path = r"C:\Users\86177\Desktop\test\test.c"
    manager = FunctionManager(file_path)
    results = manager.riskFunction()

    print(results)

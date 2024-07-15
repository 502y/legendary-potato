import subprocess
from queue import Queue
import threading
import json
import re

class CppCheck:
    def __init__(self, file_path):
        self.file_path = file_path

    def checkMemoryLeaks(self):
        cmd = ["cppcheck", "--enable=all", self.file_path]
        output_queue = Queue()

        def enqueue_output(out, queue):
            for line in iter(out.readline, b''):
                # 使用 errors='ignore' 忽略无法解码的字节
                queue.put(line.decode(errors='ignore').strip())
            out.close()

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False)
        output_thread = threading.Thread(target=enqueue_output, args=(process.stdout, output_queue))
        output_thread.daemon = True
        output_thread.start()

        process.wait()
        output_thread.join()

        results = []
        while not output_queue.empty():
            results.append(output_queue.get())

        file_path_pattern = r"^Checking.*\.\.\.$"
        results = [result for result in results if not re.match(file_path_pattern, result)]
        file_path_pattern_ = r".*files checked.*"
        results = [result for result in results if not re.match(file_path_pattern_, result)]

        if results and len(results) > 1:
            results.pop()  # 删除最后一个元素
            results.pop()  # 删除最后一个元素

        # 删除所有3的倍数索引的元素
        i = len(results) - 1
        while i >= 0:
            if (i + 1) % 3 == 0:
                del results[i]
            i -= 1

        json_objects = []

        # 遍历 results 列表，每次取两个元素
        for i in range(0, len(results), 2):
            # 获取路径、位置、内容和代码
            pattern = r"^(.*):(\d+):(\d+):(.*)$"
            match = re.match(pattern, results[i])
            if match:
                path = match.group(1)
                location = match.group(2) + "," + match.group(3)
                content = match.group(4)
            else:
                path = None
                location = None
                content = None
            code = results[i+1]

            # 构建 JSON 对象
            json_object = {
                "path": path.strip(),
                "location": location.strip(),
                "content": content.strip(),
                "code": code.strip()
            }

            # 将 JSON 对象添加到列表中
            json_objects.append(json_object)

        return json_objects

if __name__ == "__main__":
    file_path = r'C:\Users\86177\Desktop\大作业\登录系统（会员管理）'
    checker = CppCheck(file_path)
    results = checker.checkMemoryLeaks()

    if results:
        for line in results:
            print(line)
    else:
        print("No issues found by CppCheck.")


# [invalidscanf] scanf或类似函数的使用可能不安全或无效
# [constParameter] const参数在函数体内被修改
# [constVariablePointer] 指向常量的指针被修改
# [unreadVariable] 变量被声明但从未被读取或使用
# [missingIncludeSystem] 缺少系统头文件
# [useClosedFile] 试图访问一个已经关闭的文件
# [shadowVariable] 变量被声明为相同的名称
# [unusedFunction] 函数未被使用
# [arrayIndexOutOfBounds] 数组索引越界
# [castSizeFunctionToVoid] 函数指针转换为void*
# [duplicateCase] 存在重复的case
# [globalShadowing] 局部变量与全局变量同名
# [incompatiblePointerTypes] 指针类型不兼容
# [invalidPointerCast] 指针类型转换无效
# [leak] 内存泄漏
# [magicNumber] 使用了未定义的数值常量
# [misMatchingDeclarations] 函数声明和定义不匹配
# [nullPointer] 可能的空指针解引用
# [possibleNullDereference] 指针可能为NULL但仍然被解引用
# [uninitConditionVar] 条件变量可能未初始化
# [uninitStructField] 结构体成员可能未初始化
# [uninitMemberVar] 成员变量未初始化
# [uninitVariable] 变量可能未初始化
# [unreachableCode] 代码不可达
# [unusedFunctionParameter] 函数参数未被使用
# [unusedStructMember] 结构体成员未被使用

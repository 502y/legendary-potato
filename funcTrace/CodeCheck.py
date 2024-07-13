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

        # 删除第一个元素，如果列表不为空
        if results:
            results.pop(0)  # 删除第一个元素

        if results and len(results) > 1:
            results.pop()  # 删除最后一个元素
            results.pop()  # 再次删除最后一个元素，此时它已经是倒数第二个元素了

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
    file_path = r'example.c'
    checker = CppCheck(file_path)
    results = checker.checkMemoryLeaks()

    if results:
        for line in results:
            print(line)
    else:
        print("No issues found by CppCheck.")


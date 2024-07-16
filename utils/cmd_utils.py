import os
import subprocess
import tempfile

from PyQt5.QtGui import QColor


def compile_and_run(c_code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp_file:
        tmp_file.write(c_code)
        c_source_path = tmp_file.name

    compile_command = ['gcc', '-o', 'output', c_source_path]
    try:
        result = subprocess.run(compile_command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise Exception(
            f'Compilation failed with error code {e.returncode} and error <span style="color: {QColor("red").name()};">{e.stderr}</span>')

    # 运行编译后的程序
    executable_path = './output'
    try:
        process = subprocess.Popen([executable_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        process.wait()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Execution failed with error code {e.returncode} and output: {e.output}")

    # 清理临时 文件和编译产物
    os.remove(c_source_path)
    current_dir = os.getcwd()
    compile_out_put = os.path.join(current_dir, "output.exe")
    os.remove(compile_out_put)

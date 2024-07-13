import json

from clang.cindex import Index, Config


class AST_Tree_json:
    _instance = None  # 用于存储单例的私有类变量

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, absolute_path, args=None):
        if not hasattr(self, '_initialized'):  # 防止重复初始化
            self._initialized = True
            self.absolute_path = absolute_path
            self.clang_path = r'E:\LLVM\bin\libclang.dll'
            Config.set_library_file(self.clang_path)

            # 设置命令行参数以忽略标准头文件
            if args is None:
                args = ['-nostdinc']
            elif not any(arg.startswith('-nostdinc') for arg in args):
                args.append('-nostdinc')

            self.AST_Root = Index.create().parse(absolute_path, args).cursor

    def serialize_node(self, cursor):
        node_dict = {
            "kind": str(cursor.kind),
            "location": [cursor.extent.start.line, cursor.extent.start.column,
                         cursor.extent.end.line, cursor.extent.end.column],
            "file": cursor.extent.start.file.name if cursor.extent.start.file else '',
            "children": []
        }
        if cursor.spelling:
            # print('kind: ', cursor.kind)
            node_dict["spelling"] = cursor.spelling
            # print('keywords: ', cursor.spelling)
            # print('location: ', cursor.extent.start.line, cursor.extent.start.column,
            #       cursor.extent.end.line, cursor.extent.end.column)
        for child in cursor.get_children():
            child_dict = self.serialize_node(child)
            node_dict["children"].append(child_dict)
        # (start_line, start_column, end_line, end_column) (起始行, 起始列， 结束行，结束列)
        return node_dict

    def start(self):
        string_res = self.serialize_node(self.AST_Root)
        serialized_json = json.dumps(string_res, indent=4, ensure_ascii=False)
        return serialized_json
        # local_time = time.localtime()
        # date_time = time.strftime("%Y_%m_%d_%H_%M_%S", local_time)
        # with open('./res_{}.json'.format(date_time), 'w', encoding='utf-8') as file:
        #     file.write(serialized_json)
        #     file.close()
        # 虽然但是它能识别[]{};+-=，不能获取它们的标识符....而且获取不到值....
        # print(serialized_json)

    def get_AST_Root(self):
        return self.AST_Root

# if __name__ == '__main__':
#     path = r"C:\Users\13238\Downloads\Compressed\CJAG-master\CJAG-master\cjag.c"
#     ast_obj = AST_Tree_json(path)
#     json_ = ast_obj.start()
#     data = json.loads(json_)
#     instance = LLVMGeneratedModel.from_dict(data)
#     with open("report.json", 'w') as f:
#         f.write(json_)
#     # print(json_)

import os
import sqlite3

from utils.str_utils import is_empty_or_whitespace


# file path is "utils/database/database_util.py"
class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


@SingletonDecorator
class Database:
    def __init__(self):
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "code_analysis.db")

        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def execute(self, sql, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self.conn.commit()
        return cursor.fetchall()

    def get_all_threat(self):
        return self.execute("SELECT * FROM Threat")

    def query_by_threat(self, threat: str):
        return self.execute("SELECT * FROM Threat WHERE threat=?", (threat.lower(),))

    def insert_threat(self, description: str, level: int, threat: str = ""):
        self.execute("INSERT INTO Threat (threat,level, description) VALUES (?, ?,?)",
                     (threat.lower(), level, description))

    def delete_threat_by_name(self, threat: str):
        return self.execute("DELETE FROM Threat WHERE threat=?", (threat,))

    def update_threat(self, threat: str, new_threat: str, description: str, level: int):
        # 初始化一个空列表来存储SET子句
        set_clauses = []
        # 初始化一个空列表来存储参数值
        params = []

        if not is_empty_or_whitespace(description):
            set_clauses.append("description = ?")
            params.append(description)
        if level is not None:
            set_clauses.append("level = ?")
            params.append(level)
        if not is_empty_or_whitespace(new_threat):
            set_clauses.append("threat = ?")
            params.append(new_threat)

        if not set_clauses:
            return

        # 构建完整的UPDATE语句
        update_query = f"UPDATE Threat SET {', '.join(set_clauses)} WHERE threat = ?"

        params.append(threat.lower())
        self.execute(update_query, params)

    def search_Threat_Func_re(self, regex_pattern):
        sql_query = f"SELECT * FROM Threat WHERE threat REGEXP {regex_pattern}"
        return self.execute(sql_query)

    def search_Threat_Func_fuzzy(self, pattern):
        sql_query = f"SELECT * FROM Threat WHERE threat LIKE {pattern}"
        return self.execute(sql_query)

    def close(self):
        self.conn.close()

import sqlite3
import time


class DataManager(object):

    def __init__(self):
        super(DataManager, self).__init__()
        self.__cursor = sqlite3.connect("test.db").cursor()
        # 在meta_table表中存放数据表的类型信息和创建时间信息
        self.__cursor.execute("select count(*) from sqlite_master where type='table' and name='meta_table'")
        if self.__cursor.fetchall()[0][0] <= 0:  # 数据库中没有meta_table则新建一个
            self.__cursor.execute("create table meta_table "
                                  "(name text primary key not null, type text not null, create_time integer not null);")
            self.__cursor.connection.commit()

    def get_tables(self) -> list:
        """获取当前数据表中所有表名"""
        self.__cursor.execute("select name from sqlite_master where type='table' order by name")
        return [t[0] for t in self.__cursor.fetchall()]

    def get_my_tables(self, my_type: str) -> list:
        """根据表的类型获取数据表名，my_type可取的值为excel_check.py中的ExcelCheck.headers.keys()"""
        if my_type == '全部表格':
            sql = "select name from meta_table"
        else:
            sql = f"select name from meta_table where type = '{my_type}'"
        self.__cursor.execute(sql)
        return [t[0] for t in self.__cursor.fetchall()]

    def get_my_tables_info(self, my_type: str) -> list:
        """根据表的类型获取保存在meta_table中数据表相关信息，每个元素为一个元组(表名,类型,秒级时间戳)
        my_type可取的值为excel_check.py中的ExcelCheck.headers.keys()"""
        if my_type == '全部表格':
            sql = "select * from meta_table"
        else:
            sql = f"select * from meta_table where type = '{my_type}'"
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def get_columns(self, table_name: str) -> list:
        """返回一个元素为元组的列表，包括每个列的全部信息"""
        self.__cursor.execute('pragma table_info(' + table_name + ')')
        return self.__cursor.fetchall()

    def get_column_names(self, table_name: str) -> list:
        """返回一个列表，每个元素为一个列名"""
        self.__cursor.execute('pragma table_info(' + table_name + ')')
        return [t[1] for t in self.__cursor.fetchall()]

    def get_column_types(self, table_name: str) -> dict:
        """返回一个字典：列名->列数据类型"""
        self.__cursor.execute('pragma table_info(' + table_name + ')')
        columns = self.__cursor.fetchall()
        return {c[1]: c[2] for c in columns}

    def create_table(self, table_type: str, table_name: str, table_columns: list):
        """新建一张类型为table_type，名为table_name的表，各列列名由table_columns定义"""
        # 先加入meta_table
        self.__cursor.execute(
            f"insert into meta_table (name, type, create_time) "
            f"values ('{table_name}', '{table_type}', {int(time.time())});")  # 时间戳为秒级
        # 然后创建表格，使用双引号将表名和列名引起来以防止有的表名或列名为数字
        self.__cursor.execute('create table "{name}" (id integer primary key autoincrement, {columns});'
                              .format(name=table_name, columns=", ".join(f'"{c}" text' for c in table_columns)))
        self.__cursor.connection.commit()

    def insert_data(self, table_name: str, columns: list, rows: list):
        """向table_name表中插入一行或多行数据，这里rows中每一个元组都按照columns指定的顺序排列"""
        for i, row in enumerate(rows):
            try:
                sql = 'insert into "{name}" ({columns}) values ({row});'\
                    .format(name=table_name, columns=', '.join(f'"{c}"' for c in columns),  # 将列名用双引号包起来以防列名为数字
                            row=", ".join(f"'{d}'" for d in row))
                # print(sql)
                self.__cursor.execute(sql)
                self.__cursor.connection.commit()
            except Exception as e:
                raise Exception(f"执行第{i}行对应的SQL语句时出错：{str(e)}\n{sql}")

    def get_table(self, table_name: str) -> (dict, list):
        """返回表格的表头字典和数据表(list[list])"""
        header = self.__cursor.execute(f'pragma table_info({table_name})')
        # 由于数据库中保存了id，所以这里要去掉首列的id；由于id位于第一个，所以后面的索引减去1
        header_dict = {t[1]: t[0]-1 for t in self.__cursor.fetchall()[1:]}
        self.__cursor.execute(f'select * from {table_name}')
        # fetchall返回的是tuple的list，这里转为list的list
        # 由于数据库中保存了id，所以这里要去掉首列的id，表头和列均去掉了首列的id，所以header_dict与data仍然是对应的
        data = [list(t[1:]) for t in self.__cursor.fetchall()]
        return header_dict, data

    def remove_table(self, table_name: str):
        """从数据库中删除要删除的表格"""
        # 使用双引号将表名和列名引起来以防止有的表名为数字
        self.__cursor.execute(f"""delete from meta_table where name = '{table_name}'""")
        self.__cursor.execute(f"""drop table "{table_name}";""")
        self.__cursor.connection.commit()

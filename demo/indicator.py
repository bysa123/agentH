# 1. 异常处理 → 文件读写 with open → json、datetime 标准库
# 2. dict 字典深度练习，字典各种遍历
# 3. class 面向对象基础
# 4. 写小实战：读取文件，解析 json，调用 http 接口，保存结果到本地。

# 小demo:
# 1. 读取文本文件，统计行数
# 2. json 字符串 ↔ python 字典互转
# 3. 使用 requests 调用公开 http 接口，打印返回结果
# 4. 写一个 class 简单实体类，实例化对象

user_list = [
    {"name": "张三", "age": 18, "gender": "男"},
    {"name": "李四", "age": 20, "gender": "女"},
    {"name": "王五", "age": 22, "gender": "男"}
]

user = {
    "name": "张三",
    "age": 18,
    "gender": "男",
}

for k in user_list:
    print(f"姓名: {k['name']}, 年龄: {k['age']}, 性别: {k['gender']}")

for v in user.values():
    print(v)

# calss 面向对象基础： 类比java的class, 封装属性和方法， python一切皆对象， __init__() 构造函数， self 代表实例对象本身
class User:
    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender
    def say_hello(self):
        print(f"大家好，我是{self.name}，今年{self.age}岁，性别{self.gender}")

# 创建实例对象
p1 = User("张三", 23, "男")

class Student(User):
    def __init__(self, name, age, gender, student_id):
        # 调用父类的构造函数
        super().__init__(name, age, gender)
        self.student_id = student_id
    def show_student_id(self):
        print(f"学号: {self.student_id}")
s = Student("王五", 20, "男", "2024001")
object_s = s.__dict__
print(object_s)
# s.say_hello()
# s.show_student_id()

# 1. 定义`Record`类，保存一条记录（name、create_time）
# 2. 实例化 2 个对象，转成字典列表
# 3. 使用`json`保存到本地文件
# 4. 使用`try except`捕获异常
# 5. 使用`datetime`生成时间
import datetime
import json
class Record:
    def __init__(self, name):
        self.name = name;
        self.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_records_to_json(records, filename):
    print(f"保存记录到文件: {filename}")
    try:
        record_dist = [record.__dict__ for record in records]
        with open(filename, "a", encoding="utf-8") as f:
            json.dump(record_dist, f, ensure_ascii=False, indent=2)
        print(f"保存成功，共 {len(records)} 条记录")
    except FileNotFoundError:
        print("文件不存在")
    except json.JSONDecodeError:
        print("json 解析错误")

sq = Record("张三")
sq2 = Record("李四")
save_records_to_json([sq, sq2], "test.json")

# 列表，字典是可变的，直接赋值只是共用同一份内存，改一个另一个也跟着变

# 浅拷贝copy：只拷贝第一层，嵌套里面的子对象仍然共用
# 深拷贝deepcopy：拷贝所有层级，包括嵌套里面的子对象，完全独立的内存空间




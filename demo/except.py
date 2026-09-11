# 错误捕获
def dev(a,b): 
    print('进入函数')
    try:
        res = a / b
    except ZeroDivisionError:
        print("除数不能为0")
        return None
    except TypeError:
        print("类型错误")
        return None

    else:
        print("计算成功")
        return res
    finally:
        print("finally")

print(dev(10, 0))
print(dev(10, "a"))


# 文件读取
with open("demo.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

with open('demo.txt', 'a', encoding='utf-8') as f:
    f.write("追加一行!")

try:
    with open('no_exist.text', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
        print("文件不存在")


# json库
# python对象dict/dist -> json字符串 json.dumps()
# json字符串 -> python对象 json.loads()
import json
data = {
    "name": "张三",
    "age": 18,
    "gender": "男",
}

json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)

# json字符串 → dict
obj = json.loads(json_str) 
print(obj["name"])


# datetime时间库
import datetime
now = datetime.datetime.now()
print('当前时间对象', now)

now_str = now.strftime("%Y-%m-%d %H:%M:%S")
print('当前时间字符串', now_str)

#字符串转时间对象
dt = datetime.datetime.strptime("2024-06-01 12:00:00", "%Y-%m-%d %H:%M:%S")
print('字符串转时间对象', dt)

#时间差
one_day = datetime.timedelta(days=1)
tomorrow = now + one_day
yesterday = now - one_day

# 1. 获取当前时间
# 2. 构造字典数据
# 3. 保存到 json 文件
# 4. 读取这个 json 文件打印，捕获文件不存在异常
nowtime = datetime.datetime.now()
testData = {
    "name": "张三",
    "age": 18,
    "gender": "男",
    "time": nowtime.strftime("%Y-%m-%d %H:%M:%S")
}
with open('test.json', 'w', encoding='utf-8') as f:
    json.dump(testData, f, ensure_ascii=False, indent=2)

try:
    with open('test.json', 'r', encoding='utf-8') as f:
        read_data = json.load(f)
    print(read_data)
except FileNotFoundError:
    print("文件不存在")



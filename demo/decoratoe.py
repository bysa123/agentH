import time
import functools

def log_and_cost(prefix="业务函数"):
    """
    带参数装饰器
    功能：打印入参、统计耗时、捕获异常、打印出参
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"\n=====【{prefix}】开始执行 =====")
            print(f"入参: args={args}, kwargs={kwargs}")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                end = time.perf_counter()
                print(f"出参: {result}")
                print(f"执行成功，耗时: {(end - start):.4f} s")
                return result
            except Exception as e:
                end = time.perf_counter()
                print(f"执行异常！耗时: {(end - start):.4f} s，异常信息：{e}")
                # 可以选择重新抛出异常 raise，或者返回默认值
                raise
        return wrapper
    return decorator


# ------------------- 使用示例 -------------------
@log_and_cost(prefix="加法计算")
def calc_add(a, b):
    return a + b


@log_and_cost(prefix="可能报错的函数")
def div_num(a, b):
    return a / b


if __name__ == "__main__":
    calc_add(100, 200)
    calc_add(a=100, b=200) #kwargs： 精确传递参数，kwargs = {a: 100, b: 200}
    div_num(10, 0)

装饰器就是一个函数，用来在不修改原函数代码、不改动原函数调用地方的前提下，给原有函数新增额外功能
python函数是一等公民
1. 函数可以当做参数传给另一个函数，函数可以返回函数。装饰器就是利用这个特性。
2. 装饰器本质：**闭包 + 语法糖 @**
3. 使用场景：打印日志、统计接口耗时、权限校验、缓存、重试。



# 列表推导
**简洁快速生成列表**，替代普通 for 循环 append，代码更短。
本质：一行语法，快速构建 list。

vnev： python自带的虚拟环境工具
给每一个项目单独创建一套隔离的python环境，避免不同项目之间的依赖冲突。类比前端每个项目的node_modules.

创建虚拟环境：python3 -m venv venv
激活虚拟环境：source venv/bin/activate / Windows： venv\Scripts\activate 
退出虚拟环境：deactivate
导出依赖：pip freeze > requirements.txt
一键安装依赖：pip install -r requirements.txt

pip 只能管 Python 库；venv 只能做隔离环境。
conda 两件事都能干，**甚至可以直接安装、切换 Python 解释器本身，还能管理 C/C++ 底层库**

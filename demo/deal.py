# pandas/numpy基础/PDF/CSV文件处理
# pandas：基于numpy封装，给数组加上列名，索引，变成表格DataFrame;适合处理csv,excel表格等数据，对数据进行清洗、处理、分析等操作；脚本做数据导入导出
# 不适合做业务接口，不把pandas放入接口逻辑
# numpy: 底层数值矩阵，没有列名，没有表头；适合做数值计算，矩阵运算等；脚本做数据分析、科学计算

# 字典进阶 + class 面向对象

# 筛选excel中存储引擎为oss的数据
import pandas as pd
from pathlib import Path
base_dir = Path(__file__).resolve().parent
print(base_dir)
excel_path = base_dir / "data" / 'AI数据集.xlsx'


try:
    df = pd.read_excel(excel_path)
    df_filtered = df[df['存储引擎'] == 'oss']
except FileNotFoundError:
    print("文件不存在")
    exit(1)
# print(df_filtered)
df_filtered.to_csv(base_dir / "data" / 'oss数据.csv', index=False, encoding='utf-8-sig')  # 保存为csv文件
# 将筛选出来的数据保存为json
df_filtered.to_json(base_dir / "data" / 'oss数据.json', orient='records', force_ascii=False)






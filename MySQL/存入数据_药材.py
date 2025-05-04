import csv
import mysql.connector

# 连接数据库（请根据实际情况修改参数）
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2025",  # 替换为你的MySQL密码
    database="fangji",         # 替换为你的数据库名
    charset='utf8mb4'
)

cursor = db.cursor()

# 读取CSV文件并插入数据
with open('中药材.csv', 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # 跳过标题行

    for row in csvreader:
        # 去除每个字段的首尾空格，空字段替换为 None（对应SQL中的 NULL）
        row = [value.strip() if value.strip() else None for value in row]

        # 参数化查询（需确保字段顺序与CSV列顺序一致）
        sql = """INSERT INTO medicine_data 
                 (药材, 别名, 性味归经, 功用, 症状, 药材分类, 用法用量, 注意事项)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            cursor.execute(sql, row)
        except mysql.connector.Error as e:
            print(f"插入数据时出错: {e}, 数据: {row}")

# 提交更改并关闭连接
db.commit()
db.close()
import csv
import mysql.connector

# 连接数据库
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2025",
    database="fangji",
    charset='utf8mb4'
)

cursor = db.cursor()

# 读取CSV文件并插入数据
with open('最终方剂.csv', 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # 跳过标题行

    for row in csvreader:
        # 确保每行有 9 列数据，不足的部分填充为 "尚不明确"
        row = row + ["尚不明确"] * (9 - len(row)) if len(row) < 9 else row[:9]

        # 如果字段为空或为 None，则替换为 "尚不明确"
        row = ["尚不明确" if not value else value for value in row]

        # 参数化查询
        sql = """INSERT INTO chinese_medicine
                 (药剂, 古籍, 配方, 功用, 症状, 使用注意, 用法用量, 注意事项, 组成)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            cursor.execute(sql, row)
        except mysql.connector.Error as e:
            print(f"插入数据时出错: {e}, 数据: {row}")

# 提交更改并关闭连接
db.commit()
db.close()
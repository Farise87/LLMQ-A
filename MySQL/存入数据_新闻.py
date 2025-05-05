import csv
import mysql.connector

# 数据库配置
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2025",
    database="fangji",
    charset='utf8mb4'
)

# 连接数据库

cursor = db.cursor()



# 读取CSV文件并插入数据
with open('资讯数据.csv', 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # 跳过标题行

    for row in csvreader:


        # 参数化查询
        sql = """INSERT INTO medicine_news
                 (标题, 图片链接, 文章内容)
                 VALUES (%s, %s, %s)"""
        try:
            cursor.execute(sql, row)
        except mysql.connector.Error as e:
            print(f"插入数据时出错: {e}, 数据: {row}")

# 提交事务并关闭连接
db.commit()
cursor.close()
db.close()

print("数据导入成功！")
CREATE TABLE IF NOT EXISTS chinese_medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    药剂 VARCHAR(255) NOT NULL,
    古籍 VARCHAR(255),
    配方 TEXT,
    功用 TEXT,
    症状 TEXT,
    使用注意 TEXT,
    用法用量 TEXT,
    注意事项 TEXT,
    组成 TEXT
);
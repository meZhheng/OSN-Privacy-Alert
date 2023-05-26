from Mysql import Mysql
import csv


def read_csv_and_process(file_path, columns, batch_size):
    data = []
    count = 0
    database = Mysql()

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)  # 读取CSV文件的头部
        column_indices = [header.index(column) for column in columns]

        for row in reader:
            count += 1
            row_data = [row[i] for i in column_indices]
            # row_data = [s.encode('utf8mb4') for s in row_data]
            data.append(row_data)

            if count % batch_size == 0:
                database.blog_insert(data)
                data = []

        if data:  # 处理剩余的不足50行的数据
            database.blog_insert(data)

    database.close()


def main():
    # 使用示例：
    file_path = r"D:\文档\WeChat Files\wxid_8t2ki3l4hglp22\FileStorage\File\2023-05\5634364264.csv"  # CSV文件路径
    columns = ['bid', '正文', '日期', '位置', '工具', '话题', '评论数', '点赞数', '转发数', '@用户']  # 要读取的列名

    read_csv_and_process(file_path, columns, 50)


if __name__ == "__main__":
    main()

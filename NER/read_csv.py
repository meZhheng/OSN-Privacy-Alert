import csv
from predict_sequence_label import predict


def read_csv_column(input_file_path, output_file_path, column_name):
    """
    从CSV文件中读取指定列的数据，并进行预测，将结果写入另一个CSV文件。

    参数:
        input_file_path (str): 输入CSV文件的路径。
        output_file_path (str): 输出CSV文件的路径。
        column_name (str): 要读取的列名。
    """
    with open(input_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        if column_name not in reader.fieldnames:
            print(f"在CSV文件中找不到列 '{column_name}'。")
            return []

        for row in reader:
            result = predict(row[column_name])  # 进行预测
            write_dict_to_csv(output_file_path, result)  # 将结果写入输出CSV文件


def write_dict_to_csv(file_path, data_dict):
    """
    将字典数据作为一行写入CSV文件。

    参数:
        file_path (str): CSV文件的路径。
        data_dict (dict): 要写入的字典数据。
    """
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([str(data_dict)])  # 将字典数据转换为字符串并写入CSV文件


def main():
    # 指定CSV文件路径和要读取的列名
    input_file_path = r"D:\文档\WeChat Files\wxid_8t2ki3l4hglp22\FileStorage\File\2023-05\1907518591.csv"
    output_file_path = 'output.csv'
    column_name = '正文'

    read_csv_column(input_file_path, output_file_path, column_name)


if __name__ == "__main__":
    main()

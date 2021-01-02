import json


def process_json(input_json_file, output_json_file):
    file_in = open(input_json_file, "r")
    file_out = open(output_json_file, "w")
    # load数据到变量json_data
    json_data = json.load(file_in)
    print(json_data)
    print("after update  --->")
    print(type(json_data))
    # 修改json中的数据
    json_data["user/throttle"] = "0.0"
    print(json_data)
    # 将修改后的数据写回文件
    file_out.write(json.dumps(json_data))
    file_in.close()
    file_out.close()


if __name__ == '__main__':
    for i in range(133, 163):
        process_json("data/record_"+str(i)+".json", "correction/record_"+str(i)+".json")




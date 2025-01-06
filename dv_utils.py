import logging
import os
import csv
import pprint

from constants import causes, csrs, csrs32
from shared_utils import InstrDict, arg_lut

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")


def make_dv(instr_dict: InstrDict):
    # 指定输出的 CSV 文件名

    data = []
    for key in instr_dict.keys():
        dict_item = instr_dict[key]
        temp_dict = {}
        temp_dict['isa_name'] = dict_item['isa_name']
        temp_dict['type'] = dict_item['type']
        temp_dict['opcode'] = dict_item['opcode']
        if dict_item['funct3']:
            temp_dict['funct3'] = dict_item['funct3']
        else:
            temp_dict['funct3'] = ''
        if dict_item['funct7']:
            temp_dict['funct7'] = dict_item['funct7']
        else:
            temp_dict['funct7'] = ''
        data.append(temp_dict)
    pass



    # 假设字典列表如下
#    data = [
#        {"Name": "Alice", "Age": 25, "City": "New York"},
#        {"Name": "Bob", "Age": 30, "City": "Los Angeles"},
#        {"Name": "Charlie", "Age": 35, "City": "Chicago"}
#    ]

    # 指定输出的 CSV 文件名
    output_file = "output.csv"

    # 将数据写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())

        # 写入表头
        writer.writeheader()

        # 写入数据行
        writer.writerows(data)

    print(f"数据已成功写入 {output_file}")

    # Write the modified output to the file
#    with open("dv.encoding.out.h", "w", encoding="utf-8") as enc_file:
#        enc_file.write(output_str)



riscv_isa_type_dict = {'0110011': 'R',
                       '0111011': 'R',
                       '1010011': 'R',
                       '1110111': 'R',
                       '0000011': 'I',
                       '0010011': 'I',
                       '1100111': 'I',
                       '1110011': 'I',
                       '0001111': 'I',
                       '0011011': 'I',
                       '0100011': 'S',
                       '1100011': 'B',
                       '0110111': 'U',
                       '0010111': 'U',
                       '1101111': 'J',
                       '0101111': 'A',
                       '1010111': 'V'
                       }

def parse_isa(isa_dict:  InstrDict):
    dict_item = {}
    for key in isa_dict.keys():
        dict_item = isa_dict[key]
        encoding = isa_dict[key]['encoding']
        opcode = encoding[25:32]
        isa_dict[key]['isa_name'] = key
        isa_dict[key]['opcode'] = opcode
        isa_dict[key]['type'] = riscv_isa_type_dict[opcode]
        if 'R' == isa_dict[key]['type']:
            funct7 = encoding[0:7]
            funct3 = encoding[17:20]
            isa_dict[key]['funct7'] = funct7
            isa_dict[key]['funct3'] = funct3
        if 'I' == isa_dict[key]['type']:
            funct3 = encoding[17:20]
            isa_dict[key]['funct3'] = funct3
            if ('0010011' == isa_dict[key]['opcode']) or ('0011011' == isa_dict[key]['opcode']):
                funct7 = encoding[0:7]
                isa_dict[key]['funct7'] = funct7
        if 'B' == isa_dict[key]['type']:
            funct3 = encoding[17:20]
            isa_dict[key]['funct3'] = funct3
        if 'S' == isa_dict[key]['type']:
            funct3 = encoding[17:20]
            isa_dict[key]['funct3'] = funct3
        if 'J' == isa_dict[key]['type']:
            pass
        if 'U' == isa_dict[key]['type']:
            pass
import logging
import os
import csv
import pprint

from constants import causes, csrs, csrs32
from shared_utils import InstrDict, arg_lut

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")


def add_leading_quote(row):
    return {k: f"{v}" if isinstance(v, str) and v.isdigit() else v for k, v in row.items()}

def force_text_format(row):
    return {k: f'= "{v}"' if k == "ID" else v for k, v in row.items()}

def make_talon(instr_dict: InstrDict):

    talon_r = []         # for R-type instructions
    talon_i = []         # for I-type instructions
    talon_i_shamtd = []  # for I-type shamtd-subtype instructions
    talon_i_shamtw = []  # for I-type shamtw-subtype instructions


    for key in instr_dict.keys():
        dict_item = instr_dict[key]  # get source data

        temp_dict = {}               # for data transfer, maybe opttmazed in future
        talon_dict = {}              # transfer information to talon

        ###
        # copy data from source to local
        ###
        temp_dict['extension'] = dict_item['extension'][0]
        temp_dict['isa_name'] = dict_item['isa_name']
        temp_dict['type'] = dict_item['type']
        temp_dict['opcode'] = dict_item['opcode']
        temp_dict['variable_filed'] = dict_item['variable_fields']

        ### assemble instruction and variables
        temp_dict['instruction'] = dict_item['isa_name']
        for item in temp_dict['variable_filed']:
            temp_dict['instruction'] +=  ' ' + item + ','

        temp_dict['instruction'] = temp_dict['instruction'].rstrip(',')
        talon_dict['Instructions'] = temp_dict['instruction']

        if "funct3" in dict_item:
            temp_dict['funct3'] = dict_item['funct3']
        else:
            temp_dict['funct3'] = ''
        if 'funct7' in dict_item:
            temp_dict['funct7'] = dict_item['funct7']
        else:
            temp_dict['funct7'] = ''
        if 'imm12' in dict_item:
            temp_dict['imm12'] = dict_item['imm12']
        else:
            temp_dict['imm12'] = ''



        ###
        # change format for talon
        ###
        if "_" in talon_dict['Instructions']:
            talon_dict['Instructions'] = talon_dict['Instructions'].replace("_", ".")

        if "shamtd" in talon_dict['Instructions']:
            talon_dict['Instructions'] = talon_dict['Instructions'].replace("shamtd", "shamt")

        if "shamtw" in talon_dict['Instructions']:
            talon_dict['Instructions'] = talon_dict['Instructions'].replace("shamtw", "shamt")

        talon_dict['opcode[6:5]'] = temp_dict['opcode'][0:2]
        talon_dict['opcode[4:2]'] = temp_dict['opcode'][2:5]
        talon_dict['opcode[1:0]'] = temp_dict['opcode'][5:]

        ###
        # deal data according to type and sub-type
        ###
        if 'R' == temp_dict['type']:
            talon_dict['funct7[31:25]'] = temp_dict['funct7']
            talon_dict['funct3[14:12]'] = temp_dict['funct3']
            talon_dict['inst[24:20]'] = 'rs2'
            talon_dict['inst[19:15]'] = 'rs1'
            talon_dict['inst[11:17]'] = 'rd'
            talon_r.append(talon_dict)

        if 'I' == temp_dict['type']:
            talon_dict['funct3[14:12]'] = temp_dict['funct3']
            talon_dict['inst[19:15]'] = 'rs1'
            talon_dict['inst[11:17]'] = 'rd'
            if 'shamtd' in temp_dict['variable_filed']:                # shamtd sub-type
                talon_dict['funct7[31:26]'] = temp_dict['imm12'][0:6]
                talon_dict['inst[25:20]'] = 'shamt'
                talon_i_shamtd.append(talon_dict)
            elif 'shamtw' in temp_dict['variable_filed']:              # shamtw sub-type
                talon_dict['funct7[31:25]'] = temp_dict['imm12'][0:7]
                talon_dict['inst[24:20]'] = 'shamt'
                talon_i_shamtw.append(talon_dict)
            else:                                                      # normal I-type
                talon_dict['inst[31:20]'] = temp_dict['imm12']
                talon_i.append(talon_dict)


    ###
    # Generate R type for talon
    ###
    output_file = "r_type.csv"
    field_order = ["Instructions", "funct7[31:25]", "inst[24:20]", "inst[19:15]",
                   "funct3[14:12]", "inst[11:17]", "opcode[6:5]", "opcode[4:2]", "opcode[1:0]"]
    # 将数据写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = field_order, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows([add_leading_quote(row) for row in talon_r])
    print(f"数据已成功写入 {output_file}")

    ###
    # Generate I type for talon
    ###
    output_file = "I_type.csv"
    field_order = ["Instructions", "inst[31:20]", "inst[19:15]",
                   "funct3[14:12]", "inst[11:17]", "opcode[6:5]", "opcode[4:2]", "opcode[1:0]"]
    # 将数据写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = field_order, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows([add_leading_quote(row) for row in talon_i])
    print(f"数据已成功写入 {output_file}")

    ###
    # Generate I type shmatd subtype for talon
    ###
    output_file = "I_shamtd_type.csv"
    field_order = ["Instructions", "funct7[31:26]", "inst[25:20]", "inst[19:15]",
                   "funct3[14:12]", "inst[11:17]", "opcode[6:5]", "opcode[4:2]", "opcode[1:0]"]
    # 将数据写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = field_order, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows([add_leading_quote(row) for row in talon_i_shamtd])
    print(f"数据已成功写入 {output_file}")

    ###
    # Generate I type shmatd subtype for talon
    ###
    output_file = "I_shamtw_type.csv"
    field_order = ["Instructions", "funct7[31:25]", "inst[24:20]", "inst[19:15]",
                   "funct3[14:12]", "inst[11:17]", "opcode[6:5]", "opcode[4:2]", "opcode[1:0]"]
    # 将数据写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = field_order, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows([add_leading_quote(row) for row in talon_i_shamtw])
    print(f"数据已成功写入 {output_file}")
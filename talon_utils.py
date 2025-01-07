import logging
import os
import csv
import pprint

from constants import causes, csrs, csrs32
from shared_utils import InstrDict, arg_lut

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")



#example
#
#  `define ZBB_I_INSTR_CG_BEGIN(INSTR_NAME) \
#  `INSTR_CG_BEGIN(INSTR_NAME, riscv_zbb_instr) \
#    cp_rs1         : coverpoint instr.rs1; \
#    cp_rd          : coverpoint instr.rd; \
#    `DV(cp_gpr_hazard : coverpoint instr.gpr_hazard;)
#
#`define ZBB_R_INSTR_CG_BEGIN(INSTR_NAME) \
#  `INSTR_CG_BEGIN(INSTR_NAME, riscv_zbb_instr) \
#    cp_rs1         : coverpoint instr.rs1; \
#    cp_rs2         : coverpoint instr.rs2; \
#    cp_rd          : coverpoint instr.rd;  \
#    `DV(cp_gpr_hazard : coverpoint instr.gpr_hazard;) \
# \
#    `ZBB_I_INSTR_CG_BEGIN(roriw)
#`CP_VALUE_RANGE(num_bit_rotate, instr.imm, 0, XLEN / 2 - 1)
#`CG_END
#
#`ZBB_R_INSTR_CG_BEGIN(rev8)
#`CG_END
#
#// Multiplication
#`ZBC_R_INSTR_CG_BEGIN(clmul)
#`CG_END
#
#`ZBC_R_INSTR_CG_BEGIN(clmulh)
#`CG_END



coverage_define = []
coverage_define_record = []
coverage_delaration = []

funct3_info = []
funct7_info = []


def gen_coverage_code(instr_dict: dict):
    global coverage_delaration
    extension = instr_dict['extension']
    if '_' in extension :
        isa_extension = extension.split('_')[1].upper()
    else:
        isa_extension = 'ERROR'

    isa_type = instr_dict['type']
    isa_name = instr_dict['isa_name']

    sv_line = '`' + isa_extension + '_' + isa_type + '_INSTR_CG_BEGIN(' + isa_name +')'
    coverage_delaration.append(sv_line)
    sv_line = '`CG_END'
    coverage_delaration.append(sv_line)
    sv_line = ''
    coverage_delaration.append(sv_line)

    #  `define ZBB_I_INSTR_CG_BEGIN(INSTR_NAME) \
    #  `INSTR_CG_BEGIN(INSTR_NAME, riscv_zbb_instr) \
    #    cp_rs1         : coverpoint instr.rs1; \
    #    cp_rd          : coverpoint instr.rd; \
    #    `DV(cp_gpr_hazard : coverpoint instr.gpr_hazard;)
    #
    sv_line = '  `define ' + isa_extension  + '_' + isa_type +'_INSTR_CG_BEGIN(INSTR_NAME) \\'
    if sv_line not in coverage_define_record:
        coverage_define_record.append(sv_line)
        coverage_define.append(sv_line)

        sv_line = '  `INSTR_CG_BEGIN(INSTR_NAME, ' + 'riscv_' + isa_extension.lower() + '_instr) \\'
        coverage_define.append(sv_line)

        sv_line = '    cp_rs1         : coverpoint instr.rs1; \\'
        coverage_define.append(sv_line)

        sv_line = '    cp_rd          : coverpoint instr.rd; \\'
        coverage_define.append(sv_line)

        sv_line = '    `DV(cp_gpr_hazard : coverpoint instr.gpr_hazard;)'
        coverage_define.append(sv_line)

        sv_line = '  '
        coverage_define.append(sv_line)

    funct3_info = []
    funct7_info = []


    if "funct3" in instr_dict:
        sv_line = isa_name.upper() + ': get_func3 = 3\'b' + instr_dict['funct3'];
        funct3_info.append(sv_line)
    if "funct7" in instr_dict:
        sv_line = isa_name.upper() + ': get_func7 = 7\'b' + instr_dict['funct7'];
        funct7_info.append(sv_line)

    pass



def add_leading_quote(row):
    return {k: f"{v}" if isinstance(v, str) and v.isdigit() else v for k, v in row.items()}

def force_text_format(row):
    return {k: f'= "{v}"' if k == "ID" else v for k, v in row.items()}

def make_talon(instr_dict: InstrDict):
    # 指定输出的 CSV 文件名

    data = []
    talon_r = []
    talon_i = []
    for key in instr_dict.keys():
        dict_item = instr_dict[key]
        temp_dict = {}
        talon_dict = {}
        temp_dict['extension'] = dict_item['extension'][0]
        temp_dict['isa_name'] = dict_item['isa_name']
        temp_dict['type'] = dict_item['type']
        temp_dict['opcode'] = dict_item['opcode']
        temp_dict['variable_filed'] = dict_item['variable_fields']

        temp_dict['instruction'] = dict_item['isa_name']
        for item in temp_dict['variable_filed']:
            temp_dict['instruction'] +=  ' ' + item + ','

        temp_dict['instruction'] = temp_dict['instruction'].rstrip(',')
        talon_dict['Instructions'] = temp_dict['instruction']
        pass

        if "funct3" in dict_item:
            temp_dict['funct3'] = dict_item['funct3']
        else:
            temp_dict['funct3'] = ''
        if 'funct7' in dict_item:
            temp_dict['funct7'] = dict_item['funct7']
        else:
            temp_dict['funct7'] = ''

        talon_dict['opcode[6:5]'] = temp_dict['opcode'][0:2]
        talon_dict['opcode[4:2]'] = temp_dict['opcode'][2:5]
        talon_dict['opcode[1:0]'] = temp_dict['opcode'][5:]

        if 'R' == temp_dict['type']:
            talon_dict['funct7[31:25]'] = temp_dict['funct7']
            talon_dict['funct3[14:12]'] = temp_dict['funct3']
            talon_dict['inst[24:20]'] = 'rs2'
            talon_dict['inst[19:15]'] = 'rs1'
            talon_dict['inst[11:17]'] = 'rd'
            talon_r.append(talon_dict)

        if 'I' == temp_dict['type']:
            talon_i.append(talon_dict)

        data.append(temp_dict)
        gen_coverage_code(temp_dict)
    pass



    # 假设字典列表如下
#    data = [
#        {"Name": "Alice", "Age": 25, "City": "New York"},
#        {"Name": "Bob", "Age": 30, "City": "Los Angeles"},
#        {"Name": "Charlie", "Age": 35, "City": "Chicago"}
#    ]

    # 指定输出的 CSV 文件名
    output_file = "output.csv"

    field_order = ["Instructions", "funct7[31:25]", "inst[24:20]", "inst[19:15]",
                   "funct3[14:12]", "inst[11:17]", "opcode[6:5]", "opcode[4:2]", "opcode[1:0]"]
    # 将数据写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = field_order, quoting=csv.QUOTE_MINIMAL)

        # 写入表头
        writer.writeheader()

        # 写入数据行
        #writer.writerows(talon_r)
        writer.writerows([add_leading_quote(row) for row in talon_r])
    print(f"数据已成功写入 {output_file}")

    # 指定输出文件名
    coverage_delaration_file = "coverage_delaration.sv"

    # 按行写入 .sv 文件
    with open(coverage_delaration_file, mode='w', encoding='utf-8') as file:
        for line in coverage_define:
            file.write(line + '\n')  # 每行写入后添加换行符
    # 按行写入 .sv 文件
    with open(coverage_delaration_file, mode='a', encoding='utf-8') as file:
        for line in coverage_delaration:
            file.write(line + '\n')  # 每行写入后添加换行符

    print(f"内容已成功写入到 {coverage_delaration_file}")



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
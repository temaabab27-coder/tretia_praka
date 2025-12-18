# src/assembler.py
import argparse
import yaml

# --- Коды операций ---
OPCODES = {
    "load": 8,
    "read": 25,
    "write": 4,
    "div": 27,
}

def encode_load(const):
    # A=8, B=const (27 бит), команда: 4 байта, little-endian
    val = (8 & 0x1F) | ((const & 0x1FFFFFF) << 5)
    return val.to_bytes(4, "little")

def encode_read(addr):
    # A=25, B=addr (11 бит), команда: 2 байта
    val = (25 & 0x1F) | ((addr & 0x7FF) << 5)
    return val.to_bytes(2, "little")

def encode_write(addr):
    # A=4, B=addr (11 бит), команда: 2 байта
    val = (4 & 0x1F) | ((addr & 0x7FF) << 5)
    return val.to_bytes(2, "little")

def encode_div(addr):
    # A=27, B=addr (11 бит), команда: 2 байта
    val = (27 & 0x1F) | ((addr & 0x7FF) << 5)
    return val.to_bytes(2, "little")

def parse_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("program", [])

def assemble(instructions):
    binary = b""
    for instr in instructions:
        for op, arg in instr.items():
            op = op.lower()
            if op == "load":
                binary += encode_load(arg)
            elif op == "read":
                binary += encode_read(arg)
            elif op == "write":
                binary += encode_write(arg)
            elif op == "div":
                binary += encode_div(arg)
            else:
                raise ValueError(f"Неизвестная команда: {op}")
    return binary

def format_bytes(binary):
    parts = []
    for b in binary:
        parts.append(f"0x{b:02X}")
    return ", ".join(parts)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="YAML-файл с программой")
    parser.add_argument("-o", "--output", required=True, help="Выходной .bin файл")
    parser.add_argument("--test", action="store_true", help="Режим теста: вывести байты")
    args = parser.parse_args()

    instructions = parse_yaml(args.input)
    binary = assemble(instructions)

    if args.test:
        print(format_bytes(binary))

    with open(args.output, "wb") as f:
        f.write(binary)

    print(f"Собрано {len(instructions)} команд → {len(binary)} байт")

if __name__ == "__main__":
    main()
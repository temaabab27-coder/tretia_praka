import argparse
import struct
import csv

def decode_instruction(byte_stream, offset):
    # Читаем первый байт, чтобы определить opcode (младшие 5 бит)
    if offset >= len(byte_stream):
        return None, 0
    first_byte = byte_stream[offset]
    opcode = first_byte & 0x1F  # младшие 5 бит

    if opcode == 8:  # LOAD: 4 байта
        if offset + 4 > len(byte_stream):
            raise ValueError("Недостаточно байт для LOAD")
        val = struct.unpack("<I", byte_stream[offset:offset+4])[0]
        const = (val >> 5) & 0x1FFFFFF
        return {"op": "LOAD", "arg": const}, 4

    elif opcode in (25, 4, 27):  # READ, WRITE, DIV: по 2 байта
        if offset + 2 > len(byte_stream):
            raise ValueError("Недостаточно байт для команды")
        val = struct.unpack("<H", byte_stream[offset:offset+2])[0]
        addr = (val >> 5) & 0x7FF
        op_name = {25: "READ", 4: "WRITE", 27: "DIV"}[opcode]
        return {"op": op_name, "addr": addr}, 2

    else:
        raise ValueError(f"Неизвестный opcode: {opcode} (байт 0x{first_byte:02X})")

def run_program(binary, test_mode=False):
    # Память — 1024 ячейки
    mem = [0] * 1024
    acc = 0
    pc = 0  # program counter

    # Декодируем программу
    instructions = []
    offset = 0
    while offset < len(binary):
        instr, size = decode_instruction(binary, offset)
        if instr is None:
            break
        instructions.append(instr)
        offset += size

    if test_mode:
        print(f"Программа загружена: {len(instructions)} команд")

    # Выполняем
    for i, instr in enumerate(instructions):
        op = instr["op"]
        if op == "LOAD":
            acc = instr["arg"]
            if test_mode:
                print(f"[{i}] LOAD {instr['arg']} → ACC = {acc}")
        elif op == "READ":
            addr = instr["addr"]
            if addr >= len(mem):
                raise IndexError(f"READ: адрес {addr} вне памяти")
            acc = mem[addr]
            if test_mode:
                print(f"[{i}] READ {addr} → ACC = {acc} (mem[{addr}] = {mem[addr]})")
        elif op == "WRITE":
            addr = instr["addr"]
            if addr >= len(mem):
                raise IndexError(f"WRITE: адрес {addr} вне памяти")
            mem[addr] = acc
            if test_mode:
                print(f"[{i}] WRITE {addr} ← ACC = {acc}")
        elif op == "DIV":
            addr = instr["addr"]
            if addr >= len(mem):
                raise IndexError(f"DIV: адрес {addr} вне памяти")
            divisor = mem[addr]
            if divisor == 0:
                raise ZeroDivisionError(f"DIV: деление на ноль в mem[{addr}]")
            acc //= divisor
            if test_mode:
                print(f"[{i}] DIV {addr} → ACC = {acc} (деление на mem[{addr}] = {divisor})")
        else:
            raise ValueError(f"Неизвестная команда: {op}")

    if test_mode:
        print(f"Выполнено. ACC = {acc}")

    return mem, acc

def save_memory_dump(mem, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for i, val in enumerate(mem):
            if val != 0:  # только ненулевые ячейки (опционально)
                writer.writerow([i, val])
    print(f"Дамп памяти сохранён: {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Бинарный файл (.bin)")
    parser.add_argument("-o", "--output", help="CSV-дамп памяти")
    parser.add_argument("--test", action="store_true", help="Режим теста: вывод шагов")
    args = parser.parse_args()

    with open(args.input, "rb") as f:
        binary = f.read()

    mem, acc = run_program(binary, test_mode=args.test)

    if args.output:
        save_memory_dump(mem, args.output)

if __name__ == "__main__":
    main()
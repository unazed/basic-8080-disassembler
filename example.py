import unazed_disasm
import string


if __name__ != "__main__":
    raise SystemExit("run this at top-level, thanks")

with open("example.com", 'rb') as data:
    data = data.read()
disasm = unazed_disasm.Disassembler(data, unazed_disasm.OPCODE_MAP)
offs = 0
for instr, *operands in disasm.iterate_instructions():
    bytes_ = f"{format(ord(instr.byte_ident), 'x').rjust(2,'0'):4s}"
    if instr.operands:
        _ = instr.operands[0].data
        _ = [_[i:i+2] for i in range(0, len(_), 2) ]
        bytes_ += ' '.join(_)
    ascii_ = [k if k in string.ascii_letters else '.' for k in map(chr, map(lambda x: int(x, 16), bytes_.split()))]
    print(f"+{format(offs, 'x').rjust(4, '0'):10s} {bytes_:20s} {instr.op_ident % operands[0] if operands else instr.op_ident:20s} {''.join(ascii_).ljust(3, '.'):4s} {instr._note}")
    offs += instr.byte_size + 1

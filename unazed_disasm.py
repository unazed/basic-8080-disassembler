CODE_MAP = {
    "INT_ERR": 0x01,
    "BIN_ILL": 0x02,
    'BIN_ARG': 0x03
    }


class Operand:
    @staticmethod
    def int_to_array(data):
        arr = []
        while data:
            arr.append(data & 0xFF)
            data >>= 8
        return arr[::-1]

    def __init__(self, data, ty, byte_size=None):
        if ty not in ["d8", "d16", "a16"]:
            int_halt(CODE_MAP['INT_ERR'], "Internal Error",
                     "Operadn.__init__ received unexpected 'ty' parameter")
        self.ty = ty
        if data is None:
            if byte_size is None:
                int_halt(CODE_MAP['INT_ERR'],
                         "Internal Error",
                         "Operand.__init__ received NoneType 'data', but "
                         "did not expect NoneType 'byte_size'")
            self.byte_size = byte_size
            self.data = data
        elif isinstance(data, int):
            div, mod = divmod(data.bit_length(), 8)
            self.byte_size = byte_size or div + (not not mod)
            self.data = self.int_to_array(data)
        elif isinstance(data, (list, tuple)):
            self.byte_size = byte_size or len(data)
            self.data = list(data)
        elif isinstance(data, str):
            self.byte_size = byte_size or len(data)
            self.data = list(map(ord, data))
        elif isinstance(data, bytes):
            self.byte_size = byte_size or len(data)
            self.data = list(data)
        else:
            int_halt(CODE_MAP['INT_ERR'],
                     "Internal error",
                     "Operand.__init__ received abnormal 'data' type: "
                     f"{type(data)}")

    def copy(self):
        return Operand(self.data, self.ty, self.byte_size)


class Instruction:
    def __init__(self, op_ident, byte_ident, *operands, fn=None):
        self.op_ident = op_ident
        self.byte_ident = byte_ident
        self.operands = operands
        self.byte_size = sum(op.byte_size for op in operands)
        self.fn = fn
        self._note = ""

    def __str__(self):
        return f"<{self.op_ident!r}, {self.byte_size} bytes, {self.operands}>"

    def unpack(self):
        return (self.byte_ident, self)

    def copy(self):
        operands = map(Operand.copy, self.operands)
        return Instruction(self.op_ident, self.byte_ident, *operands, fn=self.fn)


class Disassembler:
    def __init__(self, data, opcode_map, org=0x00):
        self.data = data
        self.org = org
        self.opcode_map = opcode_map

    def iterate_instructions(self):
        byte_stack = list(self.data)
        while byte_stack:
            byte = byte_stack.pop(0)
            if (instr := self.opcode_map.get(chr(byte), None)) is None:
                int_halt(CODE_MAP['BIN_ILL'], "Diassembler Error",
                         f"Unknown byte {byte!r} parsed", True)
                continue
            instr = instr.copy()
            operands = []
            for op in instr.operands:
                if op.ty == "d16":
                    try:
                        data = format(byte_stack.pop(0) | (byte_stack.pop(0) << 8),
                                'x').rjust(4, '0')
                        operands.append(f"$0x{data}")
                    except IndexError:
                        int_halt(CODE_MAP['BIN_ARG'], "Disassembler Error",
                                 f"Insufficient arguments for {instr.op_ident!r}"
                                 " expected 1 `d16` arg, got none")
                elif op.ty == "d8":
                    try:
                        data = format(byte_stack.pop(0), 'x').rjust(2,'0')
                        operands.append(f"$0x{data}")
                    except IndexError:
                        int_halt(CODE_MAP['BIN_ARG'], "Disassembler Error",
                                f"Insufficient arguments for {instr.op_ident!r}"
                                " expected 1 `d8` arg, got none")
                elif op.ty == "a16":
                    try:
                        addr = byte_stack.pop(0) | (byte_stack.pop(0) << 8)
                        if addr - self.org >= 0:
                            addr -= self.org
                            instr._note += f"(reloc. -{hex(self.org)}) "
                        else:
                            instr._note = f"(reloc. out of bounds) "
                        data = format(addr, 'x').rjust(4, '0')
                        operands.append(f"(0x{data})")
                    except IndexError:
                        int_halt(CODE_MAP['BIN_ARG'], "Disassembler Error",
                                f"Insufficient arguments for {instr.op_ident!r}"
                                "expected 1 `a16` arg, got none")
                op.data = data if not len(data) % 2 else f"\x00{data}"
            if instr.op_ident.startswith("*"):
                instr._note += f"(unused op.) "
            yield (instr, *operands)

def int_halt(code, msg, add=None, warn=False):
    msg = f"\n[{code}]\tfatal\t\t{msg}\n" \
          f"|\tnote:\t\t{add or '(null)'}\n" \
          f"|\t{'continuing' if warn else 'halting'} ..."
    if warn:
        return print(msg)
    raise SystemExit(msg)


OPCODE_MAP = dict(map(Instruction.unpack, [
    Instruction("NOP", "\x00",
                fn=lambda env:
                    None
                ),
    Instruction("LXI B,%s", "\x01",
                Operand(None, "d16", 0x02),
                fn=lambda env, d16:
                    None
                ),
    Instruction("STAX B", "\x02",
                fn=lambda env:
                    None
                ),
    Instruction("INX B", "\x03",
                fn=lambda env:
                    None
                ),
    Instruction("INR B", "\x04",
                fn=lambda env:
                    None
                ),
    Instruction("DCR B", "\x05",
                fn=lambda env:
                    None
                ),
    Instruction("MVI B,%s", "\x06",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RLC", "\x07",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x08",
                fn=lambda env:
                    None
                ),
    Instruction("DAD B", "\x09",
                fn=lambda env:
                    None
                ),
    Instruction("LDAX B", "\x0A",
                fn=lambda env:
                    None
                ),
    Instruction("DCX B", "\x0B",
                fn=lambda env:
                    None
                ),
    Instruction("INR C", "\x0C",
                fn=lambda env:
                    None
                ),
    Instruction("DCR C", "\x0D",
                fn=lambda env:
                    None
                ),
    Instruction("MVI C,%s", "\x0E",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RRC", "\x0F",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x10",
                fn=lambda env:
                    None
                ),
    Instruction("LXI D,%s", "\x11",
                Operand(None, "d16", 0x02),
                fn=lambda env, d16:
                    None
                ),
    Instruction("STAX D", "\x12",
                fn=lambda env:
                    None
                ),
    Instruction("INX D", "\x13",
                fn=lambda env:
                    None
                ),
    Instruction("INR D", "\x14",
                fn=lambda env:
                    None
                ),
    Instruction("DCR D", "\x15",
                fn=lambda env:
                    None
                ),
    Instruction("MVI D,%s", "\x16",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RAL", "\x17",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x18",
                fn=lambda env:
                    None
                ),
    Instruction("DAD D", "\x19",
                fn=lambda env:
                    None
                ),
    Instruction("LDAX D", "\x1A",
                fn=lambda env:
                    None
                ),
    Instruction("DCX D", "\x1B",
                fn=lambda env:
                    None
                ),
    Instruction("INR E", "\x1C",
                fn=lambda env:
                    None
                ),
    Instruction("DCR E", "\x1D",
                fn=lambda env:
                    None
                ),
    Instruction("MVI E,%s", "\x1E",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RAR", "\x1F",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x20",
                fn=lambda env:
                    None
                ),
    Instruction("LXI H,%s", "\x21",
                Operand(None, "d16", 0x02),
                fn=lambda env, d16:
                    None
                ),
    Instruction("SHLD %s", "\x22",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("INX H", "\x23",
                fn=lambda env:
                    None
                ),
    Instruction("INR H", "\x24",
                fn=lambda env:
                    None
                ),
    Instruction("DCR H", "\x25",
                fn=lambda env:
                    None
                ),
    Instruction("MVI H,%s", "\x26",
                Operand(None, "d8", 0x01),
                fn=lambda env, a16:
                    None
                ),
    Instruction("DAA", "\x27",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x28",
                fn=lambda env:
                    None
                ),
    Instruction("DAD H", "\x29",
                fn=lambda env:
                    None
                ),
    Instruction("LHLD %s", "\x2a",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("DCX H", "\x2b",
                fn=lambda env:
                    None
                ),
    Instruction("INR L", "\x2c",
                fn=lambda env:
                    None
                ),
    Instruction("DCR L", "\x2d",
                fn=lambda env:
                    None
                ),
    Instruction("MVI L,%s", "\x2e",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("CMA", "\x2f",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x30",
                fn=lambda env:
                    None
                ),
    Instruction("LXI SP,%s", "\x31",
                Operand(None, "d16", 0x02),
                fn=lambda env, d16:
                    None
                ),
    Instruction("STA %s", "\x32",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("INX SP", "\x33",
                fn=lambda env:
                    None
                ),
    Instruction("INR M", "\x34",
                fn=lambda env:
                    None
                ),
    Instruction("DCR M", "\x35",
                fn=lambda env:
                    None
                ),
    Instruction("MVI M,%s", "\x36",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("STC", "\x37",
                fn=lambda env:
                    None
                ),
    Instruction("*NOP", "\x38",
                fn=lambda env:
                    None
                ),
    Instruction("DAD SP", "\x39",
                fn=lambda env:
                    None
                ),
    Instruction("LDA %s", "\x3A",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("DCX SP", "\x3B",
                fn=lambda env:
                    None
                ),
    Instruction("INR A", "\x3C",
                fn=lambda env:
                    None
                ),
    Instruction("DCR A", "\x3D",
                fn=lambda env:
                    None
                ),
    Instruction("MVI A,%s", "\x3E",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("CMC", "\x3F",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,B", "\x40",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,C", "\x41",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,D", "\x42",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,E", "\x43",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,H", "\x44",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,L", "\x45",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,M", "\x46",
                fn=lambda env:
                    None
                ),
    Instruction("MOV B,A", "\x47",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,B", "\x48",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,C", "\x49",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,D", "\x4A",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,E", "\x4B",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,H", "\x4C",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,L", "\x4D",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,M", "\x4E",
                fn=lambda env:
                    None
                ),
    Instruction("MOV C,A", "\x4F",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,B", "\x50",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,C", "\x51",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,D", "\x52",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,E", "\x53",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,H", "\x54",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,L", "\x55",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,M", "\x56",
                fn=lambda env:
                    None
                ),
    Instruction("MOV D,A", "\x57",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,B", "\x58",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,C", "\x59",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,D", "\x5A",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,E", "\x5B",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,H", "\x5C",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,L", "\x5D",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,M", "\x5E",
                fn=lambda env:
                    None
                ),
    Instruction("MOV E,A", "\x5F",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,B", "\x60",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,C", "\x61",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,D", "\x62",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,E", "\x63",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,H", "\x64",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,L", "\x65",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,M", "\x66",
                fn=lambda env:
                    None
                ),
    Instruction("MOV H,A", "\x67",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,B", "\x68",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,C", "\x69",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,D", "\x6A",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,E", "\x6B",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,H", "\x6C",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,L", "\x6D",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,M", "\x6E",
                fn=lambda env:
                    None
                ),
    Instruction("MOV L,A", "\x6F",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,B", "\x70",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,C", "\x71",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,D", "\x72",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,E", "\x73",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,H", "\x74",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,L", "\x75",
                fn=lambda env:
                    None
                ),
    Instruction("HLT", "\x76",
                fn=lambda env:
                    None
                ),
    Instruction("MOV M,A", "\x77",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,B", "\x78",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,C", "\x79",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,D", "\x7A",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,E", "\x7B",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,H", "\x7C",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,L", "\x7D",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,M", "\x7E",
                fn=lambda env:
                    None
                ),
    Instruction("MOV A,A", "\x7F",
                fn=lambda env:
                    None
                ),
    Instruction("ADD B", "\x80",
                fn=lambda env:
                    None
                ),
    Instruction("ADD C", "\x81",
                fn=lambda env:
                    None
                ),
    Instruction("ADD D", "\x82",
                fn=lambda env:
                    None
                ),
    Instruction("ADD E", "\x83",
                fn=lambda env:
                    None
                ),
    Instruction("ADD H", "\x84",
                fn=lambda env:
                    None
                ),
    Instruction("ADD L", "\x85",
                fn=lambda env:
                    None
                ),
    Instruction("ADD M", "\x86",
                fn=lambda env:
                    None
                ),
    Instruction("ADD A", "\x87",
                fn=lambda env:
                    None
                ),
    Instruction("ADC B", "\x88",
                fn=lambda env:
                    None
                ),
    Instruction("ADC C", "\x89",
                fn=lambda env:
                    None
                ),
    Instruction("ADC D", "\x8A",
                fn=lambda env:
                    None
                ),
    Instruction("ADC E", "\x8B",
                fn=lambda env:
                    None
                ),
    Instruction("ADC H", "\x8C",
                fn=lambda env:
                    None
                ),
    Instruction("ADC L", "\x8D",
                fn=lambda env:
                    None
                ),
    Instruction("ADC M", "\x8E",
                fn=lambda env:
                    None
                ),
    Instruction("ADC A", "\x8F",
                fn=lambda env:
                    None
                ),
    Instruction("SUB B", "\x90",
                fn=lambda env:
                    None
                ),
    Instruction("SUB C", "\x91",
                fn=lambda env:
                    None
                ),
    Instruction("SUB D", "\x92",
                fn=lambda env:
                    None
                ),
    Instruction("SUB E", "\x93",
                fn=lambda env:
                    None
                ),
    Instruction("SUB H", "\x94",
                fn=lambda env:
                    None
                ),
    Instruction("SUB L", "\x95",
                fn=lambda env:
                    None
                ),
    Instruction("SUB M", "\x96",
                fn=lambda env:
                    None
                ),
    Instruction("SUB A", "\x97",
                fn=lambda env:
                    None
                ),
    Instruction("SBB B", "\x98",
                fn=lambda env:
                    None
                ),
    Instruction("SBB C", "\x99",
                fn=lambda env:
                    None
                ),
    Instruction("SBB D", "\x9A",
                fn=lambda env:
                    None
                ),
    Instruction("SBB E", "\x9B",
                fn=lambda env:
                    None
                ),
    Instruction("SBB H", "\x9C",
                fn=lambda env:
                    None
                ),
    Instruction("SBB L", "\x9D",
                fn=lambda env:
                    None
                ),
    Instruction("SBB M", "\x9E",
                fn=lambda env:
                    None
                ),
    Instruction("SBB A", "\x9F",
                fn=lambda env:
                    None
                ),
    Instruction("ANA B", "\xA0",
                fn=lambda env:
                    None
                ),
    Instruction("ANA C", "\xA1",
                fn=lambda env:
                    None
                ),
    Instruction("ANA D", "\xA2",
                fn=lambda env:
                    None
                ),
    Instruction("ANA E", "\xA3",
                fn=lambda env:
                    None
                ),
    Instruction("ANA H", "\xA4",
                fn=lambda env:
                    None
                ),
    Instruction("ANA L", "\xA5",
                fn=lambda env:
                    None
                ),
    Instruction("ANA M", "\xA6",
                fn=lambda env:
                    None
                ),
    Instruction("ANA A", "\xA7",
                fn=lambda env:
                    None
                ),
    Instruction("XRA B", "\xA8",
                fn=lambda env:
                    None
                ),
    Instruction("XRA C", "\xA9",
                fn=lambda env:
                    None
                ),
    Instruction("XRA D", "\xAA",
                fn=lambda env:
                    None
                ),
    Instruction("XRA E", "\xAB",
                fn=lambda env:
                    None
                ),
    Instruction("XRA H", "\xAC",
                fn=lambda env:
                    None
                ),
    Instruction("XRA L", "\xAD",
                fn=lambda env:
                    None
                ),
    Instruction("XRA M", "\xAE",
                fn=lambda env:
                    None
                ),
    Instruction("XRA A", "\xAF",
                fn=lambda env:
                    None
                ),
    Instruction("ORA B", "\xB0",
                fn=lambda env:
                    None
                ),
    Instruction("ORA C", "\xB1",
                fn=lambda env:
                    None
                ),
    Instruction("ORA D", "\xB2",
                fn=lambda env:
                    None
                ),
    Instruction("ORA E", "\xB3",
                fn=lambda env:
                    None
                ),
    Instruction("ORA H", "\xB4",
                fn=lambda env:
                    None
                ),
    Instruction("ORA L", "\xB5",
                fn=lambda env:
                    None
                ),
    Instruction("ORA M", "\xB6",
                fn=lambda env:
                    None
                ),
    Instruction("ORA A", "\xB7",
                fn=lambda env:
                    None
                ),
    Instruction("CMP B", "\xB8",
                fn=lambda env:
                    None
                ),
    Instruction("CMP C", "\xB9",
                fn=lambda env:
                    None
                ),
    Instruction("CMP D", "\xBA",
                fn=lambda env:
                    None
                ),
    Instruction("CMP E", "\xBB",
                fn=lambda env:
                    None
                ),
    Instruction("CMP H", "\xBC",
                fn=lambda env:
                    None
                ),
    Instruction("CMP L", "\xBD",
                fn=lambda env:
                    None
                ),
    Instruction("CMP M", "\xBE",
                fn=lambda env:
                    None
                ),
    Instruction("CMP A", "\xBF",
                fn=lambda env:
                    None
                ),
    Instruction("RNZ", "\xC0",
                fn=lambda env:
                    None
                ),
    Instruction("POP B", "\xC1",
                fn=lambda env:
                    None
                ),
    Instruction("JNZ %s", "\xC2",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("JMP %s", "\xC3",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("CNZ %s", "\xC4",
                Operand(None, "a16", 0x02),
                fn=lambda env:
                    None
                ),
    Instruction("PUSH B", "\xC5",
                fn=lambda env:
                    None
                ),
    Instruction("ADI %s", "\xC6",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 0", "\xC7",
                fn=lambda env:
                    None
                ),
    Instruction("RZ", "\xC8",
                fn=lambda env:
                    None
                ),
    Instruction("RET", "\xC9",
                fn=lambda env:
                    None
                ),
    Instruction("JZ %s", "\xCA",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("*JMP %s", "\xCB",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("CZ %s", "\xCC",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("CALL %s", "\xCD",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("ACI %s", "\xCE",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 1", "\xCF",
                fn=lambda env:
                    None
                ),
    Instruction("RNC", "\xD0",
                fn=lambda env:
                    None
                ),
    Instruction("POP D", "\xD1",
                fn=lambda env:
                    None
                ),
    Instruction("JNC %s", "\xD2",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("OUT %s", "\xD3",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("CNC %s", "\xD4",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("PUSH D", "\xD5",
                fn=lambda env:
                    None
                ),
    Instruction("SUI %s", "\xD6",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 2", "\xD7",
                fn=lambda env:
                    None
                ),
    Instruction("RC", "\xD8",
                fn=lambda env:
                    None
                ),
    Instruction("*RET", "\xD9",
                fn=lambda env:
                    None
                ),
    Instruction("JC %s", "\xDA",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("IN %s", "\xDB",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("CC %s", "\xDC",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("*CALL %s", "\xDD",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("SBI %s", "\xDE",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 3", "\xDF",
                fn=lambda env:
                    None
                ),
    Instruction("RPO", "\xE0",
                fn=lambda env:
                    None
                ),
    Instruction("POP H", "\xE1",
                fn=lambda env:
                    None
                ),
    Instruction("JPO %s", "\xE2",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("XTHL", "\xE3",
                fn=lambda env:
                    None
                ),
    Instruction("CPO %s", "\xE4",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("PUSH H", "\xE5",
                fn=lambda env:
                    None
                ),
    Instruction("ANI %s", "\xE6",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 4", "\xE7",
                fn=lambda env:
                    None
                ),
    Instruction("RPE", "\xE8",
                fn=lambda env:
                    None
                ),
    Instruction("PCHL", "\xE9",
                fn=lambda env:
                    None
                ),
    Instruction("JPE %s", "\xEA",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("XCHG", "\xEB",
                fn=lambda env:
                    None
                ),
    Instruction("CPE %s", "\xEC",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("*CALL %s", "\xED",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("XRI %s", "\xEE",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 5", "\xEF",
                fn=lambda env:
                    None
                ),
    Instruction("RP", "\xF0",
                fn=lambda env:
                    None
                ),
    Instruction("POP PSW", "\xF1",
                fn=lambda env:
                    None
                ),
    Instruction("JP %s", "\xF2",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("DI", "\xF3",
                fn=lambda env:
                    None
                ),
    Instruction("CP %s", "\xF4",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("PUSH PSW", "\xF5",
                fn=lambda env:
                    None
                ),
    Instruction("ORI %s", "\xF6",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 6", "\xF7",
                fn=lambda env:
                    None
                ),
    Instruction("RM", "\xF8",
                fn=lambda env:
                    None
                ),
    Instruction("SPHL", "\xF9",
                fn=lambda env:
                    None
                ),
    Instruction("JM %s", "\xFA",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("EI", "\xFB",
                fn=lambda env:
                    None
                ),
  Instruction("CM %s", "\xFC",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("*CALL %s", "\xFD",
                Operand(None, "a16", 0x02),
                fn=lambda env, a16:
                    None
                ),
    Instruction("CPI %s", "\xFE",
                Operand(None, "d8", 0x01),
                fn=lambda env, d8:
                    None
                ),
    Instruction("RST 7", "\xFF",
                fn=lambda env:
                    None
                )
    ]))




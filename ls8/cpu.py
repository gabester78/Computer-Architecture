"""CPU functionality."""

import sys
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
SP = 7
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # keep track of the address off the current instruction, default is 0
        self.pc = 0  # points to the instruction being executed

        self.ram = [0] * 256

        # variable are called registers and each can hold a sing byte
        self.reg = [0] * 8
        self.sp = 7
        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        self.branchtable[CMP] = self.CMP
        self.branchtable[JMP] = self.jmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne
        self.E = 0
        self.L = 0
        self.G = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.strip()
                        line = line.split('#', 1)[0]
                        line = int(line, 2)
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def jne(self):
        if self.E == 0:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def jeq(self):
        if self.E == 1:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def jmp(self):
        self.pc = self.reg[self.ram[self.pc + 1]]

    def CMP(self):
        reg_a = self.reg[self.ram[self.pc + 1]]
        reg_b = self.reg[self.ram[self.pc + 2]]

        if reg_a == reg_b:
            self.E = 1
        elif reg_a < reg_b:
            self.L = 1
        elif reg_a > reg_b:
            self.G = 1
        self.pc += 3

    def call(self):
        return_addr = self.pc + 2
        self.reg[SP] -= 1
        addr_to_push_to = self.reg[SP]
        self.ram[addr_to_push_to] = return_addr
        reg_num = self.ram[self.pc + 1]
        sub_addr = self.reg[reg_num]
        self.pc = sub_addr

    def ret(self):
        address_pop_from = self.reg[SP]
        return_addr = self.ram[address_pop_from]
        self.reg[SP] += 1
        self.pc = return_addr

    def add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def ldi(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def prn(self):
        register = self.ram_read(self.pc + 1)
        print(self.reg[register])
        self.pc += 2

    def hlt(self):
        self.switch = False

    def mul(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def push(self):
        self.reg[SP] -= 1

        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num]
        push_to = self.reg[SP]
        self.ram[push_to] = value

        self.pc += 2

    def pop(self):
        address_pop_from = self.reg[SP]
        value = self.ram[address_pop_from]

        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value

        self.reg[SP] += 1

        self.pc += 2

    def run(self):
        """Run the CPU."""
        self.switch = True

        while self.switch:
            instruction_register = self.pc
            instruction = self.ram[instruction_register]
            self.branchtable[instruction]()

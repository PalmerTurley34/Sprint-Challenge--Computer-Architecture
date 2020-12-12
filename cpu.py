"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""
    PRN = 0b01000111
    LDI = 0b10000010
    MUL = 0b10100010
    PUSH = 0b01000101
    POP = 0b01000110
    CALL = 0b01010000
    RET = 0b00010001
    ADD = 0b10100000
    sp = 7

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.registers = [0] * 8
        self.pc = 0
        self.branchtable = {}
        self.branchtable[self.PRN] = self.PRN_handle
        self.branchtable[self.LDI] = self.LDI_handle
        self.branchtable[self.MUL] = self.MUL_handle
        self.branchtable[self.PUSH] = self.PUSH_handle
        self.branchtable[self.POP] = self.POP_handle
        self.branchtable[self.CALL] = self.CALL_handle
        self.branchtable[self.RET] = self.RET_handle
        self.branchtable[self.ADD] = self.ADD_handle
        self.registers[self.sp] = 0xf4


    def load(self, program_file):
        """Load a program into memory."""

        address = 0
        program = []
        f = open(program_file)
        line = f.readline()
        while line != '':
            if line[0] in ['0', '1']:
                program.append(int(line[:8], 2))
            line = f.readline() 
        f.close()


        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        IC = self.ram_read(self.pc)
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)
        while IC != HLT:
            self.branchtable[IC](operand_a, operand_b)
            IC = self.ram[self.pc]
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR


    def LDI_handle(self, a, b):
        self.registers[a] = b
        self.pc += 3

    def MUL_handle(self, a, b):
        self.alu('MUL', a, b)
        self.pc += 3

    def ADD_handle(self, a, b):
        self.alu('ADD', a, b)
        self.pc += 3

    def PRN_handle(self, a, b):
        print(self.registers[a])
        self.pc += 2

    def PUSH_handle(self, a, b):
        self.registers[self.sp] -= 1
        self.ram[self.registers[self.sp]] = self.registers[a]
        self.pc += 2

    def POP_handle(self, a, b):
        self.registers[a] = self.ram[self.registers[self.sp]]
        self.registers[self.sp] += 1
        self.pc += 2

    def CALL_handle(self, a, b):
        self.registers[self.sp] -= 1
        self.ram[self.registers[self.sp]] = self.pc + 2
        self.pc = self.registers[a] 

    def RET_handle(self, a, b):
        self.pc = self.ram[self.registers[self.sp]]
        self.registers[self.sp] += 1
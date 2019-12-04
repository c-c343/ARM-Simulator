import sys
import os
from collections import namedtuple

global isBreak
global inputFileName
global outputFileName
isBreak = False


class Disassemble:
    format = ""
    line = ""
    opCode = ""
    instruction = ""
    legString = ""
    ALUImmediate = 0
    address = 0
    altAddress = 0
    opWidth = 0
    shamt = 0
    op = 0
    Rt = 0
    Rm = 0
    Rn = 0
    Rd = 0

    def run(self, line, address):
        self.address = address
        self.line = line[0:32]
        self.format = self.instructionFormat(int(self.line[0:11], 2))
        self.bitCodeSlice()
        self.instruction = self.getOpInustruction()
        self.legString = self.legCode()
        self.printToFile()

    def instructionFormat(self, value):
        if value >= 160 and value <= 191:
            return "B"
        elif value == 1360 or value == 1624 or value == 1690 or value == 1691 \
                or value == 1104 or value == 1112 or value == 1872 or value == 0 \
                or value == 1692:
            return "R"
        elif value == 2038:
            return "BREAK"
        elif value == 2047:
            return "Negative Int"
        elif (value >= 1160 and value <= 1161) or (value >= 1672 and value <= 1673):
            return "I"
        elif value >= 1440 and value <= 1455:
            return "CB"
        elif (value >= 1648 and value <= 1687) or (value >= 1940 and value <= 1943):
            return "IM"
        elif value == 1984 or value == 1986:
            return "D"
        else:
            return "Error"

    def bitCodeSlice(self):
        if self.format == "B":
            self.opCode = self.line[0:6]
            self.altAddress = retInt(self.line[6:33])
            self.opWidth = 6
        elif self.format == "R":
            self.opCode = self.line[0:11]
            self.Rm = int(self.line[11:16], 2)
            self.shamt = int(self.line[16:22], 2)
            self.Rn = int(self.line[22:27], 2)
            self.Rd = int(self.line[27:33], 2)
            self.opWidth = 11
        elif self.format == "D":
            self.opCode = self.line[0:11]
            self.altAddress = retInt(self.line[11:20])
            self.op = int(self.line[20:22], 2)
            self.Rn = int(self.line[22:27], 2)
            self.Rt = int(self.line[27:33], 2)
            self.opWidth = 11
        elif self.format == "I":
            self.opCode = self.line[0:10]
            self.ALUImmediate = retInt(self.line[10:22])
            self.Rn = int(self.line[22:27], 2)
            self.Rd = int(self.line[27:33], 2)
            self.opWidth = 10
        elif self.format == "CB":
            self.opCode = self.line[0:8]
            self.altAddress = retInt(self.line[8:27])
            self.Rt = int(self.line[27:33], 2)
            self.opWidth = 8
        elif self.format == "IW":
            self.opCode = self.line[0:11]
            self.ALUImmediate = retInt(self.line[11:27])
            self.Rd = int(self.line[27:33], 2)
            self.opCode = 11
        elif self.format == "IM":
            self.Rd = int(self.line[27:33], 2)
            self.opCode = self.line[0:9]
            self.ALUImmediate = self.line[11:27]
            self.opWidth = 9
        else:
            self.opWidth = 11

    def getOpInustruction(self):
        if isBreak == True:
            return "NUM"
        elif self.opCode == "000101":
            return "B"
        elif self.opCode == "10001010000":
            return "AND"
        elif self.opCode == "10001011000":
            return "ADD"
        elif self.opCode == "1001000100":
            return "ADDI"
        elif self.opCode == "10101010000":
            return "ORR"
        elif self.opCode == "10110100":
            return "CBZ"
        elif self.opCode == "10110101":
            return "CBNZ"
        elif self.opCode == "11001011000":
            return "SUB"
        elif self.opCode == "1101000100":
            return "SUBI"
        elif self.opCode == "110100101":
            return "MOVZ"
        elif self.opCode == "111100101":
            return "MOVK"
        elif self.opCode == "11010011010":
            return "LSR"
        elif self.opCode == "11010011011":
            return "LSL"
        elif self.opCode == "11111000000":
            return "STUR"
        elif self.opCode == "11111000010":
            return "LDUR"
        elif self.opCode == "11111110110":
            return "Break"
        elif self.opCode == "11111111111":
            return "Negative Int"
        elif self.opCode == "00000000000":
            return "NOP"
        elif self.opCode == "11101010000":
            return "EOR"
        elif self.opCode == "11010011100":
            return "ASR"
        else:
            return "ERROR"

    def legCode(self):
        if self.format == "BREAK":
            global isBreak
            isBreak = True
            return "BREAK"
        elif self.format == "Negative Int":
            return self.line[0:32] + "\t" + str(self.address) + "\t" + str(int(self.line, 2) - (1 << len(self.line)))
        elif self.instruction == "NUM":
            return self.line[0:32] + "\t" + str(self.address) + "\t" + str(int(self.line, 2))
        elif self.format == "B":
            if int(self.line[6:7]):
                return self.format + "\t#" + str(int(self.line[6:32], 2) - (1 << 26))
            else:
                return self.format + "\t#" + str(int(self.line[6:32], 2))
        elif self.instruction == "NOP":
            return "NOP"
        elif self.format == "R":
            if self.instruction == "LSR" or self.instruction == "LSL" or self.instruction == "ASR":
                return self.instruction + "\t" + "R" + str(self.Rd) + ", " + "R" + str(self.Rn) + ", #" + str(
                    self.shamt)
            else:
                return self.instruction + "\t" + "R" + str(self.Rd) + ", " + "R" + str(self.Rn) + ", " + "R" + str(
                    self.Rm)
        elif self.format == "I":
            if int(self.line[10:11]):
                return self.instruction + "\t" + "R" + str(self.Rd) + ", " + "R" + str(self.Rn) + ", " + "#" + str(
                    int(self.line[self.opWidth:self.opWidth + 12], 2) - (1 << 12))
            else:
                return self.instruction + "\t" + "R" + str(self.Rd) + ", " + "R" + str(self.Rn) + ", " + "#" + str(
                    int(self.line[self.opWidth:self.opWidth + 12], 2))
        elif self.format == "CB":
            if int(self.line[8:9]):
                return self.instruction + "\t" + "R" + str(self.Rt) + ", " + "#" + str(
                    int(self.line[self.opWidth:self.opWidth + 19], 2) - (1 << 19))
            else:
                return self.instruction + "\t" + "R" + str(self.Rt) + ", " + "#" + str(
                    int(self.line[self.opWidth:self.opWidth + 19], 2))
        elif self.format == "IM":
            if self.line[self.opWidth:self.opWidth + 2] == "00":
                shift_amount = "0"
            elif self.line[self.opWidth:self.opWidth + 2] == "01":
                shift_amount = "16"
            elif self.line[self.opWidth:self.opWidth + 2] == "10":
                shift_amount = "32"
            elif self.line[self.opWidth:self.opWidth + 2] == "11":
                shift_amount = "48"
            return self.instruction + "\t" + "R" + str(self.Rd) + ", " + \
                   str(int(self.line[11:27], 2)) + ", LSL " + shift_amount
        elif self.format == "D":
            return self.instruction + "\t" + "R" + str(self.Rt) + ", " + "[R" + str(self.Rn) + ", #" + \
                   str(int(self.line[11:20], 2)) + "]"
        else:
            return self.instruction + ": opCode" + self.line[0:11] + " ;format: " + self.format

    def printToFile(self):
        if self.format != "Negative Int" and self.instruction != "NUM":
            outFile.write(self.line[0:8] + " " + self.line[8:11] + " " \
                          + self.line[11:16] + " " + self.line[16:21] + " " + self.line[21:26] + " " \
                          + self.line[26:32] + "\t" + str(self.address) + "\t" + self.legString + "\n")
        else:
            outFile.write(self.legString + "\n")

class Register:
    register = ""
    data = 0

class PreIssueBuffer():
    preIssueBuffer = []
    def __init__(self):
        for i in range(4):
            self.preIssueBuffer.append(Disassemble())

class ALUQueue():
    preALUQueue = []
    postALUQueue = []
    def __init__(self):
        for i in range(2):
            self.preALUQueue.append(Disassemble())
        for i in range(1):
            legCode = ""
            entry = [legCode, Register()]
            self.postALUQueue.append(entry)


class MEMQueue():
    preMEMQueue = []
    postMEMQueue = []
    def __init__(self):
        for i in range(2):
            self.preMEMQueue.append(Disassemble())
        for i in range(1):
            legCode = ""
            entry = [legCode, Register()]
            self.postMEMQueue.append(entry)

class IF():
    def __init__(self):
        for i in range(2):
            self.run()
    def run(self):
        if Sim.pc != Sim.breakIndex:
            if Sim.simList[Sim.pc].format == "B":
                Sim.pc += Sim.simList[Sim.pc].altAddress
            elif Sim.simList[Sim.pc].format == "CB":
                if Sim.simList[Sim.pc].instruction == "CBNZ":
                    if Sim.regList[Sim.simList[Sim.pc].Rt].data != 0:
                        Sim.pc += Sim.simList[Sim.pc].altAddress
                    else:
                        Sim.pc += 1
                if Sim.simList[Sim.pc].instruction == "CBZ":
                    if Sim.regList[Sim.simList[Sim.pc].Rt].data == 0:
                        Sim.pc += Sim.simList[Sim.pc].altAddress
                    else:
                        Sim.pc += 1
            if self.availablility() >= 2:
                self.insertToBuffer(Sim.simList[Sim.pc])
                Sim.pc += 1

            elif self.availablility() == 1:
                self.insertToBuffer(Sim.simList[Sim.pc])
                Sim.pc += 1
    def availablility(self):
        count = 0
        if len(Sim.preIssueBuffer[3].legString) == 0:
            count += 1
        if len(Sim.preIssueBuffer[2].legString) == 0:
            count += 1
        if len(Sim.preIssueBuffer[1].legString) == 0:
            count += 1
        if len(Sim.preIssueBuffer[0].legString) == 0:
            count += 1
        return count
    def firstAvailable(self):
        if len(Sim.preIssueBuffer[0].legString) == 0:
            return 0
        if len(Sim.preIssueBuffer[1].legString) == 0:
            return 1
        if len(Sim.preIssueBuffer[2].legString) == 0:
            return 2
        if len(Sim.preIssueBuffer[3].legString) == 0:
            return 3
    def insertToBuffer(self, instance):
        Sim.preIssueBuffer[self.firstAvailable()] = instance

class Issue():
    def __init__(self):
        for i in range(2):
            self.run()
    def run(self):
        instance = Sim.preIssueBuffer[0]
        if not (self.isHazard(instance)):
            if self.goesToALU(instance) and self.preALUAvailability() >= 1:
                self.insertALU(instance)
                self.removeInstance()
            elif self.goesToMEM(instance) and self.preMEMAvailability() >= 1:
                self.insertMEM(instance)
                self.removeInstance()
    def isHazard(self, instance):
        if instance.format == "R":
            check1 = self.regCheck(instance.Rn)
            check2 = self.regCheck(instance.Rm)
            if check1 or check2:
                return True
            else:
                return False
        elif instance.format == "I" or instance.format == "D":
            return self.regCheck(instance.Rn)
        elif instance.format == "IM":
            return self.regCheck(instance.Rd)
        return False
    def regCheck(self, register):
        for i in range(2):
            if Sim.preALUQueue[i].format == "R" or Sim.preALUQueue[i].format == "I" or Sim.preALUQueue[i].format == "IM":
                if Sim.preALUQueue[i].Rd == register:
                    return True
            elif Sim.preMEMQueue[i].format == "D":
                if Sim.preMEMQueue[i].Rd == register:
                    return True
        if Sim.postALUQueue[0][1].register == register or Sim.postALUQueue[0][1].register == register or Sim.postALUQueue[0][1].register == register:
            return True
        elif Sim.postMEMQueue[0][1].register == register:
            return True
        return False

    def removeInstance(self):
        if self.firstAvailable() == -1:
            for i in range(3):
                Sim.preIssueBuffer[i] = Sim.preIssueBuffer[i + 1]
            Sim.preIssueBuffer[3] = Disassemble()
        else:
            for i in range(self.firstAvailable()):
                Sim.preIssueBuffer[i] = Sim.preIssueBuffer[i+1]

    def insertMEM(self, instance):
        Sim.preMEMQueue[self.preMEMFirstAvailable()] = instance
    def insertALU(self, instance):
        Sim.preALUQueue[self.preALUFirstAvailable()] = instance
    def preALUFirstAvailable(self):
        if len(Sim.preALUQueue[0].legString) == 0:
            return 0
        elif len(Sim.preALUQueue[1].legString) == 0:
            return 1
    def preALUAvailability(self):
        if len(Sim.preALUQueue[0].legString) == 0:
            return 2
        elif len(Sim.preALUQueue[1].legString) == 0:
            return 1
        else:
            return 0
    def preMEMFirstAvailable(self):
        if len(Sim.preMEMQueue[0].legString) == 0:
            return 0
        elif len(Sim.preMEMQueue[1].legString) == 0:
            return 1
    def preMEMAvailability(self):
        if len(Sim.preMEMQueue[0].legString) > 0:
            return 2
        elif len(Sim.preMEMQueue[1].legString) > 0:
            return 1
        else:
            return 0
    def preMEMAvailability(self):
        if len(Sim.preMEMQueue[0].legString) == 0:
            return 2
        elif len(Sim.preMEMQueue[1].legString) == 0:
            return 1
        else:
            return 0
    def goesToALU(self, instance):
        if instance.format == "R" or instance.format == "I" or instance.format == "IM":
            return True
        else:
            return False
    def goesToMEM(self, instance):
        if instance.format == "D":
            return True
        else:
            return False
    def firstAvailable(self):
        if len(Sim.preIssueBuffer[0].legString) == 0:
            return 0
        if len(Sim.preIssueBuffer[1].legString) == 0:
            return 1
        if len(Sim.preIssueBuffer[2].legString) == 0:
            return 2
        if len(Sim.preIssueBuffer[3].legString) == 0:
            return 3
        else:
            return -1
class MEM():
    instance = Disassemble()
    def __init__(self):
        self.run()
    def run(self):
        entry = Register()
        self.instance = Sim.preMEMQueue[0]
        Sim.preMEMQueue[0] = Sim.preMEMQueue[1]
        Sim.preMEMQueue[1] = Disassemble()
        entry.register = self.instance.Rt
        Sim.postMEMQueue[0][0] = self.instance.legString
        if self.instance.format == "D":
            if self.instance.instruction == "LDUR":
                entry.data = Sim.dataList[
                    ((Sim.regList[self.instance.Rn].data + self.instance.altAddress * \
                      4 - Sim.simList[Sim.breakIndex - 1].address) / 4) - 1]
            if self.instance.instruction == "STUR":
                while (len(Sim.dataList) < (Sim.regList[self.instance.Rn].data + self.instance.altAddress *
                                             4 - Sim.simList[Sim.breakIndex - 1].address) / 4):
                    for index in range(8):
                        Sim.dataList.append(0)
                Sim.dataList[((Sim.regList[self.instance.Rn].data + self.instance.altAddress *
                                4 - Sim.simList[Sim.breakIndex - 1].address) / 4) - 1] = Sim.regList[self.instance.Rt].data
        Sim.postMEMQueue[0][1] = entry

class ALU():
    instance = Disassemble()
    def __init__(self):
        self.run()
    def run(self):
        self.instance = Sim.preALUQueue[0]
        Sim.preALUQueue[0] = Sim.preALUQueue[1]
        Sim.preALUQueue[1] = Disassemble()
        Sim.postALUQueue[0][1].register = self.instance.Rd
        Sim.postALUQueue[0][0] = self.instance.legString
        if self.instance.format == "R":
            if self.instance.instruction == "LSR":
                Sim.postALUQueue[0][1].data = rshift(Sim.regList[self.instance.Rn].data,
                                                                 self.instance.shamt)
            elif self.instance.instruction == "LSL":
                Sim.postALUQueue[0][1].data = lshift(Sim.regList[self.instance.Rn].data,
                                                                 self.instance.shamt)
            elif self.instance.instruction == "AND":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data & Sim.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "ADD":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data + Sim.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "ORR":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data | Sim.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "SUB":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data - Sim.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "EOR":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data ^ Sim.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "ASR":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data >> self.instance.shamt
        elif self.instance.format == "I":
            if self.instance.instruction == "ADDI":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data + self.instance.ALUImmediate
            if self.instance.instruction == "SUBI":
                Sim.postALUQueue[0][1].data = Sim.regList[self.instance.Rn].data - self.instance.ALUImmediate
        elif self.instance.format == "IM":
            if self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "00":
                shift_amount = 0
            elif self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "01":
                shift_amount = 16
            elif self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "10":
                shift_amount = 32
            elif self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "11":
                shift_amount = 48
            if self.instance.instruction == "MOVZ":
                Sim.postALUQueue[0][1].data = lshift(int(self.instance.line[11:27], 2), shift_amount)

            else:
                mask = 0xFFFF << shift_amount
                data = Sim.regList[self.instance.Rd].data
                data = data & ~mask
                data = data | int(self.instance.ALUImmediate, 2) << shift_amount
                Sim.postALUQueue[0].data = data

class WB():
    def __init__(self):
        self.run()
    def run(self):
        if len(Sim.postMEMQueue[0][0]) > 0:
            Sim.regList[Sim.postMEMQueue[0][1].register].data = Sim.postMEMQueue[0][1].data
            memQ = MEMQueue()
            Sim.postMEMQueue = memQ.postMEMQueue
        if len(Sim.postALUQueue[0][0]) > 0:
            Sim.regList[int(Sim.postALUQueue[0][1].register)].data = Sim.postALUQueue[0][1].data
            aluQ = ALUQueue()
            Sim.postALUQueue = aluQ.postALUQueue
class State:
    cycle = ""
    instance = Disassemble()
    dataList = []
    breakIndex = 0
    simList = []
    pc = 0

    def run(self, cycle, instance, dataList, breakIndex, simList):
        self.simList = simList
        self.breakIndex = breakIndex
        self.dataList = dataList
        self.instance = instance
        self.cycle = cycle
        self.process()
        if self.instance.format != "B" and self.instance.format != "CB":
            self.pc = 1

    def process(self):
        if self.instance.format == "R":
            if self.instance.instruction == "LSR":
                Simulate.regList[self.instance.Rd].data = rshift(Simulate.regList[self.instance.Rn].data,
                                                                 self.instance.shamt)
            elif self.instance.instruction == "LSL":
                Simulate.regList[self.instance.Rd].data = lshift(Simulate.regList[self.instance.Rn].data,
                                                                 self.instance.shamt)
            elif self.instance.instruction == "AND":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data & Simulate.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "ADD":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data + Simulate.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "ORR":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data | Simulate.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "SUB":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data - Simulate.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "EOR":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data ^ Simulate.regList[
                    self.instance.Rm].data
            elif self.instance.instruction == "ASR":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data >> self.instance.shamt
        elif self.instance.format == "I":
            if self.instance.instruction == "ADDI":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data + self.instance.ALUImmediate
            if self.instance.instruction == "SUBI":
                Simulate.regList[self.instance.Rd].data = Simulate.regList[self.instance.Rn].data - self.instance.ALUImmediate
        elif self.instance.format == "B":
            self.pc += self.instance.altAddress
        elif self.instance.format == "CB":
            if self.instance.instruction == "CBNZ":
                if Simulate.regList[self.instance.Rt].data != 0:
                    self.pc += self.instance.altAddress
                else:
                    self.pc = 1
            if self.instance.instruction == "CBZ":
                if Simulate.regList[self.instance.Rt].data == 0:
                    self.pc += self.instance.altAddress
                else:
                    self.pc = 1
        elif self.instance.format == "IM":
            if self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "00":
                shift_amount = 0
            elif self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "01":
                shift_amount = 16
            elif self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "10":
                shift_amount = 32
            elif self.instance.line[self.instance.opWidth:self.instance.opWidth + 2] == "11":
                shift_amount = 48
            if self.instance.instruction == "MOVZ":
                Simulate.regList[self.instance.Rd].data = lshift(int(self.instance.line[11:27], 2), shift_amount)

            else:
                mask = 0xFFFF << shift_amount
                data = Simulate.regList[self.instance.Rd].data
                data = data & ~mask
                data = data | int(self.instance.ALUImmediate, 2) << shift_amount
                Simulate.regList[self.instance.Rd].data = data
        elif self.instance.format == "D":
            if self.instance.instruction == "LDUR":
                Simulate.regList[self.instance.Rt].data = self.dataList[
                    ((Simulate.regList[self.instance.Rn].data + self.instance.altAddress * \
                      4 - self.simList[self.breakIndex - 1].address) / 4) - 1]
            if self.instance.instruction == "STUR":
                while (len(self.dataList) < (Simulate.regList[self.instance.Rn].data + self.instance.altAddress *
                                             4 - self.simList[self.breakIndex - 1].address) / 4):
                    for index in range(8):
                        self.dataList.append(0)
                self.dataList[((Simulate.regList[self.instance.Rn].data + self.instance.altAddress * \
                                4 - self.simList[self.breakIndex - 1].address) / 4) - 1] = Simulate.regList[
                    self.instance.Rt].data

class Cache:
    set = []
    def __init__(self):
        for i in range(4):
            entryL = []
            for i in range(2):
                LRUbits = [0, 0, 0]
                data = [0, 0]
                entry = [LRUbits, data]
                entryL.append(entry)
            self.set.append(entryL)

class Simulate:
    cycle = 1
    pc = 0
    staddress = 96
    address = staddress
    breakIndex = 0
    simList = []
    regList = []
    dataList = []
    state = State()
    cache = Cache()
    pIssueBuffer = PreIssueBuffer()
    ALUQ = ALUQueue()
    MEMEQ = MEMQueue()
    preIssueBuffer = pIssueBuffer.preIssueBuffer
    preALUQueue = ALUQ.preALUQueue
    postALUQueue = ALUQ.postALUQueue
    preMEMQueue = MEMEQ.preMEMQueue
    postMEMQueue = MEMEQ.postMEMQueue

    def run(self):
        myfile = open(inputFileName, "r")
        global outSim
        outSim = open(outputFileName + "_sim.txt", "w+")
        global outFile
        outFile = open(outputFileName + "_dis.txt", "w+")
        for index in range(32):
            reg = Register()
            reg.register = "R" + str(index)
            reg.data = 0
            self.regList.append(reg)
        index = 1
        for line in myfile:
            dis = Disassemble()
            dis.run(line, self.address)
            if line[0:11] == "11111110110":
                self.breakIndex = index - 1
            self.address += 4
            index += 1
            self.simList.append(dis)
        for instance in self.simList[self.breakIndex:]:
            if instance.line[0:1] == "1":
                self.dataList.append(int(instance.line, 2) - (1 << len(instance.line)))
            else:
                self.dataList.append(int(instance.line, 2))
  #      self.cache.set[1][1][1][0] = self.simList[0].line
  #      while 0 <= self.pc < len(self.simList) and self.pc < self.breakIndex + 1:
   #         self.state = State()
   #         self.state.run(self.cycle, self.simList[self.pc], self.dataList, self.breakIndex, self.simList)
   #         self.printState()
   #         if self.simList[self.pc].line[0:11] == "11111110110":
   #             break
    #        self.cycle += 1

        for i in range(13):
            self.printState()
            WB()
            MEM()
            ALU()
            Issue()
            IF()
            self.cycle += 1

    def printState(self):
        for index in range(21):
            outSim.write("-")

        outSim.write("\nCycle:" + str(self.cycle) + "\t\n")
        outSim.write("\nPre-Issue Buffer:\n" +
                     "\tEntry 0:\t" + self.preIssueBuffer[0].legString +
                     "\n\tEntry 1:\t" + self.preIssueBuffer[1].legString +
                     "\n\tEntry 2:\t" + self.preIssueBuffer[2].legString +
                     "\n\tEntry 3:\t" + self.preIssueBuffer[3].legString +
                     "\nPre_ALU Queue:\n" +
                     "\tEntry 0:\t" + self.preALUQueue[0].legString +
                     "\n\tEntry 1:\t" + self.preALUQueue[1].legString +
                     "\nPost_ALU Queue:\n" +
                     "\tEntry 0:\t" + self.postALUQueue[0][0] +
                     "\nPre_MEM Queue:\n" +
                     "\tEntry 0:\t" + self.preMEMQueue[0].legString +
                     "\n\tEntry 1:\t" + self.preMEMQueue[1].legString +
                     "\nPost_MEM Queue:\n" +
                     "\tEntry 0:\t" + self.postMEMQueue[0][0])

        outSim.write("\n" + "\nRegisters\n" + "R00:\t")
        for index in range(8):
            outSim.write(str(self.regList[index].data) + "\t")
        outSim.write("\n" + "R08: \t")
        for index in range(8, 16):
            outSim.write(str(self.regList[index].data) + "\t")
        outSim.write("\n" + "R16: \t")
        for index in range(16, 24):
            outSim.write(str(self.regList[index].data) + "\t")
        outSim.write("\n" + "R24: \t")
        for index in range(16, 24):
            outSim.write(str(self.regList[index].data) + "\t")

        outSim.write("\n\nCache\nSet 0: LRU=0*\n" +
                     "\tEntry 0:[(" + str(self.cache.set[0][0][0][0]) + "," +
                     str(self.cache.set[0][0][0][1]) + "," + str(self.cache.set[0][0][0][2]) + ")<" +
                     str(self.cache.set[0][0][1][0]) + "," + str(self.cache.set[0][0][1][1]) + ">]" +
                     "\n" +
                     "\tEntry 1:[(" + str(self.cache.set[0][1][0][0]) + "," +
                     str(self.cache.set[0][1][0][1]) + "," + str(self.cache.set[0][1][0][0]) + ")<" +
                     str(self.cache.set[0][1][1][0]) + "," + str(self.cache.set[0][1][1][1]) + ">]" +
                     "\n" +
                     "Set 1: LRU=0*\n" +
                     "\tEntry 0:[(" + str(self.cache.set[1][0][0][0]) + "," +
                     str(self.cache.set[1][0][0][1]) + "," + str(self.cache.set[1][0][0][2]) + ")<" +
                     str(self.cache.set[1][0][1][0]) + "," + str(self.cache.set[1][0][1][1]) + ">]" +
                     "\n" +
                     "\tEntry 1:[(" + str(self.cache.set[1][1][0][0]) + "," +
                     str(self.cache.set[1][1][0][1]) + "," + str(self.cache.set[1][1][0][0]) + ")<" +
                     str(self.cache.set[1][1][1][0]) + "," + str(self.cache.set[1][1][1][1]) + ">]" +
                     "\n" +
                     "Set 2: LRU=0*\n" +
                     "\tEntry 0:[(" + str(self.cache.set[2][0][0][0]) + "," +
                     str(self.cache.set[2][0][0][1]) + "," + str(self.cache.set[2][0][0][2]) + ")<" +
                     str(self.cache.set[2][0][1][0]) + "," + str(self.cache.set[2][0][1][1]) + ">]" +
                     "\n" +
                     "\tEntry 1:[(" + str(self.cache.set[2][1][0][0]) + "," +
                     str(self.cache.set[2][1][0][1]) + "," + str(self.cache.set[2][1][0][0]) + ")<" +
                     str(self.cache.set[2][1][1][0]) + "," + str(self.cache.set[2][1][1][1]) + ">]" +
                     "\n" +
                     "Set 3: LRU=0*\n" +
                     "\tEntry 0:[(" + str(self.cache.set[3][0][0][0]) + "," +
                     str(self.cache.set[3][0][0][1]) + "," + str(self.cache.set[3][0][0][2]) + ")<" +
                     str(self.cache.set[3][0][1][0]) + "," + str(self.cache.set[3][0][1][1]) + ">]" +
                     "\n" +
                     "\tEntry 1:[(" + str(self.cache.set[3][1][0][0]) + "," +
                     str(self.cache.set[3][1][0][1]) + "," + str(self.cache.set[3][1][0][0]) + ")<" +
                     str(self.cache.set[3][1][1][0]) + "," + str(self.cache.set[3][1][1][1]) + ">]" +
                     "\n"
                     )

        outSim.write("\nData:")
        if self.dataList:
            index = 0
            for data in self.dataList:
                if index == 0 or index % 8 == 0:
                    outSim.write("\n" + str((self.simList[self.breakIndex - 1].address + index * 4) + 4) + ":")
                outSim.write(str(data) + "\t")
                index += 1
        outSim.write("\n")

def rshift(val, n):
    return (val % 0x100000000) >> n


def lshift(val, n):
    return (val % 0x100000000) << n


def ashiftR(val, n):
    if bin(val)[0:1] == "-":
        mask = 1 << len(str("{0:b}".format(val))[1:]) - 1

        for i in range(n):
            temp = rshift(mask, 1)
            mask = temp | mask
        print val
        print n
        print bin(val)
        print bin(val >> n)
        data = rshift(int(("{0:b}".format(val))[1:], 2), n)
        data = data | mask
        data = -data
        return data
    else:
        newBin = bin(val)[2:len(bin(val)[2:]) - n + 2]
        shiftBIn = "0b"
        for i in range(n):
            shiftBIn = shiftBIn + "1"
        newBin = shiftBIn + newBin
        return retInt(newBin)


def retInt(bin):
    if int(bin[0:1]):
        return int(bin, 2) - (1 << len(bin))
    else:
        return int(bin, 2)


for i in range(len(sys.argv)):
    if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
        inputFileName = sys.argv[i + 1]
        print inputFileName
    elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
        outputFileName = sys.argv[i + 1]
        print outputFileName + "_dis.txt"
        print outputFileName + "_sim.txt"
if __name__ == "__main__":
    global Sim
    Sim = Simulate()
    Sim.run()

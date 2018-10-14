import os, struct
import tkinter as tk
from tkinter import filedialog

def find_name(f, name_pos):
    name = b""
    char = f[name_pos:name_pos + 1]
    i = 1
    while char != b"\x00":
        name += char
        if name_pos + i == len(f): break
        char = f[name_pos + i:name_pos + i + 1]
        i += 1
    return(name.decode("utf-8"))

def extract_files(filename):
    root = tk.Tk()
    root.withdraw()
    if filename:
        with open(filename, "rb") as inf:
            inb = inf.read()
            inf.close()
        wiiu = False
        switch = False
        if inb[:8] == b'FRES    ':
            switch = True
        elif inb[:4] == b'FRES':
            wiiu = True
        if wiiu:
            bom = ">" if inb[8:0xA] == b'\xFE\xFF' else "<"
            endianness = {">": "Big", "<": "Little"}
            pos = struct.unpack(bom + "i", inb[0x4C:0x50])[0]
            pos += 0x4C
            size = struct.unpack(bom + "I", inb[pos:pos+4])[0]
            count = struct.unpack(bom + "i", inb[pos+4:pos+8])[0]
            if pos - 0x4C:
                for i in range(count + 1):
                    name_pos = struct.unpack(bom + "i", inb[pos+16+(0x10*i):pos+20+(0x10*i)])[0]
                    data_pos = struct.unpack(bom + "i", inb[pos+20+(0x10*i):pos+24+(0x10*i)])[0]
                    if data_pos in [0, 0xFFFFFFFF]:
                        name = ""
                    else:
                        name_pos += pos + 8 + (0x10*i) + 8
                        data_pos += pos + 8 + (0x10*i) + 12
                        pos = data_pos
                        data_pos = struct.unpack(bom + "i", inb[pos:pos+4])[0] + pos
                        dataSize = struct.unpack(bom + "I", inb[pos+4:pos+8])[0]
                        data = inb[data_pos:data_pos + dataSize]
                        name = find_name(inb, name_pos)
                        folder = os.path.dirname(os.path.abspath(filename))
                        with open(folder + "/" + name, "wb+") as output:
                            output.write(data)
            else:
                print("No Embedded files found.")
        elif switch:
            bom = ">" if inb[0xC:0xE] == b'\xFE\xFF' else "<"
            endianness = {">": "Big", "<": "Little"}
            startoff = struct.unpack(bom + "q", inb[0x98:0xA0])[0]
            count = struct.unpack(bom + "q", inb[0xC8:0xD0])[0]
            if not count:
                print("No Embedded files found.")
            else:
                namesoff = struct.unpack(bom + "q", inb[0xA0:0xA8])[0] + 0x20
                for i in range(count):
                    fileoff = struct.unpack(bom + "q", inb[startoff + i * 16:startoff + 8 + i * 16])[0]
                    dataSize = struct.unpack(bom + "q", inb[startoff + 8 + i * 16:startoff + 16 + i * 16])[0]
                    data = inb[fileoff:fileoff + dataSize]
                    nameoff = struct.unpack(bom + "q", inb[namesoff + i * 16:namesoff + 8 + i * 16])[0]
                    nameSize = struct.unpack(bom + 'H', inb[nameoff:nameoff + 2])[0]
                    name = inb[nameoff + 2:nameoff + 2 + nameSize].decode('utf-8')
                    folder = os.path.dirname(os.path.abspath(filename))
                    with open(folder + "/" + name, "wb+") as output:
                        output.write(data)
        else:
            print("Unable to recognize the BFRES file!")
    return 1

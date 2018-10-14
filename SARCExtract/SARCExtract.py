import os
import sys
import struct
from .libyaz0 import decompress as Yaz0Dec

def uint8(data, pos, bom):
    return struct.unpack(bom + "B", data[pos:pos + 1])[0]

def uint16(data, pos, bom):
    return struct.unpack(bom + "H", data[pos:pos + 2])[0]

def uint32(data, pos, bom):
    return struct.unpack(bom + "I", data[pos:pos + 4])[0]

def bytes_to_string(data, offset=0, charWidth=1, encoding='utf-8'):
    end = data.find(b'\0' * charWidth, offset)
    if end == -1:
        return data[offset:].decode(encoding)
    return data[offset:end].decode(encoding)

def sarc_extract(data, mode, fn):
    pos = 6
    name, ext = os.path.splitext(fn)
    if mode == 1:
        magic1 = data[0:4]
        if magic1 != b"SARC":
            with open(name + ".bin", "wb") as f:
                f.write(data)
    order = uint16(data, pos, ">")
    pos += 6
    if order == 0xFEFF:
        bom = ">"
    elif order == 0xFFFE:
        bom = "<"
    else:
        sys.exit(1)
    doff = uint32(data, pos, bom)
    pos += 8
    magic2 = data[pos:pos + 4]
    pos += 6
    assert magic2 == b"SFAT"
    node_count = uint16(data, pos, bom)
    pos += 6
    nodes = []
    for x in range(node_count):
        pos += 8
        srt = uint32(data, pos, bom)
        pos += 4
        end = uint32(data, pos, bom)
        pos += 4
        nodes.append([srt, end])
    magic3 = data[pos:pos + 4]
    pos += 8
    assert magic3 == b"SFNT"
    strings = []
    no_names = 0
    if bytes_to_string(data[pos:]) == "":
        no_names = 1
        for x in range(node_count):
            strings.append("file" + str(x))
    else:
        for x in range(node_count):
            string = bytes_to_string(data[pos:])
            pos += len(string)
            while (data[pos]) == 0:
                pos += 1
            strings.append(string)
    try:
        os.mkdir(name)
    except OSError:
        print("Folder already exists, continuing....")
    if no_names:
        print("No names found. Trying to guess the file names...")
    bntx_count = 0
    bnsh_count = 0
    flan_count = 0
    flyt_count = 0
    flim_count = 0
    gtx_count  = 0
    sarc_count = 0
    szs_count  = 0
    file_count = 0
    for x in range(node_count):
        filename = os.path.join(name, strings[x])
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        start, end = (doff + nodes[x][0]), (doff + nodes[x][1])
        filedata = data[start:end]
        if no_names:
            if filedata[0:4] == b"BNTX":
                filename = name + "/" + "bntx" + str(bntx_count) + ".bntx"
                bntx_count += 1
            elif filedata[0:4] == b"BNSH":
                filename = name + "/" + "bnsh" + str(bnsh_count) + ".bnsh"
                bnsh_count += 1
            elif filedata[0:4] == b"FLAN":
                filename = name + "/" + "bflan" + str(flan_count) + ".bflan"
                flan_count += 1
            elif filedata[0:4] == b"FLYT":
                filename = name + "/" + "bflyt" + str(flyt_count) + ".bflyt"
                flyt_count += 1
            elif filedata[-0x28:-0x24] == b"FLIM":
                filename = name + "/" + "bflim" + str(flim_count) + ".bflim"
                flim_count += 1
            elif filedata[0:4] == b"Gfx2":
                filename = name + "/" + "gtx" + str(gtx_count) + ".gtx"
                gtx_count += 1
            elif filedata[0:4] == b"SARC":
                filename = name + "/" + "sarc" + str(sarc_count) + ".sarc"
                sarc_count += 1
            elif filedata[0:4] == b"Yaz0":
                filename = name + "/" + "szs" + str(szs_count) + ".szs"
                szs_count += 1
            else:
                filename = name + "/" + "file" + str(file_count)
                file_count += 1
        with open(filename, "wb") as f:
            f.write(filedata)

def extract_szs(fname):
    with open(fname, "rb") as f:
        data = f.read()
    magic = data[0:4]
    if magic == b"Yaz0":
        decompressed = Yaz0Dec(data)
        sarc_extract(decompressed, 1, fname)
    elif magic == b"SARC":
        sarc_extract(data, 0, fname)
    return 1

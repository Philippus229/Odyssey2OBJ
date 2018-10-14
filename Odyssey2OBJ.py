import byml, os, ntpath, subprocess, shutil, embed_extract
from tkinter.filedialog import askopenfilename, askdirectory
from SARCExtract import SARCExtract
from bntx_extract import bntx_extract

class OBJ:
    def __init__(self):
        self.obj = []
        self.mtl = []

class OBJGroup:
    def __init__(self):
        self.objs = []
        self.obj_count = 0
        self.v_count = 0
        self.vt_count = 0
        self.vn_count = 0

    def save(self, objpath, mtlpath):
        with open(objpath, "w") as f:
            f.truncate(0)
            for obj in self.objs:
                for line in obj.obj:
                    f.write(line)
            f.close()
        with open(mtlpath, "w") as f:
            f.truncate(0)
            for obj in self.objs:
                for line in obj.mtl:
                    f.write(line)
            f.close()
        if not os.path.isdir("tex"):
            os.mkdir("tex")
        for line in open(mtlpath, "r").readlines():
            if line.startswith("map_Kd"):
                try:
                    shutil.copy(os.path.join("models", line.split()[1]), line.split()[1])
                except:
                    print("Could not copy file " + os.path.join("models", line.split()[1]) + " to " + line.split()[1])

    def get_count(self, string):
        while self.obj_count < len(self.objs):
            for line in self.objs[self.obj_count].obj:
                if line.startswith("v "):
                    self.v_count += 1
                elif line.startswith("vt "):
                    self.vt_count += 1
                elif line.startswith("vn "):
                    self.vn_count += 1
            self.obj_count += 1
        if string == "v ":
            return self.v_count
        elif string == "vt ":
            return self.vt_count
        elif string == "vn ":
            return self.vn_count

def add_to_obj(in_obj, out_obj, obj_dir, obj_data, out_name, obj_group):
    og = obj_group
    tmp_obj = OBJ()
    tmp_obj.obj.append("o " + out_name + "\n")
    for line in open(in_obj, "r").readlines():
        if line.startswith("v "):
            values = line.split()
            v = list(map(float, values[1:4]))
            v = [v[0]*obj_data[2][0]+obj_data[0][0],
                 v[1]*obj_data[2][1]+obj_data[0][1],
                 v[2]*obj_data[2][2]+obj_data[0][2]]
            tmp_obj.obj.append("v " + str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")
        elif line.startswith("vn "):
            values = line.split()
            v = list(map(float, values[1:4]))
            v = [v[0]*obj_data[2][0]+obj_data[0][0],
                 v[1]*obj_data[2][1]+obj_data[0][1],
                 v[2]*obj_data[2][2]+obj_data[0][2]]
            tmp_obj.obj.append("vn " + str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")
        elif line.startswith("vt "):
            tmp_obj.obj.append(line)
        elif line.startswith("usemtl") or line.startswith("usemat"):
            tmp_obj.obj.append(line)
        elif line.startswith("mtllib"):
            try:
                tmp_obj.mtl.append(open(os.path.join(obj_dir, line.split()[1]), "r").read() + "\n")
            except:
                print("Could not open file: " + os.path.join(obj_dir, line.split()[1]))
            tmp_obj.obj.append("mtllib " + out_obj[:-3] + "mtl\n")
        elif line.startswith("f"):
            new_f = [line.split(" ")[1].split("/"),
                     line.split(" ")[2].split("/"),
                     line.split(" ")[3].split("/")]
            new_new_f = "f "
            for new_f_part in new_f:
                if len(new_f_part) == 1:
                    new_new_f += str(int(new_f_part[0])+og.get_count("v "))
                elif len(new_f_part) == 3:
                    if len(new_f_part[0]) > 0:
                        new_new_f += str(int(new_f_part[0])+og.get_count("v ")) + "/"
                    if len(new_f_part[1]) > 0:
                        new_new_f += str(int(new_f_part[1])+og.get_count("vt ")) + "/"
                    if len(new_f_part[2]) > 0:
                        new_new_f += str(int(new_f_part[2])+og.get_count("vn "))
                new_new_f += " "
            new_new_f = new_new_f[:-1] + "\n"
            tmp_obj.obj.append(new_new_f)
    og.objs.append(tmp_obj)
    return og
                    
def get_model_obj(modelname):
    obj_path = os.path.join("models", modelname + ".obj")
    romfs_dir = open("data0.txt", "r").read()
    new_data = []
    with open("data1.txt", "r") as f:
        for line in f.readlines():
            new_data.append(line)
            if line.replace('\n', '') == modelname:
                return obj_path
    szs_path = os.path.join(os.path.join(romfs_dir, "ObjectData"), modelname + ".szs")
    if os.path.isfile(szs_path):
        done = SARCExtract.extract_szs(szs_path)
        bfres_path = os.path.join(szs_path[:-4], modelname + ".bfres")
        done = subprocess.Popen(os.path.join("BFRES2OBJ", "BFRES2OBJ.exe") + " " + bfres_path + " " + os.path.join("models", modelname + ".obj"), stdout=subprocess.PIPE, shell=True).wait()
        new_lines = []
        if os.path.isfile(obj_path):
            with open(obj_path, "r") as f:
                for line in f.readlines():
                    new_lines.append(line.replace(",", "."))
            with open(obj_path, "w") as f:
                for line in new_lines:
                    f.write(line)
        with open("data1.txt", "w") as f:
            f.truncate(0)
            for line in new_data:
                if not line == "":
                    f.write(line)
            f.write(modelname + "\n")
        return obj_path
    return ""

def init_thing():
    if os.path.isdir("models"):
        with open("data0.txt", "r") as f:
            romfs_dir = f.read()
    else:
        os.mkdir("models")
        os.mkdir(os.path.join("models", "tex"))
        romfs_dir = askdirectory(title="Select a SMO RomFS dump")
        with open("data0.txt", "w") as f:
            f.write(romfs_dir)
        with open("data1.txt", "w") as f:
            f.write("")
        if os.path.isdir(romfs_dir):
            print("Extracting textures... (this will take a few minutes)")
            objdata_dir = os.path.join(romfs_dir, "ObjectData")
            if os.path.isdir(objdata_dir):
                for file in os.listdir(objdata_dir):
                    if file.endswith("Texture.szs"):
                        szs_path = os.path.join(objdata_dir, file)
                        done = SARCExtract.extract_szs(szs_path)
                        efd = szs_path[:-4]
                        if os.path.isdir(efd):
                            i = 0
                            while i < 2:
                                for file2 in os.listdir(efd):
                                    file_path = os.path.join(efd, file2)
                                    if file2.endswith(".bfres") and i == 0:
                                        done = embed_extract.extract_files(file_path)
                                    elif file2.endswith(".bntx") and i == 1:
                                        out_dir = os.path.join("models", "tex")
                                        done = bntx_extract.extract_textures(file_path, out_dir)
                                i += 1
                        shutil.rmtree(os.path.join(objdata_dir, file[:-4]))
                for file in os.listdir(os.path.join("models", "tex")):
                    if file.endswith(".dds"):
                        inf = os.path.join(os.path.join("models", "tex"), file)
                        command = "texconv.exe " + inf + " -o " + os.path.join("models", "tex") + " -ft bmp"
                        done = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).wait()
                        os.remove(inf)
            print("Done!")

init_thing()
stage_file_szs = askopenfilename(filetypes =(("SZS File", "*.szs"),("All Files","*.*")), title = "Select a SMO stage SZS")
done = SARCExtract.extract_szs(stage_file_szs)
stage_file = os.path.join(stage_file_szs[:-4], ntpath.basename(stage_file_szs)[:-3] + "byml")
scenario = 0
root = byml.Byml(open(stage_file, "rb").read()).parse()
a = root[scenario]
intybinty = 0
obj_group = OBJGroup()
for b in a['ObjectList']:
    obj_name = ''
    stage_name = ''
    res_path = ''
    unit_cfg_name = ''
    obj_data = [[0,0,0],[0,0,0],[0,0,0]]
    for c in b:
        if c == 'ModelName':
            obj_name = str(b['ModelName'])
        elif c == 'PlacementFilename':
            stage_name = str(b['PlacementFilename'])
        elif c == 'ResourceCategory':
            res_path = str(b['ResourceCategory'])
        elif c == 'UnitConfigName':
            unit_cfg_name = str(b['UnitConfigName'])
        elif c == 'Translate':
            obj_data[0][0] = float(str(b['Translate']['X']).replace(',', '.'))
            obj_data[0][1] = float(str(b['Translate']['Y']).replace(',', '.'))
            obj_data[0][2] = float(str(b['Translate']['Z']).replace(',', '.'))
        elif c == 'Rotate':
            obj_data[1][0] = float(str(b['Rotate']['X']).replace(',', '.'))
            obj_data[1][1] = float(str(b['Rotate']['Y']).replace(',', '.'))
            obj_data[1][2] = float(str(b['Rotate']['Z']).replace(',', '.'))
        elif c == 'Scale':
            obj_data[2][0] = float(str(b['Scale']['X']).replace(',', '.'))
            obj_data[2][1] = float(str(b['Scale']['Y']).replace(',', '.'))
            obj_data[2][2] = float(str(b['Scale']['Z']).replace(',', '.'))
    if not obj_name == "":
        obj_path = get_model_obj(obj_name)
    if obj_path == "" or not os.path.isfile(obj_path):
        obj_path = get_model_obj(unit_cfg_name)
    if os.path.isfile(obj_path):
        obj_group = add_to_obj(obj_path, "out.obj", "models", obj_data, str(intybinty), obj_group)
    intybinty += 1
obj_group.save("out.obj", "out.mtl")

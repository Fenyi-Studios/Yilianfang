import tkinter, ttkbootstrap, json, threading, os, logging, dgpb, zipfile, subprocess
import tkinter.ttk as tk
from tkinter import messagebox
from tkinter import simpledialog

def saveSettings(): # 保存设置
    with open(lib+"set.json","w") as f:
        f.write(json.dumps(settings))

def init(): # 初始化
    global lib,cmcl,settings
    # 初始化资源文件夹
    lib = f"{os.getcwd()}\\library\\"
    libFolders = ["downloads",".minecraft","mserver","downloads\\jre8","temp"]   # 创建文件夹
    if not os.path.isdir(lib):
        os.makedirs(lib)
    for libFolder in libFolders:
        if not os.path.isdir(lib+libFolder):
            os.makedirs(lib+libFolder)
    libFiles = [["set.json","{}"],["cmcl.json",""]]  # 创建文件
    for libFile in libFiles:
        if not os.path.isfile(lib+libFile[0]):
            with open(lib+libFile[0],"w") as f:
                f.write(libFile[1])
    with open(lib+"set.json","r") as f:
        settings = json.load(f)
    # 提示
    if not "TheTipsStatus" in settings:
        messagebox.showinfo("提示","请检查是否有将易联坊启动器安装在包含中文、空格的文件夹中。如果有，请迁移至无中文、空格的文件夹中。如果没有，请点下方按钮继续。")
        settings["TheTipsStatus"] = True
        saveSettings()
    # 初始化日志模块
    logging.basicConfig(level=logging.DEBUG,format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",datefmt="%Y-%m-%d %H:%M:%S",filename=lib+"latest.log",filemode="w")
    logging.info("初始化资源文件夹、日志模块完成。")
    logging.debug("设置："+str(settings))
    # 初始化启动器内核
    if not os.path.isfile(lib+"cmcl.exe"):
        dgpb.dgpb("https://github.com/MrShieh-X/console-minecraft-launcher/releases/download/2.2.1/cmcl.exe",lib+"cmcl.exe","启动器依赖项")
    logging.info("初始化启动器内核完成。")
    cmcl = lib+"cmcl.exe"
    # 初始化 Java 环境
    if not os.path.exists(lib+"downloads\\jre8\\bin\\java.exe"):
        dgpb.dgpb("https://github.com/RuizeSun/ResourcesForElfClient/releases/download/1/8u421.zip",lib+"temp\\jre8.zip","Minecraft 1.17 以下版本依赖项")
        jrezip = zipfile.ZipFile(lib+"temp\\jre8.zip")
        jrezip.extractall(lib+"downloads\\jre8\\")
        jrezip.close()
        os.remove(lib+"temp\\jre8.zip")
    if not os.path.exists(lib+"downloads\\jdk17\\bin\\java.exe"):
        dgpb.dgpb("https://github.com/RuizeSun/ResourcesForElfClient/releases/download/2/jdk17_0_11.zip",lib+"temp\\jdk17.zip","Minecraft 1.17~1.20 版本依赖项")
        jrezip = zipfile.ZipFile(lib+"temp\\jdk17.zip")
        jrezip.extractall(lib+"downloads\\jdk17\\")
        jrezip.close()
        os.remove(lib+"temp\\jdk17.zip")
    if not os.path.exists(lib+"downloads\\jdk21\\bin\\java.exe"):
        dgpb.dgpb("https://github.com/RuizeSun/ResourcesForElfClient/releases/download/3/jdk21.zip",lib+"temp\\jdk21.zip","Minecraft 1.20 以上版本依赖项")
        jrezip = zipfile.ZipFile(lib+"temp\\jdk21.zip")
        jrezip.extractall(lib+"downloads\\jdk21\\")
        jrezip.close()
        os.remove(lib+"temp\\jdk21.zip")

def accountClear(): # 清空所有账号
    with open(lib+"cmcl.json","r") as f:
        cmcljson = json.loads(f.read())
    if "accounts" in cmcljson:
        cmcljson["accounts"] = []
        with open(lib+"cmcl.json","w") as f:
            f.write(json.dumps(cmcljson))
def accountCreate(mode="ms",username="Steve"): # 创建账号
    'mode 对应 ms（正版）、of（离线） 两种模式， username 对应离线登录用户名'
    accountClear()
    if mode == "of":
        os.system(f"{cmcl} account --login=offline --name={username}")
    else:
        os.system(f"{cmcl} account --login=microsoft")
    os.system(f"{cmcl} account -s 0")
def accountGet(): # 获取账号信息
    with open(lib+"cmcl.json","r") as f:
        cmcljson = json.load(f)
    if "accounts" in cmcljson and not len(cmcljson["accounts"]) == 0:
        return {"loginMethod":cmcljson["accounts"][0]["loginMethod"],"playerName":cmcljson["accounts"][0]["playerName"]}
    else:
        return {"loginMethod":-1}
def accountLogin(): # 按钮触发事件：登录    
    if messagebox.askyesno("登录","使用何种方式登录 “本地游玩” 应用？\n           ↓ 微软登录   ||   ↘ 离线登录",):
        accountCreate(mode="ms")
    else:
        accountCreateQuestion = simpledialog.askstring("登录","玩家名称")
        accountCreate(mode="of",username=accountCreateQuestion)
    updateLocalLoginStatus()
def accountLogout(): # 按钮触发事件：登出
    accountClear()
    updateLocalLoginStatus()
def getDownloadableVersions(type="r"): # 获取可下载的版本号\
    global cmcl
    versions = subprocess.getoutput(f"{cmcl} install --show={type}")
    versions = versions.split(maxsplit=-1)[24:]
    return versions
def guiLocalpageDownloadButton(): # 本地游玩下载按钮触发事件
    localPageDownloadPage = ttkbootstrap.Window("下载",size=(640,480),resizable=(0,0))
    yscroll = tk.Scrollbar(localPageDownloadPage, orient=tkinter.VERTICAL)
    table = tk.Treeview(
            master=localPageDownloadPage,
            height=10,
            columns=["版本号","原版下载","Fabric 安装","Forge/NeoForge安装","Optifine 安装"],
            show='headings',
            yscrollcommand=yscroll.set
            )
    yscroll.config(command=table.yview)
    yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    table.heading(column='版本号', text='版本号', anchor='w',
                  command=lambda: print('版本号'))
    table.heading('原版下载', text='原版下载', )
    table.heading('Fabric 安装', text='Fabric 安装', )
    table.heading('Forge/NeoForge安装', text='Forge/NeoForge安装', )
    table.heading('Optifine 安装', text='Optifine 安装', )
    table.column('原版下载', width=100, minwidth=100, anchor=tkinter.S, )
    table.column('Fabric 安装', width=100, minwidth=100, anchor=tkinter.S)
    table.column('Forge/NeoForge安装', width=100, minwidth=100, anchor=tkinter.S)
    table.column('Optifine 安装', width=100, minwidth=100, anchor=tkinter.S)
    table.pack()
    versionList = getDownloadableVersions("all")
    o = list()
    for i in versionList:
        if len(o) == 5:
            table.insert('', 0, values=[o[4],o[3],o[2],o[1],o[0]])
            o = list()
        o.append(i)
    localPageDownloadPage.mainloop()
init()
# 窗口初始化
window = ttkbootstrap.Window("易联坊客户端",size=(640,480),resizable=(0,0))
tab_main=tk.Notebook(window,width=624,height=432)
tab_main.place(x=8,y=8)
# 主页
homepage = tk.Frame(tab_main)
# 离线模式
localpage = tk.Frame(tab_main)
localPageAccountStatusLabel = tk.Label(localpage,text="正在加载...")
localPageAccountStatusLabel.grid(row=0,columnspan=15)
localPageDownloadButton = tk.Button(localpage,text="下载 Minecraft",command=guiLocalpageDownloadButton).grid(row=1,column=0)
# 内容变化
def updateLocalLoginStatus():
    accountInformation = accountGet()
    if accountInformation["loginMethod"] == -1:
        localPageAccountStatusLabel["text"] = "未登录"
        loginButton = tk.Button(localpage,command=accountLogin,text="登录")
        loginButton.grid(row=0, column=15)
    elif accountInformation["loginMethod"] == 0:
        localPageAccountStatusLabel["text"] = "离线登录："+accountInformation["playerName"]
        logoutButton = tk.Button(localpage,command=accountLogout,text="登出")
        logoutButton.grid(row=0, column=15)
    else:
        localPageAccountStatusLabel["text"] = "微软登录："+accountInformation["playerName"]
        logoutButton = tk.Button(localpage,command=accountLogout,text="登出")
        logoutButton.grid(row=0, column=15)
    localpage.update()
updateLocalLoginStatus()
# Mainloop
tab_main.add(homepage,text="主页")
tab_main.add(localpage,text="本地游玩")
window.mainloop()

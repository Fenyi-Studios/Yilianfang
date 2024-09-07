import tkinter, json, os, logging, dgpb, zipfile, subprocess, time, sys, requests, elf
import _thread as thread
import tkinter.ttk as tk
from tkinter import messagebox
from tkinter import simpledialog

def saveSettings(): # 保存设置
    with open(lib+"set.json","w") as f:
        f.write(json.dumps(settings))
def getSettings(key): # 获取设置
    if key in settings:
        return settings[key]
    else:
        defaultSettings = json.loads(libFiles[0][1])
        if key in defaultSettings:
            settings[key] = defaultSettings[key]
            return settings[key]
        else:
            return None

def init(): # 初始化
    global lib,cmcl,settings,minecraft,fenyiServer,isServerOpening,dVersion,libFiles
    # 初始化资源文件夹
    lib = f"{os.getcwd()}\\library\\"
    libFolders = ["downloads","mserver","downloads\\jre8","temp"]   # 创建文件夹
    minecraft = f"{os.getcwd()}\\.minecraft\\"
    fenyiServer = "https://auth.fenserver.cn/"
    dVersion = {"betaCode":["d1063a",106301],"releaseCode":"1.0.0","type":"预先发布版"}
    if not os.path.isdir(lib):
        os.makedirs(lib)
    for libFolder in libFolders:
        if not os.path.isdir(lib+libFolder):
            os.makedirs(lib+libFolder)
    libFiles = [["set.json","{\"lastReadAnnouncement\":1}"],["cmcl.json","{\"language\": \"zh\",\"downloadSource\": 0,\"exitWithMinecraft\": false,\"checkAccountBeforeStart\": false,\"printStartupInfo\": true}"]]  # 创建文件
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
    logging.basicConfig(level=logging.DEBUG,format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",datefmt="%Y-%m-%d %H:%M:%S",filename=lib+"latest.log",filemode="w",encoding="utf-8")
    logging.info("初始化资源文件夹、日志模块完成。")
    logging.debug("设置："+str(settings))
    # 初始化启动器内核
    if not os.path.isfile(lib+"cmcl.exe"):
        dgpb.dgpb("https://gh.llkk.cc/https://github.com/MrShieh-X/console-minecraft-launcher/releases/download/2.2.1/cmcl.exe",lib+"cmcl.exe","启动器依赖项")
    logging.info("初始化启动器内核完成。")
    cmcl = lib+"cmcl.exe"
    # 初始化 Java 环境
    if not os.path.exists(lib+"downloads\\jre8\\bin\\java.exe"):
        dgpb.dgpb("https://gh.llkk.cc/https://github.com/RuizeSun/ResourcesForElfClient/releases/download/1/8u421.zip",lib+"temp\\jre8.zip","Minecraft 1.17 以下版本依赖项")
        jrezip = zipfile.ZipFile(lib+"temp\\jre8.zip")
        jrezip.extractall(lib+"downloads\\jre8\\")
        jrezip.close()
        os.remove(lib+"temp\\jre8.zip")
        if not "java" in subprocess.getoutput("echo %path%"):
            os.system(f"setx PATH \"%PATH%;{lib}\\downloads\\jre8\\bin\\\" /m")
        os.system(f"set PATH=\"%PATH%;{lib}\\downloads\\jre8\\bin\\\"")
    if not os.path.exists(lib+"downloads\\jdk17\\bin\\java.exe"):
        dgpb.dgpb("https://gh.llkk.cc/https://github.com/RuizeSun/ResourcesForElfClient/releases/download/2/jdk17_0_11.zip",lib+"temp\\jdk17.zip","Minecraft 1.17~1.20 版本依赖项")
        jrezip = zipfile.ZipFile(lib+"temp\\jdk17.zip")
        jrezip.extractall(lib+"downloads\\jdk17\\")
        jrezip.close()
        os.remove(lib+"temp\\jdk17.zip")
    if not os.path.exists(lib+"downloads\\jdk21\\bin\\java.exe"):
        dgpb.dgpb("https://gh.llkk.cc/https://github.com/RuizeSun/ResourcesForElfClient/releases/download/3/jdk21.zip",lib+"temp\\jdk21.zip","Minecraft 1.20 以上版本依赖项")
        jrezip = zipfile.ZipFile(lib+"temp\\jdk21.zip")
        jrezip.extractall(lib+"downloads\\jdk21\\")
        jrezip.close()
        os.remove(lib+"temp\\jdk21.zip")
    logging.info("初始化 Java 环境完成。")
    # 检测服务器是否可用
    try:
        serverCheck = requests.get(f"{fenyiServer}eLFP/getServerInfo.php")
        if serverCheck.status_code == 200:
            isServerOpening = True
        else:
            isServerOpening = False
    except:
        isServerOpening = False

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
        cmcljson = json.loads(f.read())
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
def accountFenyiLogin(): # 纷易账号登录
    try:
        fenyiAccountUsername = simpledialog.askstring("纷易登录","请输入您的纷易账号用户名：")
        fenyiAccountPassword = simpledialog.askstring("纷易登录","请输入您的纷易账号密码：",show="*")
        fenyiAccountRequest = requests.post(f"{fenyiServer}api/loginAPI_return.php",{"username":fenyiAccountUsername,"password":fenyiAccountPassword})
        fenyiAccount = json.loads(fenyiAccountRequest.text)
        if not fenyiAccount["code"] == "200":
            messagebox.showwarning("警告","验证失败，请检查用户名或密码是否正确！")
        else:
            fenyiAccountPersonalContent = json.loads(requests.post(f"{fenyiServer}api/getPersonContentFromKey.php",{"key":fenyiAccount["personal_key"]}).text)
            settings["FenyiAccount"]["key"] = fenyiAccount["personal_key"]
            settings["FenyiAccount"]["status"] = "logined"
            settings["FenyiAccount"]["username"] = fenyiAccountPersonalContent["name"]
            settings["FenyiAccount"]["email"] = fenyiAccountPersonalContent["email"]
            settings["FenyiAccount"]["id"] = fenyiAccountPersonalContent["id"]
            saveSettings()
        homePageFAccountStatus()
    except:
        messagebox.showerror("错误","无法登录纷易账号。")
        logging.error("无法登录纷易账号，请求中出现问题。")
        homePageFAccountStatus()
def accountFenyiLogout(): # 纷易账号登出
    settings["FenyiAccount"] = {"status":"unlogined"}
    saveSettings()
    homePageFAccountStatus()
def getDownloadableVersions(type="r"): # 获取可下载的版本号\
    global cmcl
    versions = subprocess.getoutput(f"{cmcl} install --show={type}")
    versions = versions.split(maxsplit=-1)[24:]
    logging.debug(f"获取版本信息成功：【{type}】{str(versions)}")
    return versions
def guiLocalpageDownloadButton(): # 本地游玩下载按钮触发事件
    global versionList
    def downloadMinecraft():
        downloadMinecraftVersion = simpledialog.askstring("下载 Minecraft","Minecraft 版本：")
        downloadMinecraftVersionName = simpledialog.askstring("下载 Minecraft","版本名称：")
        if downloadMinecraftVersionName in library:
            messagebox.showerror("错误","该版本已存在。")
            return None
        if " " in downloadMinecraftVersionName:
            messagebox.showerror("错误","版本名称不能包含空格。")
            return None
        if "ELF-" in downloadMinecraftVersionName:
            messagebox.showerror("错误","版本名称无法使用。")
            return None
        if not downloadMinecraftVersion in versionList:
            messagebox.showerror("错误","没有找到此版本！已退出安装。")
        else:
            def downloadCommmand():
                os.system(f"start {cmcl} install "+downloadMinecraftVersion+" -n "+downloadMinecraftVersionName)
            thread.start_new_thread(downloadCommmand, ())
            
    localPageDownloadPage = tkinter.Tk()
    localPageDownloadPage.title("版本下载")
    localPageDownloadPage.geometry("640x480")
    localPageDownloadPage.resizable(0,0)
    yscroll = tk.Scrollbar(localPageDownloadPage, orient=tkinter.VERTICAL)
    table = tk.Treeview(
            master=localPageDownloadPage,
            height=10,
            columns=["版本号","adfgdfg","sdfgdfg","ddfgdfg","fdfgdfg"],
            show='headings',
            yscrollcommand=yscroll.set
            )
    yscroll.config(command=table.yview)
    yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    table.heading(column='版本号', text='0', anchor='w',
                  command=lambda: print('版本号'))
    table.heading('adfgdfg', text='1', )
    table.heading('sdfgdfg', text='2', )
    table.heading('ddfgdfg', text='3', )
    table.heading('fdfgdfg', text='4', )
    table.column('版本号', width=100, minwidth=100, anchor=tkinter.S, )
    table.column('adfgdfg', width=100, minwidth=100, anchor=tkinter.S, )
    table.column('sdfgdfg', width=100, minwidth=100, anchor=tkinter.S)
    table.column('ddfgdfg', width=100, minwidth=100, anchor=tkinter.S)
    table.column('fdfgdfg', width=100, minwidth=100, anchor=tkinter.S)
    table.pack()
    versionList = getDownloadableVersions("all")
    if "HTTP" in versionList:
        messagebox.showerror("错误","获取版本列表失败，请重试。")
        logging.error("获取版本列表失败，请求出现问题。")
        localPageDownloadPage.destroy()
        return None
    o = list()
    for i in versionList:
        if len(o) == 5:
            table.insert('', 0, values=[o[4],o[3],o[2],o[1],o[0]])
            o = list()
        o.append(i)
    table.insert('', 0, values=o)
    tk.Button(localPageDownloadPage,text="下载 Minecraft",command=downloadMinecraft).pack()
    localPageDownloadPage.mainloop()
def guiLaunch(): # 图形化本地启动
    global localPageLibrarySelect
    if not localPageLibrarySelect.get() in library:
        messagebox.showerror("错误","没有找到该版本！")
        return None
    if "ELF-" in localPageLibrarySelect.get():
        if not messagebox.askyesno("警告","你正在启动的版本是易联坊联机客户端，不使用联机模块启动可能引起错误！"):
            return None
    try:
        logging.info("正在启动游戏。名称："+localPageLibrarySelect.get())
        with open(f"{minecraft}versions\\{localPageLibrarySelect.get()}\\{localPageLibrarySelect.get()}.json","r") as f:
            versionJson = json.loads(f.read())
        if versionJson["javaVersion"]["majorVersion"] < 16:
            javapath = f"{lib}downloads\\jre8\\bin\\java.exe"
        elif versionJson["javaVersion"]["majorVersion"] < 20 and versionJson["javaVersion"]["majorVersion"] > 15:
            javapath = f"{lib}downloads\\jdk17\\bin\\java.exe"
        else:
            javapath = f"{lib}downloads\\jdk21\\bin\\java.exe"
        with open(f"{lib}cmcl.json","r") as f:
            cmcljson = json.loads(f.read())
        with open(f"{lib}cmcl.json","w") as f:
            cmcljson["javaPath"] = javapath
            f.write(json.dumps(cmcljson))
        def launching():
            os.system(f"{cmcl} -s {localPageLibrarySelect.get()} && {cmcl} version --isolate")
            os.system(f"{cmcl} {localPageLibrarySelect.get()}")
        thread.start_new_thread(launching, ())
    except:
        messagebox.showerror("错误","启动时出现错误。")
        logging.error("启动时出现问题。")
def elfPage(): # 联机页面
    elfPage = tkinter.Toplevel(window)
    yscroll = tk.Scrollbar(elfPage, orient=tkinter.VERTICAL)
    table = tk.Treeview(
            master=elfPage,
            height=10,
            columns=["房间ID","房间名称","房间简介","版本","正版认证","房间状态"],
            show='headings',
            yscrollcommand=yscroll.set
            )
    yscroll.config(command=table.yview)
    yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    table.heading(column='房间ID', text='房间ID', anchor='w')
    table.heading('房间名称', text='房间名称', )
    table.heading('房间简介', text='房间简介', )
    table.heading('版本', text='版本', )
    table.heading('正版认证', text='正版认证', )
    table.heading('房间状态', text='房间状态', )
    table.column('房间ID', width=100, minwidth=100, anchor=tkinter.S, )
    table.column('房间名称', width=100, minwidth=100, anchor=tkinter.S, )
    table.column('房间简介', width=100, minwidth=100, anchor=tkinter.S)
    table.column('版本', width=100, minwidth=100, anchor=tkinter.S)
    table.column('正版认证', width=100, minwidth=100, anchor=tkinter.S)
    table.column('房间状态', width=100, minwidth=100, anchor=tkinter.S)
    table.pack()
    elfServerList = json.loads(requests.post(f"{fenyiServer}eLFP/getServerList.php",{"type":"all"}).text)
    for i in elfServerList:
        table.insert("", 0, values=[str(i["serverID"]),i["serverInfo"]["elfName"],i["serverInfo"]["elfDescription"][0:15],f"{i["gameInfo"]["version"]} {i["gameInfo"]["modLoader"]}",i["serverInfo"]["onlineMode"],i["serverInfo"]["status"]])
    def joinServer():
        serverID = simpledialog.askinteger("加入服务器","服务器ID：")
        elfserver = elf.Server(serverID)
        if not elfserver.checkStatus():
            messagebox.showerror("错误","未找到该服务器。")
            return None
        if not elfserver.isInstalled():
            elfserver.installnStart()
        else:
            elfserver.start()
    tk.Button(elfPage,text="加入服务器",command=joinServer).pack()
    elfPage.mainloop()

init()
logging.info("初始化完成，正在加载图形界面。")

# 窗口初始化
window = tkinter.Tk()
window.geometry("640x480")
window.title("易联坊客户端")
window.resizable(0,0)
tab_main=tk.Notebook(window,width=624,height=432)
tab_main.place(x=8,y=8)
def on_closing():
    sys.exit()
window.protocol("WM_DELETE_WINDOW", on_closing)

# 主页
if isServerOpening:
    homepage = tk.Frame(tab_main)
    homePageFenyiAccountStatusLabel = tk.Label(homepage,text="正在加载...")
    homePageFenyiAccountStatusLabel.grid(row=0,columnspan=2)
    tk.Button(homepage, text="联机",command=elfPage).grid(row=1,column=0)
    tab_main.add(homepage,text="主页")

# 本地游戏界面
localpage = tk.Frame(tab_main)
localPageAccountStatusLabel = tk.Label(localpage,text="正在加载...")
localPageAccountStatusLabel.grid(row=0,columnspan=2)
tk.Button(localpage,text="下载",command=guiLocalpageDownloadButton).grid(row=1,column=0)
localPageLibrarySelect = tk.Combobox(localpage,state="readonly")
localPageLibrarySelect.grid(row=2,columnspan=2)
tk.Button(localpage,text="启动",command=guiLaunch).grid(row=1,column=1)
tab_main.add(localpage,text="本地游玩")

# 关于
aboutpage = tk.Frame(tab_main)
tk.Label(aboutpage,text=f"易联坊启动器 \n{dVersion["type"]} {dVersion['releaseCode']}-{dVersion['betaCode'][0]}",font="SimHei 24").pack()
tk.Label(aboutpage,text="启动器使用了 ConsoleMinecraftLauncher 作为内核。").pack()
tab_main.add(aboutpage,text="关于")

# 公告提示
def announcement():
    try:
        announcementInfo = json.loads(requests.get("https://ruizesun.github.io/ResourcesForElfClient/announcement.json").text) 
    except:
        announcementInfo = {"type":"INFO","version":-1,"releaseTime":0,"title":"获取公告失败","text":"获取公告失败，请检查网络环境。"}
    if not announcementInfo["version"] == -1:
        lra = getSettings("lastReadAnnouncement")
        if int(lra) >= int(announcementInfo["version"]):
            return None
    if announcementInfo["type"] == "PRIMARY":
        messagebox.showinfo(f"【严重警告】{announcementInfo["title"]}",f"{announcementInfo["text"]}\n————————————————————此严重警告编辑于 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(announcementInfo["releaseTime"]))} #{announcementInfo["version"]}")
    elif announcementInfo["type"] == "WARNING":
        messagebox.showinfo(f"【警告】{announcementInfo["title"]}",f"{announcementInfo["text"]}\n————————————————————此警告编辑于 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(announcementInfo["releaseTime"]))} #{announcementInfo["version"]}")
    else:
        messagebox.showinfo(f"【公告】{announcementInfo["title"]}",f"{announcementInfo["text"]}\n————————————————————此公告编辑于 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(announcementInfo["releaseTime"]))} #{announcementInfo["version"]}")
    if not announcementInfo["version"] == -1:
        settings["lastReadAnnouncement"] = announcementInfo["version"]
        saveSettings()
    
thread.start_new_thread(announcement,())

# 内容变化
def updateLocalLoginStatus(): # 本地游戏登录状态更新
    accountInformation = accountGet()
    if accountInformation["loginMethod"] == -1:
        localPageAccountStatusLabel["text"] = "未登录"
        loginButton = tk.Button(localpage,command=accountLogin,text="登录")
        loginButton.grid(row=0, column=2)
    elif accountInformation["loginMethod"] == 0:
        localPageAccountStatusLabel["text"] = "离线登录："+accountInformation["playerName"]
        logoutButton = tk.Button(localpage,command=accountLogout,text="登出")
        logoutButton.grid(row=0, column=2)
    else:
        localPageAccountStatusLabel["text"] = "微软登录："+accountInformation["playerName"]
        logoutButton = tk.Button(localpage,command=accountLogout,text="登出")
        logoutButton.grid(row=0, column=2)
    localpage.update()
def localPageLibraryUpdate(): # 本地页面游戏版本更新
    global localPageLibrarySelect,library
    if os.path.exists(f"{minecraft}versions\\"):
        library = os.listdir(f"{minecraft}versions\\")
    else:
        library = []
    localPageLibrarySelect["values"] = library
    if not len(library) == 0:
        localPageLibrarySelect.current(0)
    localpage.update()
def homePageFAccountStatus(): # 主页纷易登录状态更新
    global homePageFenyiAccountStatusLabel
    if not "FenyiAccount" in settings:
        settings["FenyiAccount"] = {"status":"unlogined"}
        homePageFenyiAccountStatusLabel["text"] = "未登录"
        loginButton = tk.Button(homepage,text="登录",command=accountFenyiLogin)
        loginButton.grid(row=0,column=2)
    else:
        if settings["FenyiAccount"]["status"] == "unlogined":
            homePageFenyiAccountStatusLabel["text"] = "未登录"
            loginButton = tk.Button(homepage,text="登录",command=accountFenyiLogin)
            tk.Button(homepage,command=lambda:os.system(f"start {fenyiServer}register.html"),text="注册").grid(row=0,column=3)
            loginButton.grid(row=0,column=2)
        else:
            homePageFenyiAccountStatusLabel["text"] = settings["FenyiAccount"]["username"]
            logoutButton = tk.Button(homepage,command=accountFenyiLogout,text="登出")
            tk.Button(homepage,command=lambda:os.system(f"start {fenyiServer}register.html"),text="注册").grid(row=0,column=3)
            logoutButton.grid(row=0, column=2)
            tk.Button(homepage,command=lambda:os.system(f"start {fenyiServer}user/index.html"),text="用户中心").grid(row=0,column=3)
    homepage.update()
    saveSettings()

def statusUpdateThread():
    while True:
        updateLocalLoginStatus()
        localPageLibraryUpdate()
        if isServerOpening:
            homePageFAccountStatus()
        time.sleep(5)
thread.start_new_thread(statusUpdateThread, ())

# Mainloop
logging.info("图形界面加载完成")
window.mainloop()

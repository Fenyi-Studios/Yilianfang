'''
eLF Support of eLFClient
'''
import os, requests, json, xmltodict, dgpb, logging 

# 变量初始化
lib = f"{os.getcwd()}\\library\\"
libFolders = ["downloads","mserver","downloads\\jre8","temp"]   # 创建文件夹
minecraft = f"{os.getcwd()}\\.minecraft\\"
fenyiServer = "https://auth.fenserver.cn/"
cmcl = lib+"cmcl.exe"
log = logging.getLogger("elfCore")

# Server 类
class Server:
    def __init__(self,serverId):
        self.serverId = serverId
        getServerInfoRequest = requests.post(f"{fenyiServer}eLFP/getServerInfo.php",{"serverID":self.serverId})
        if not getServerInfoRequest.status_code == 200:
            logging.error(f"请求 serverID 为 {self.serverId} 的服务器信息时发生错误。")
            raise ValueError("请求服务器信息时发生错误。")
        log.debug(f"serverID 为 {self.serverId} 的服务器信息为 {getServerInfoRequest.text}")
        self.serverInfo = json.loads(getServerInfoRequest.text)
        """self.serverInfo = json.loads('''{
	"serverID": 123456,
	"gameInfo": {
		"version": "1.21",
		"modLoader": "NForge",
        "javaVersion":"21",
		"mods": [
			"https://SERVER/eLFP/mods/11b82b3b12de44c7c0b87cb2df22502b.jar",
			"https://SERVER/eLFP/mods/48s88sdg4s86e5f34s65ged2b87cb2df.jar"
		]
	},
	"serverInfo": {
		"onlineMode": true,
		"elfName": "1.21 Fabric 生存服",
		"elfDescription": "一个简单的 Fabric 生存服，快来吖！",
		"status": true,
		"ip": "127.0.0.1",
		"port": "11451",
		"rules": "不要玩元神"
	}
    }''')"""

    def checkStatus(self):
        return self.serverInfo["status"] == 200

    def accountGet(): # 获取账号信息 # 等待易联坊API完成
        with open(lib+"cmcl.json","r") as f:
            cmcljson = json.loads(f.read())
        if "accounts" in cmcljson and not len(cmcljson["accounts"]) == 0:
            return {"loginMethod":cmcljson["accounts"][0]["loginMethod"],"playerName":cmcljson["accounts"][0]["playerName"]}
        else:
            return {"loginMethod":-1}

    def installnStart(self): # 安装 & 启动
        # 获取 Fabric 和 Fabric API 最新版本
        if self.serverInfo["gameInfo"]["modLoader"] == "Fabric":
            fabricVersions = json.loads(requests.get("https://meta.fabricmc.net/v1/versions/loader/"+self.serverInfo["gameInfo"]["version"]).text)
            fabricAPIVersionsAll = xmltodict.parse((requests.get("https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/maven-metadata.xml").text))
            fabricAPIVersionsC = list()
            for i in fabricAPIVersionsAll["metadata"]["versioning"]["versions"]["version"]:
                if "+"+self.serverInfo["gameInfo"]["version"] in i:
                    fabricAPIVersionsC.append(i)
        # 获取 Forge 最新版本
        if self.serverInfo["gameInfo"]["modLoader"] == "NForge":
            forgeVersions = json.loads(requests.get("https://bmclapi2.bangbang93.com/forge/minecraft/"+self.serverInfo["gameInfo"]["version"]).text)
            forgeVersions = forgeVersions[0]["version"]
        # 自动选择 Java 版本 & 进入服务器
        with open(f"{lib}cmcl.json","r") as f:
            cmcljson = json.loads(f.read())
        with open(f"{lib}cmcl.json","w") as f:
            if self.serverInfo["gameInfo"]["javaVersion"] == "8":
                cmcljson["javaPath"] = f"{lib}downloads\\jre8\\bin\\java.exe"
            elif self.serverInfo["gameInfo"]["javaVersion"] == "17":
                cmcljson["javaPath"] = f"{lib}downloads\\jdk17\\bin\\java.exe"
            else:
                cmcljson["javaPath"] = f"{lib}downloads\\jdk21\\bin\\java.exe"
            f.write(json.dumps(cmcljson))
        # 编写安装脚本
        with open(f"{lib}temp\\elfclientinstall.cmd","w") as f:
            f.write("@echo off\ntitle 正在安装 Minecraft / Installing Minecraft\ncls\n")
            f.write(f"{cmcl} install {self.serverInfo["gameInfo"]["version"]} -n ELF-{str(self.serverInfo["serverID"])}\n{cmcl} -s ELF-{str(self.serverInfo["serverID"])}\n{cmcl} version --isolate\n")
            log.debug(self.serverInfo["gameInfo"]["mods"])
            for i in self.serverInfo["gameInfo"]["mods"]:
                if not i == "":
                    log.debug(i)
                    dgpb.dgpb(i,f"{lib}temp\\MODS_{str(self.serverInfo["serverID"])}\\{i.split("/")[-1]}","模组")
                    log.debug("1")
            if not self.serverInfo["gameInfo"]["modLoader"] == "None":
                f.write(f"mkdir {minecraft}versions\\ELF-{str(self.serverInfo["serverID"])}\\mods\\\n")
                if self.serverInfo["gameInfo"]["modLoader"] == "Fabric":
                    f.write(f"{cmcl} version --fabric={fabricVersions[0]["loader"]["version"]} --api {fabricAPIVersionsC[-1]}\nmove {minecraft}mods\\fabric-api-{fabricAPIVersionsC[-1]}.jar {minecraft}versions\\ELF-{str(self.serverInfo["serverID"])}\\mods\\\n")
                if self.serverInfo["gameInfo"]["modLoader"] == "NForge":
                    f.write(f"{cmcl} version --forge={forgeVersions}\n")
                f.write(f"move /Y {lib}temp\\MODS_{str(self.serverInfo["serverID"])}\\*.jar {minecraft}versions\\ELF-{str(self.serverInfo["serverID"])}\\mods\\ \n{cmcl} ELF-{str(self.serverInfo["serverID"])}\n")
            f.write(f"{cmcl} version --config=qpServerAddress {self.serverInfo["serverInfo"]["ip"]}:{self.serverInfo["serverInfo"]["port"]}\nexit") 
        os.system(f"start {lib}temp\\elfclientinstall.cmd")
    
    def start(self): # 单独启动
        if not self.isInstalled():
            raise RuntimeError("没有安装该服务器的客户端")
        with open(f"{lib}temp\\elfclientstart.cmd","w") as f:
            f.write(f"@echo off\ntitle 正在启动 Minecraft / Launching Minecraft\ncls\n{cmcl} -s ELF-{self.serverInfo["serverID"]}\n{cmcl} version --complete=assets\n{cmcl} version --complete=libraries\n{cmcl} version --complete=natives\n{cmcl}\nexit")
        os.system(f"start {lib}temp\\elfclientstart.cmd")
    
    def isInstalled(self): # 是否有安装此版本
        if f"ELF-{self.serverInfo["serverID"]}" in os.listdir(f"{minecraft}\\versions\\"):
            return True
        else:
            return False
log.info("易联坊内核加载完毕。")
#Server("1").installnStart()
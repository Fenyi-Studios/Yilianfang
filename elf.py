'''
eLF Support of eLFClient
'''
import os, requests, json, xmltodict,dgpb

# 变量初始化
lib = f"{os.getcwd()}\\library\\"
libFolders = ["downloads","mserver","downloads\\jre8","temp"]   # 创建文件夹
minecraft = f"{os.getcwd()}\\.minecraft\\"
fenyiServer = "http://auth.fenserver.cn/"
cmcl = lib+"cmcl.exe"

# Server 类
class Server:
    def __init__(self,serverId):
        self.serverId = serverId
        #getServerInfoRequest = requests.post(f"{fenyiServer}eLFP/getServerInfo.php",{"serverID":self.serverId})
        #self.serverInfo = json.loads(getServerInfoRequest.text)
        self.serverInfo = json.loads('''{
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
    }''')

    def accountGet(): # 获取账号信息 # 等待易联坊API完成
        with open(lib+"cmcl.json","r") as f:
            cmcljson = json.load(f)
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
            #for i in self.serverInfo["gameInfo"]["mods"]:
            #    dgpb.dgpb(i,f"{lib}temp\\MODS_{str(self.serverInfo["serverID"])}\\{i.split("/")[-1]}")
            if not self.serverInfo["gameInfo"]["modLoader"] == "None":
                f.write(f"mkdir {minecraft}version\\ELF-{str(self.serverInfo["serverID"])}\\mods\\\n")
                if self.serverInfo["gameInfo"]["modLoader"] == "Fabric":
                    f.write(f"{cmcl} version --fabric={fabricVersions[0]["loader"]["version"]} --api {fabricAPIVersionsC[-1]}\nmove {minecraft}mods\\fabric-api-{fabricAPIVersionsC[-1]}.jar {minecraft}versions\\ELF-{str(self.serverInfo["serverID"])}\\mods\\\n")
                if self.serverInfo["gameInfo"]["modLoader"] == "NForge":
                    f.write(f"{cmcl} version --forge={forgeVersions}\n")
                f.write(f"move /Q {lib}temp\\MODS_{str(self.serverInfo["serverID"])}\\*.jar {minecraft}versions\\ELF-{str(self.serverInfo["serverID"])}\\mods\\ \n{cmcl} ELF-{str(self.serverInfo["serverID"])}")
        os.system(f"{cmcl} config qpServerAddress {self.serverInfo["serverInfo"]["ip"]}:{self.serverInfo["serverInfo"]["port"]}\nstart {lib}temp\\elfclientinstall.cmd\n{cmcl} config delete=qpServerAddress")
a = Server(123456)
a.installnStart()
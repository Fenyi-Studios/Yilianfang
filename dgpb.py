"""
Download with GUI Progress Bar .py
"""
import tkinter,requests,time,logging,os
import tkinter.ttk as tk
log = logging.getLogger("DGPB")
log.info("DGPB 正在加载。")
def dgpb(downloadUrl, save, text="无"):
    global downloadProgressBar,downloadProgressWindow,log
    log.debug(f"正在创建下载程序，下载 URL 为 {downloadUrl} ，保存至 {save} ，窗口中备注为 {text} 的文件。")
    downloadProgressWindow = tkinter.Tk()
    downloadProgressWindow.geometry("320x240")
    downloadProgressWindow.title("下载")
    tkinter.Label(downloadProgressWindow,text="下载文件： ..."+downloadUrl[-15:]).pack()
    downloadProgressBar = tk.Progressbar(downloadProgressWindow,length=300,maximum=100)
    downloadProgressBar.pack()
    downloadProgressTips = tkinter.Label(downloadProgressWindow,text="正在请求内容...")
    downloadProgressTips.pack()
    tkinter.Label(downloadProgressWindow,text=text).pack()
    tkinter.Label(downloadProgressWindow,text="请勿关闭程序").pack()
    def download(downloadUrl,save):
        global downloadProgressBar,downloadProgressWindow
        log.debug(f"正在下载 URL 为 {downloadUrl} 的文件（保存至 {save} ，窗口中备注为 {text} ） 。")
        response = requests.get(downloadUrl, stream=True)
        size = 0
        chunk_size = 512288
        content_size = int(response.headers['content-length'])
        if response.status_code == 200:
            os.system(f"mkdir {"\\".join(save.split("\\")[:-1])}")
            with open(save,'wb') as file:
                start = time.time()
                for data in response.iter_content(chunk_size = chunk_size):
                    file.write(data)
                    size +=len(data)
                    downloadProgressBar["value"] = float(size / content_size * 100)
                    downloadProgressTips["text"] = f"下载速度：{round((size/(time.time()-start))/1024/1024,2)}MB/s\n下载进度：{round(size/1024/1024,2)}MB/{round(content_size/1024/1024,2)}MB\n预计还需 {round((content_size-size)/(size/(time.time()-start)))}秒"
                    downloadProgressWindow.update()
        downloadProgressWindow.destroy()
        log.debug(f"下载 URL 为 {downloadUrl} ，保存至 {save} ，窗口中备注为 {text} 的文件完成。")
    download(downloadUrl,save)
    log.debug(f"下载 URL 为 {downloadUrl} ，保存至 {save} ，窗口中备注为 {text} 的文件的程序已关闭。")
log.info("DGPB 加载完毕。")
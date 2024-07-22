"""
Download with GUI Progress Bar .py
"""
import tkinter,requests,time
import _thread as thread
import tkinter.ttk as tk
def dgpb(downloadUrl, save, text="无"):
    global downloadProgressBar,downloadProgressWindow
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
        response = requests.get(downloadUrl, stream=True)
        size = 0
        chunk_size = 512288
        content_size = int(response.headers['content-length'])
        if response.status_code == 200:
            with open(save,'wb') as file:
                start = time.time()
                for data in response.iter_content(chunk_size = chunk_size):
                    file.write(data)
                    size +=len(data)
                    downloadProgressBar["value"] = float(size / content_size * 100)
                    downloadProgressTips["text"] = f"下载速度：{round((size/(time.time()-start))/1024/1024,2)}MB/s\n下载进度：{round(size/1024/1024,2)}MB/{round(content_size/1024/1024,2)}MB\n预计还需 {round((content_size-size)/(size/(time.time()-start)))}秒"
                    downloadProgressWindow.update()
        downloadProgressWindow.destroy()
    download(downloadUrl,save)
    downloadProgressWindow.mainloop()
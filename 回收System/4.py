import tkinter
import tkinter.messagebox,tkinter.simpledialog
import os, os.path
import threading

rubbishExt = ['.tmp','.bak','.old','.$$$']

class Window:
    def __init__(self):
        self.root = tkinter.Tk()

        #创建菜单
        menu = tkinter.Menu(self.root)

        #创建"系统"子菜单
        submenu = tkinter.Menu(menu,tearoff=0)
        submenu.add_command(label="关于...", command=self.MenuAbout)
        submenu.add_separator()
        submenu.add_command(label="退出", command=self.MenuExit)
        menu.add_cascade(label = "系统", menu=submenu)

        #创建"清理"子菜单
        submenu = tkinter.Menu(menu,tearoff=0)
        submenu.add_command(label="扫描垃圾文件", command=self.MenuScanRubbish)
        submenu.add_command(label="删除垃圾文件", command=self.MenuDelRubbish)
        menu.add_cascade(label="清理",menu=submenu)

        #创建"查找"子菜单
        submenu = tkinter.Menu(menu,tearoff=0)
        submenu.add_command(label="搜索大文件",command=self.MenuScanBigFile)
        submenu.add_separator()
        submenu.add_command(label="按名称搜索文件",command=self.MenuSearchFile)
        menu.add_cascade(label="查找",menu=submenu)

        self.root.config(menu=menu)

        #创建标签,用于显示状态信息
        self.progress = tkinter.Label(self.root, anchor=tkinter.W, text='状态',bitmap='hourglass',compound='left')
        self.progress.place(x=10,y=370,width=480,height=15)

        #创建文本框,显示文件列表
        self.flist = tkinter.Text(self.root)
        self.flist.place(x=10,y=10,width=480,height=350)
        #为文本框添加垂直动条
        self.vscroll = tkinter.Scrollbar(self.flist)
        self.vscroll.pack(side='right',fill='y')
        self.flist['yscrollcommand'] = self.vscroll.set
        self.vscroll['command'] = self.flist.yview

        #(3)获取盘符
        #取得当前计算机的盘符
    def GetDrives(self):
        drives = []
        for i in range(65, 91):
                vol = chr(i) + ':/'
                if os.path.isdir(vol):
                    drives.append(vol)
        return tuple(drives)

        #(4)事件驱动

    def MainLoop(self):
        self.root.title("Windows垃圾文件清理工具")
        self.root.minsize(500,400)
        self.root.maxsize(500,400)
        self.root.mainloop()

            #"关于" 菜单
    def MenuAbout(self):
        tkinter.messagebox.showinfo("Windows垃圾文件清理工具","这是用Python编写的应用程序。\n欢迎使用并提出宝贵意见!")

            #"退出"菜单
    def MenuExit(self):
        self.root.quit();

            #"扫描垃圾文件"菜单
    def MenuScanRubbish(self):
        result = tkinter.messagebox.askquestion("Windows垃圾文件清理工具","扫描垃圾文件将需要较长的时间，是否继续？")
        if result == 'no':
            return tkinter.messagebox.showinfo("Windows垃圾文件清理工具","马上开始扫描垃圾文件！")
        self.drives = self.GetDrives()
             # self.ScanRubbish #单线程
        t = threading.Thread(target=self.ScanRubbish,args=(self.drives,)) # 创建线程
        t.start()                            #开始线程

             #"删除垃圾文件"菜单
    def MenuDelRubbish(self):
        result = tkinter.messagebox.askquestion("Windows垃圾文件处理工具","删除垃圾文件将需要较长的时间，是否继续？")
        if result == 'no':
            return tkinter.messagebox.showinfo("Windows垃圾文件清理工具","马上开始扫描垃圾文件！")
        self.drives = self.GetDrives()
        t = threading.Thread(target=self.DeleteRubbish,args=(self.drives,))
        t.start()
              #"搜索大文件"菜单
    def MenuScanBigFile(self):
        result = tkinter.messagebox.askquestion("Windows垃圾文件清理工具","扫描大文件将需要较长时间，是否继续？")
        if result == 'no':
           return tkinter.messagebox.showinfo("Windows垃圾文件清理工具","马上开始扫描大文件！")

        s = tkinter.simpledialog.askinteger("Windows垃圾文件清理工具","请设置大文件的大小(M):")
        t = threading.Thread(target=self.ScanBigFile, args=(s,))
        t.start()
        #"按名称搜索文件"菜单
    def MenuSearchFile(self) :
        s = tkinter.simpledialog.askstring("Windows垃圾文件清理工具", "请输入文件名的部分字符")
        t = threading.Thread(target=self.SearchFile, args=(s,))
        t.start()

              # 扫描垃圾文件
    def ScanRubbish(self,scanpath):
        global rubbishExt
        total = 0
        filesize = 0
        for drive in scanpath:
            for root, dirs, files in os.walk(drive):
                try:
                    for fil in files:
                        filesplit = os.path.splitext(fil)
                        if filesplit[1] == '': #若无文件扩展名
                            continue
                        try:
                            if rubbishExt.index(filesplit[1]) >= 0:   # 扩展名在垃圾文件扩展名列表中
                                fname = os.path.join(os.path.abspath(root), fil)
                                filesize += os.path.getsize(fname)
                                if total % 20 == 0:
                                    self.flist.delete(0.0, tkinter.END)
                                self.flist.insert(tkinter.END, fname + '\n')
                                l = len(fname)
                                if l > 60:
                                    self.progress['text'] = fname[:30] + '...' + fname[l - 30:l]
                                else:
                                    self.progress['text'] = fname
                                total += 1
                        except ValueError:
                            pass
                except Exception as e:
                    print(e)
                    pass
        self.progress['text'] = "找到 %s 个垃圾文件，共占用 %.2f M磁盘空间" % (total,filesize / 1024 / 1024)
                              #删除垃圾文件
    def DeleteRubbish(self,scanpath):
        global rubbishExt
        total = 0
        filesize = 0
        for drive in scanpath:
            for root, dirs, files in os.walk(drive):
                try:
                    for fil in files:
                        filesplit = os.path.splitext(fil)
                        if filesplit[1] == '': #若无文件扩展名
                            continue
                        try:
                            if rubbishExt.index(filesplit[1]) >= 0: # 扩展名在垃圾文件扩展名列表中
                                fname = os.path.join(os.path.abspath(root), fil)
                                filesize += os.path.getsize(fname)
                                try:
                                    os.remove(fname) #删除文件
                                    l = len(fname)
                                    if l>50:
                                        fname = fname[:25]+'...'+fname[l-25:l]
                                    if total % 20 == 0:
                                        self.flist.delete(0.0, tkinter.END)
                                    self.flist.insert(tkinter.END,'删除文件:'+fname + '\n')
                                    self.progress['text'] = fname
                                    total += 1
                                except:
                                    pass
                        except ValueError:
                              pass
                except Exception as e:
                      print(e)
                      pass
                                      #搜索大文件
    def ScanBigFile(self,filesize):
        total = 0
        filesize = filesize*1024*1024
        for drive in self.GetDrives():
            for root,dirs,files in os.walk(drive):
                for fil in files:
                    try:
                        fname = os.path.join(os.path.abspath(root), fil)
                        fsize = os.path.getsize(fname)
                        self.progress['text'] = fname
                        if fsize>=filesize:
                            total +=1
                            self.flist.insert(tkinter.END,'%s,[%.2f M]\n' %(fname,fsize/1024/1024))
                    except:
                        pass
                              #按名称搜索文件
    def SearchFile(self,fname):
        total = 0
        fname = fname.upper()
        for drive in self.GetDrives():
            for root, dirs, files in os.walk(drive):
                for file in files:
                    try:
                        fn = os.path.abspath(os.path.join(root, file))
                        l = len(fn)
                        if l > 50:
                            self.progress['text'] = fn[:25] + '...' + fn[l-25:l]
                        else:
                            self.progress['text'] = fn
                        if file.upper().find(fname) >= 0 :
                            total += 1
                            self.flist.insert(tkinter.END, fn + '\n')
                    except:
                        pass
                              #(5)运行窗体
if __name__=="__main__":
    window = Window()
    window.MainLoop()

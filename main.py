# codeing=utf-8
# @Time    : 2018-01-10
# @Author  : py_sky
# @Mail    : bosichong@qq.com
# @Site    : www.17python.com
# @Title   : 基于Python、Tk构建的可视化目录文件同步助手
# @Url     : http://www.17python.com/blog/49
# @Details : 比较a,b两个目录中的目录及文件的不同，修复缺失目录及文件。

'''
之前用java GUI写过一个简单的目录同步助手，前几天在WIN10下边想用的时候，发现竟然无法使用了，正好最近在学习python，所以用python重写了一简单的目录文件同步助手。

## 功能需求

之前有些喜欢拍照，但设备和场景比较多，所以每次照相回来，都为每台设备创建目录，然后在目录下边创建以时间为名的目录进行照片备份。
之后这个备份了几年，后来目录越来越多，经常发现无法准确的判断哪些照片是否备份过，因为实在太多了，所以，需要一个实际目录与备份目录比较，
并且能把比较后的结果复制到备份目录中进行备份。

## 需求分析

从需求上分析：参数需要给定两个目录，然后有比较和复制两个功能，GUI构建上只需要两个目录选择和两个按钮，使用Tk即可实现。
技术上实现采用python的 filecmp shutil os 进行一些目录及文件的比较及复制来实现需求。

## 逻辑分析

通过目录选择框获得了两个字符串，然后进行比较，分析出不同的目录与文件，然后复制到目标目录中。
为此，我创建了一个目录比较类，专门负责比较目录与文件。
此类中的比较方法中使用到了递归，Python中的递归记得最大是1000次，我觉得这个目录层次应该是够了吧？
其实本程序中，目录与文件的分析是重要部分：

+ 先判断根目录中不相同的目录与文件，然后分别记录。
+ 如果有相同的目录，使用递归比较这二个相同的目录。
+ 最后分别创建目录，复制文件到目标目录中。

## Tk Button传参方法

在构建GUI的时候，点击按钮激活的函数需要传参数进去，但Python并没有在Button中提供传参的方法，后来查到可以使用lambda

    command=lambda: def(参数1, 参数2)

这样即可达到函数传参的实现。

## 目录与文件的操作

通过这个小软件的制作，达到了对python目录及文件的分析及创建复制的模块功能的复制，功能上还可以继续扩展，后续有需要再继续添加。




'''


import filecmp  # 比较目录及文件的不同模块
import shutil #复制文件及目录
import os
import tkinter as tk
import tkinter.filedialog as filedialog  # 选择目录


class DirectoryComparison:
    '''目录比较类'''

    def __init__(self):
        self.dirdiff = []  # 用存放left与right不同的目录，
        self.filediff = []  # 用存放left与right不同文件，
        ##根据文件的不同可以互相进行复制补充。

    def fcmp(self, a, b, ign=None):
        print('a:{}'.format(a))
        print('b:{}'.format(b))
        '''
         递归比较两个目录中的不同，列出不同的目录及文件，备用复制。
        :param a:
        :param b:
        :param ign: 一个过滤文件list，某些情况下有些目录无法比较，比如mac os x下.DS_Store就无法比较，所以加入过滤列表中过滤掉。
        :return:
        '''
        if ign is None:
            ign = ['.DS_Store', '.git', '.idea']

        # 先递归取出left根目录与right根目录中不同的目录及文件，存入left_diff中
        df = filecmp.dircmp(a, b, ignore=ign)
        print(df.common)
        for f in df.left_only:
            if not f in ign:
                path = os.path.join(a, f)  # 组装绝对目录
                if os.path.isfile(path):
                    self.filediff.append(path)  # 将比较出来不同的文件放入list中。
                elif os.path.isdir(path):
                    #########################
                    # 如果是目录，使用walk递归归纳出所有需要copy的文件
                    # 这样的做的目的是为了最后的时候先创建出所有目录，然后再复制文件。
                    self.dirdiff.append(path)
                    for root, dirs, files in os.walk(path):
                        for d in dirs:
                            if not d in ign:
                                self.dirdiff.append(os.path.join(root, d))
                        for f in files:
                            if not f in ign:
                                self.filediff.append(os.path.join(root, f))

        if len(df.common) > 0:  # 如果还有相同的目录就继续递归
            for f in df.common:
                # 拼装出根目录下相同的两个目录名称，然后递归比较
                if not f in ign:
                    path_l = os.path.join(a, f)
                    path_r = os.path.join(b, f)
                    if os.path.isdir(path_l) and os.path.isdir(path_r):#如果两个都是目录那么递归比较一下
                        self.fcmp(path_l, path_r, ign)  # 递归比较


##########################################

dcmp = DirectoryComparison()  ## 创建一个目录比较对象


def dirdiff(a, b):
    '''比较两个目录'''
    dcmp.fcmp(a, b, ['.DS_Store', '.git', '.idea'])
    print('比较出不同的目录：{}'.format(dcmp.dirdiff))
    print('比较出不同的文件：{}'.format(dcmp.filediff))

def copyall(a,b):
    '''复制比较出来的不同目录和文件到目标位置'''
    print("开始创建目录++++++++++")
    for d in dcmp.dirdiff:
        tmp = d.replace(a, b)  # 拼装目录名
        if not os.path.isdir(tmp): # 如果目录不存在,或是只存在相关同名字的文件不是目录。
            print("开始创建目录{}".format(tmp))
            os.mkdir(tmp)
    print("开始复制文件++++++++++")
    for f in dcmp.filediff:
        tmp = f.replace(a,b)#拼装目录目录下的文件名
        print("开始复制文件到：{}".format(tmp))
        shutil.copy2(f,tmp)#复制文件到目标目录。





def main():
    def left_dirpath():
        print('按键已被点击')
        left_var.set('')  # 清空文本框里内容
        path = filedialog.askdirectory()
        left_var.set(path)

    def right_dirpath():
        print('按键已被点击')
        right_var.set("")
        path = filedialog.askdirectory()
        right_var.set(path)

    root = tk.Tk()
    root.title("目录比较工具 PyDirectoryComparison by py_sky")
    left_frame = tk.Frame(root)
    left_frame.pack(fill=tk.X, side=tk.TOP)
    right_frame = tk.Frame(root)
    right_frame.pack(fill=tk.X, side=tk.TOP)
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, side=tk.TOP)

    left_var = tk.StringVar()
    left_var.set("")
    left_dir = tk.Entry(left_frame, width=40, textvariable=left_var)
    left_dir.pack(fill=tk.X, side=tk.LEFT)
    left_btn = tk.Button(left_frame, text="选择左边目录", command=left_dirpath)
    left_btn.pack(fill=tk.X, side=tk.LEFT)

    right_var = tk.StringVar()
    right_var.set("")
    right_dir = tk.Entry(right_frame, width=40, textvariable=right_var)
    right_dir.pack(fill=tk.X, side=tk.LEFT)
    right_btn = tk.Button(right_frame, text="选择右边目录", command=right_dirpath)
    right_btn.pack(fill=tk.X, side=tk.LEFT)

    diff_btn = tk.Button(btn_frame, text="开始比较", command=lambda: dirdiff(left_var.get(), right_var.get()))
    diff_btn.pack(fill=tk.X)
    copy_btn = tk.Button(btn_frame, text="开始复制", command=lambda: copyall(left_var.get(), right_var.get()))
    copy_btn.pack(fill=tk.X)

    root.mainloop()


if __name__ == '__main__':
    main()

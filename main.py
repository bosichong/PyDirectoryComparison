# codeing=utf-8
# @Time    : 2017-09-01
# @Author  : J.sky
# @Mail    : bosichong@qq.com
# @Site    : www.17python.com
# @Title   : Python3 函数学习笔记
# @Url     : http://www.17python.com/blog/15
# @Details : 比较a,b两个目录中的目录及文件的不同，修复缺失目录及文件。


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

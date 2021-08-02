# モジュールのインポート
import os
import tkinter.filedialog
import tkinter.messagebox
import math

# ファイル選択ダイアログの表示
name = 'U8MB'
root = tkinter.Tk()
root.withdraw()
fTyp = [("", "*")]
iDir = os.path.abspath(os.path.dirname(__file__))
tkinter.messagebox.showinfo(name, '処理ファイルを選択してください！')
file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)

filesize = math.ceil(os.path.getsize(file) / 1000000)
print(filesize, "MB")

if filesize <= 8:
    switch = 1
else:
    switch = 2

# 処理ファイル名の出力
tkinter.messagebox.showinfo(name, file)
if switch == 2:
    tkinter.messagebox.showinfo('Judge', 'OVER 8MB')
else:
    tkinter.messagebox.showinfo('Judge', 'UNDER 8MB')

import sys
from tkinter import *
from tkinter.font import Font
from tkinter import messagebox

tkinter_gui = Tk()
select_codec = IntVar(value=3)


def test():
    print(select_codec.get())
    if select_codec.get() == 3:
        messagebox.showerror("Error", "Please select one.")
        print("Error")
    else:
        tkinter_gui.destroy()


def start_gui():
    # head_tkinter
    tkinter_gui.title(u"Prefab")
    tkinter_gui.geometry("600x200")
    fontname = "Lucida Grande"
    setup_font = Font(family=fontname, size=18)
    button_font = Font(family=fontname, size=16)
    # design_tkinter
    exp1 = Label(text=u"[Setup]\nSelect the availability and type of graphics board.", font=setup_font)
    exp1.pack()
    rdo1 = Radiobutton(value=0, text='Nvidia(NVENC_H264)', variable=select_codec)
    rdo1.place(x=70, y=80)
    rdo2 = Radiobutton(value=1, text='AMD(AMF_H264)', variable=select_codec)
    rdo2.place(x=70, y=110)
    rdo3 = Radiobutton(value=2, text='CPU(h264)', variable=select_codec)
    rdo3.place(x=70, y=140)
    button1 = Button(text=u'OK', font=button_font, width=8, command=test)
    button1.place(x=440, y=140)
    # start_tkinter


print("start")

start_gui()
print("mainloop")
tkinter_gui.mainloop()

print("end")
sys.exit()

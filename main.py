import math
import os
import sys
import re
import subprocess
import tkinter.filedialog
import tkinter.messagebox
from tkinter.font import Font
from tkinter import *

tkinter_gui = Tk()
select_codec = IntVar(value=2)


# reset
def tempremove():
    if os.path.exists('temp.mp4'):
        os.remove('temp.mp4')


# For PyInstaller
def subprocess_args(include_stdout=True):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env})
    return ret


# if sys.stdout.encoding != 'UTF-8':
#     sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
# if sys.stderr.encoding != 'UTF-8':
#     sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Path
maindir = os.path.dirname(os.path.realpath(__file__))
ffpath = maindir + '\\ffmpeg.exe'
print(ffpath)
ls_file_name = os.listdir()
print(ls_file_name)
if os.path.exists('output.mp4'):
    os.remove('output.mp4')

tempremove()
filesize = 0
suc = 0
cycle = 4
retry = 0


# tkinter


def start_gui():
    # head_tkinter
    tkinter_gui.title(u"Prefab")
    tkinter_gui.geometry("600x200")
    tkinter_gui.protocol('WM_DELETE_WINDOW', quit)
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
    rdo3 = Radiobutton(value=2, text='CPU(h264)   [Recommended]', variable=select_codec)
    rdo3.place(x=70, y=140)
    button1 = Button(text=u'OK', font=button_font, width=8, command=selected)
    button1.place(x=440, y=140)
    # start_tkinter


def gui_end():
    tkinter_gui.quit()
    tkinter_gui.destroy()


def selected():
    if select_codec.get() == 3:
        tkinter.messagebox.showerror("Error", "Please select one.")
        print("Error")
    else:
        gui_end()
        print("final select")
        print(select_codec.get())



while suc == 0:
    if retry == 0:
        start_gui()
        tkinter_gui.mainloop()
        sel = select_codec.get()
        name = '8mb-compressor'
        root = tkinter.Tk()
        root.withdraw()
        fTyp = [("", "*")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        if sel == 0:
            codec = 'h264_nvenc'
            prefix = 'cq'
            quality = 20
            nvenc = "-b:v 0"

        elif sel == 1:
            codec = 'h264_amf'
            prefix = 'crf'
            quality = 20
            nvenc = ""

        else:
            codec = 'h264'
            prefix = 'crf'
            quality = 18
            nvenc = ""
        tkinter.messagebox.showinfo(name, 'Select the source video.')
        print(codec)

    file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir, title='Select the source video.')
    rawfile = file
    root, ext = os.path.splitext(file)
    print(ext)

    if ext == ".mp4":

        # TODO: tkinter gui
        # GET Frame rate
        filesize = math.ceil(os.path.getsize(file) / 1000000)
        print(filesize, "MB")
        incommand = f'"{ffpath}" -y -i "{file}'
        rawinfo = subprocess.run(incommand, **subprocess_args(True), text=True)
        info = rawinfo.stderr
        print(info)
        countmp = info.find('fps')
        temps = (info[countmp - 6:countmp])
        if 's' in temps:
            tempfps = re.sub(r"\D", "", temps)
        else:
            tempfps = temps
        print(tempfps)
        resultfps = float(tempfps)

        while suc == 0:
            tempremove()
            if 55 > resultfps:
                fpswitch = 0
            else:
                # Drop fps
                fpswitch = 1
                cycle_str = cycle.__str__()
                command = f'"{ffpath}" -y -i "{rawfile}" -vcodec {codec} {nvenc} -vf decimate=cycle=2 temp.mp4'
                print(command)
                print("Drop fps")
                proc = subprocess.run(command, **subprocess_args(True), text=True)
                print(proc.stderr)
                os.rename("temp.mp4", "output.mp4")
                file = "output.mp4"
                filesize = math.ceil(os.path.getsize('output.mp4') / 1000000)
                print(filesize)
                if filesize >= 100:
                    quality = 50
                else:
                    quality = 30
            if filesize >= 250 and fpswitch == 0:
                quality = 35
            while filesize > 8:

                command = f'"{ffpath}" -y -i "{file}" -vcodec {codec} {nvenc} -{prefix} "{quality}" "output.mp4"'
                print(command)
                proc = subprocess.run(command, **subprocess_args(True))
                print(proc.stderr)

                if os.path.exists('output.mp4'):
                    filesize = math.ceil(os.path.getsize('output.mp4') / 1000000)
                    raw = os.path.getsize('output.mp4')
                    print(filesize, "MB", raw)
                    if codec == "h264_nvenc":
                        if raw <= 9000000 and quality < 51 or quality == 50:
                            quality = quality + 1
                        else:
                            quality = quality + 10
                            if quality > 51 and filesize > 8:
                                print("last phase failed.")
                                tkinter.messagebox.showwarning(name, 'Compression failed.')
                                suc = 1
                                break
                    else:
                        quality = quality + 1

                else:
                    print("FFMPEG ERROR")
                    tkinter.messagebox.showwarning(name, 'output.mp4 was not found.')
                    break

            else:
                print("COMPRESSED")
                tkinter.messagebox.showinfo(name, 'Compression successful.')
                suc = 1
                tempremove()

    elif ext == "":
        print("Cancelled")
        break

    else:
        tkinter.messagebox.showinfo(name, 'Only supports mp4 format.')
        retry = 1
        continue

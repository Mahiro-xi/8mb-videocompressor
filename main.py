# import modules
import os
import tkinter.filedialog
import tkinter.messagebox
import math
import subprocess

# reset
if os.path.exists('output.mp4'):
    os.remove('output.mp4')
path = os.getcwd()
ffpath = path + r'\ffmpeg.exe'
filesize = 0

# tkinter
name = 'U8MB'
root = tkinter.Tk()
root.withdraw()
fTyp = [("", "*")]
iDir = os.path.abspath(os.path.dirname(__file__))
sel = tkinter.messagebox.askyesno(name, 'Use NVENC codec?\nIf you have an NVIDIA graphics board, you can expect '
                                        'higher speed.')
if sel:
    codec = 'h264_nvenc'
    prefix = 'cq'
    quality = 20
    nvenc = "-b:v 0"
else:
    codec = 'h264'
    prefix = 'crf'
    quality = 18
    nvenc = ""
tkinter.messagebox.showinfo(name, 'Select the source video.')
file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
root, ext = os.path.splitext(file)
print(ext)

# extension
if ext == ".mp4":
    # filesize calculation
    filesize = math.ceil(os.path.getsize(file) / 1000000)
    print(filesize, "MB")

    # ffmpeg
    while filesize > 8:
        command = f'"{ffpath}" -i "{file}" -vcodec {codec} {nvenc} -{prefix} "{quality}" "output.mp4"'
        print(command)
        subprocess.run(command, capture_output=True, text=True, input="y")
        if os.path.exists('output.mp4'):
            filesize = math.ceil(os.path.getsize('output.mp4') / 1000000)
            raw = os.path.getsize('output.mp4')
            print(filesize, "MB", raw)
            if codec == "h264_nvenc":
                if raw <= 9000000:
                    quality = quality + 1
                else:
                    quality = quality + 10
            else:
                quality = quality + 1

        else:
            print("FFMPEG ERROR")
            break

    else:
        print("COMPRESSED")
else:
    tkinter.messagebox.showinfo('name', 'Only supports mp4 format.')

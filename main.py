# import modules
import math
import os
import re
import subprocess
import tkinter.filedialog
import tkinter.messagebox

# reset
if os.path.exists('output.mp4'):
    os.remove('output.mp4')

if os.path.exists('temp.mp4'):
    os.remove('temp.mp4')
path = os.getcwd()
ffpath = path + r'\ffmpeg.exe'
filesize = 0
suc = 0
cycle = 4
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
rawfile = file
root, ext = os.path.splitext(file)
print(ext)

# extension
if ext == ".mp4":
    # filesize calculation
    filesize = math.ceil(os.path.getsize(file) / 1000000)
    print(filesize, "MB")
    incommand = f'"{ffpath}" -i "{file}'
    rawinfo = subprocess.run(incommand, capture_output=False, text=True, input="y", stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    info = rawinfo.stderr
    countmp = info.find('fps')
    temps = (info[countmp - 6:countmp])
    if 's' in temps:
        tempfps = re.sub(r"\D", "", temps)
    else:
        tempfps = temps
    resultfps = float(tempfps)

    while suc == 0:
        if os.path.exists('temp.mp4'):
            os.remove('temp.mp4')
        if 55 > resultfps:
            fpswitch = 0
            fpsprefix = ""
        else:
            # Drop fps
            fpswitch = 1
            cycle_str = cycle.__str__()
            fpsprefix = "-vf decimate=cycle=" + cycle_str
            command = f'"{ffpath}" -i "{rawfile}" -vcodec {codec} {nvenc} {fpsprefix} "temp.mp4'
            print(command)
            print("Drop fps")
            proc = subprocess.run(command, capture_output=False, text=True, input="y", stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            print(proc.stderr)
            file = "temp.mp4"
            filesize = math.ceil(os.path.getsize('temp.mp4') / 1000000)
            print(filesize)
            if filesize >= 100:
                quality = 50
            else:
                quality = 30
        if filesize >= 250 and fpswitch == 0:
            quality = 35
        # ffmpeg
        while filesize > 8:

            command = f'"{ffpath}" -i "{file}" -vcodec {codec} {nvenc} -{prefix} "{quality}" "output.mp4"'
            print(command)
            proc = subprocess.run(command, capture_output=False, text=True, input="y", stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

            # log output
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
                        if quality > 51 and fpswitch == 1 and filesize > 8 and cycle == 4:
                            cycle = 2
                            break
                        elif quality > 51 and filesize > 8 and cycle == 2:
                            print("last phase failed.")
                            suc = 1
                            break
                else:
                    quality = quality + 1

            else:
                print("FFMPEG ERROR")
                break

        else:
            print("COMPRESSED")
            suc = 1
else:
    tkinter.messagebox.showinfo('name', 'Only supports mp4 format.')

import math
import os
import re
import subprocess
import tkinter.filedialog
import tkinter.messagebox

# reset
def tempremove():
    if os.path.exists('temp.mp4'):
        os.remove('temp.mp4')


# For PyInstaller
# def subprocess_args(include_stdout=True):
#    if hasattr(subprocess, 'STARTUPINFO'):
#        si = subprocess.STARTUPINFO()
#        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
#        env = os.environ
#    else:
#        si = None
#        env = None
#    if include_stdout:
#        ret = {'stdout': subprocess.PIPE}
#    else:
#        ret = {}
#    ret.update({'stdin': subprocess.PIPE,
#                'stderr': subprocess.PIPE,
#                'startupinfo': si,
#                'env': env})
#    return ret


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
while suc == 0:
    if retry == 0:
        name = '8mb-compressor'
        root = tkinter.Tk()
        root.withdraw()
        fTyp = [("", "*")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        sel = tkinter.messagebox.askyesno(name,
                                          'Use NVENC or AMF codec?\nIf you have a graphics board, you can expect '
                                          'higher speed.')
        #TODO: add h264_amf codec
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
                file = "temp.mp4"
                filesize = math.ceil(os.path.getsize('temp.mp4') / 1000000)
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

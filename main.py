import math
import os
import sys
import re
import subprocess
import tkinter.filedialog
import tkinter.messagebox
from tkinter.font import Font
from tkinter import *


class VideoCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(u"Prefab")
        self.root.geometry("600x200")
        self.select_codec = IntVar(value=0)
        self.ffpath = self.get_ffmpeg_path()
        self.setup_gui()

    def setup_gui(self):
        fontname = "Lucida Grande"
        setup_font = Font(family=fontname, size=18)
        button_font = Font(family=fontname, size=16)

        exp1 = Label(text=u"[Setup]\nSelect the availability and type of graphics board.", font=setup_font)
        exp1.pack()

        Radiobutton(value=0, text='Nvidia(NVENC_H264)', variable=self.select_codec).place(x=70, y=80)
        Radiobutton(value=1, text='AMD(AMF_H264)', variable=self.select_codec).place(x=70, y=110)
        Radiobutton(value=2, text='CPU(h264)   [Recommended]', variable=self.select_codec).place(x=70, y=140)

        Button(text=u'OK', font=button_font, width=8, command=self.selected).place(x=440, y=140)

    def selected(self):
        if self.select_codec.get() not in [0, 1, 2]:
            tkinter.messagebox.showerror("Error", "Please select one.")
        else:
            self.root.quit()
            self.root.destroy()

    def get_ffmpeg_path(self):
        maindir = os.path.dirname(os.path.realpath(__file__))
        ffpath = os.path.join(maindir, 'ffmpeg.exe')
        path_list = os.environ['PATH'].split(os.pathsep)

        for path in path_list:
            if os.path.exists(os.path.join(path, 'ffmpeg.exe')):
                ffpath = os.path.join(path, 'ffmpeg.exe')
                break

        if os.path.isfile(ffpath):
            print("ffmpeg is ready!")
            return ffpath
        else:
            print("[Error] FFmpeg is not found.", file=sys.stderr)
            exit()

    def run(self):
        self.root.mainloop()


def subprocess_args(include_stdout=True):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    ret = {'stdin': subprocess.PIPE, 'stderr': subprocess.PIPE, 'startupinfo': si, 'env': env}
    if include_stdout:
        ret['stdout'] = subprocess.PIPE
    return ret


def get_video_info(file, ffpath):
    command = f'"{ffpath}" -y -i "{file}"'
    try:
        rawinfo = subprocess.run(command, **subprocess_args(True), text=True)
        rawinfo.check_returncode()
        return rawinfo.stderr
    except subprocess.CalledProcessError as e:
        print(f"Failed to get video info: {e}")
        return None


def parse_fps(info):
    countmp = info.find('fps')
    fps_string = info[countmp - 6:countmp]
    return float(re.sub(r"\D", "", fps_string)) if 's' in fps_string else float(fps_string)


def compress_video(input_file, output_file, codec, quality, nvenc, prefix, ffpath, max_size_mb=8):
    while True:
        command = f'"{ffpath}" -y -i "{input_file}" -vcodec {codec} {nvenc} -{prefix} "{quality}" "{output_file}"'
        try:
            proc = subprocess.run(command, **subprocess_args(True))
            proc.check_returncode()

            if os.path.exists(output_file):
                filesize = math.ceil(os.path.getsize(output_file) / 1000000)
                if filesize <= max_size_mb:
                    return True
                quality += 1
            else:
                print("FFMPEG ERROR: output file not found.")
                tkinter.messagebox.showwarning("Compression Failed", f'{output_file} was not found.')
                return False
        except subprocess.CalledProcessError as e:
            print(f"FFMPEG execution failed: {e}")
            tkinter.messagebox.showwarning("Compression Failed", "FFMPEG execution failed.")
            return False


def main():
    # Initialize GUI
    root = Tk()
    gui = VideoCompressorGUI(root)
    gui.run()

    # Get user selections
    codec_map = {0: 'h264_nvenc', 1: 'h264_amf', 2: 'h264'}
    prefix_map = {0: 'cq', 1: 'crf', 2: 'crf'}
    quality_map = {0: 20, 1: 20, 2: 18}
    nvenc_map = {0: "-b:v 0", 1: "", 2: ""}
    codec = codec_map[gui.select_codec.get()]
    prefix = prefix_map[gui.select_codec.get()]
    quality = quality_map[gui.select_codec.get()]
    nvenc = nvenc_map[gui.select_codec.get()]

    # Select video file
    tkinter.messagebox.showinfo("8mb-compressor", 'Select the source video.')
    file = tkinter.filedialog.askopenfilename(filetypes=[("", "*")],
                                              initialdir=os.path.abspath(os.path.dirname(__file__)),
                                              title='Select the source video.')
    if not file:
        print("No file selected. Exiting.")
        return

    root, ext = os.path.splitext(file)
    if ext != ".mp4":
        tkinter.messagebox.showinfo("8mb-compressor", 'Only supports mp4 format.')
        return

    # Get video info and determine FPS
    info = get_video_info(file, gui.ffpath)
    if not info:
        return

    resultfps = parse_fps(info)
    output_file = "output.mp4"

    # Adjust FPS if necessary
    if resultfps > 55:
        command = f'"{gui.ffpath}" -y -i "{file}" -vcodec {codec} {nvenc} -vf decimate=cycle=2 temp.mp4'
        subprocess.run(command, **subprocess_args(True))
        os.rename("temp.mp4", output_file)
        file = output_file

    # Compress video
    if compress_video(file, output_file, codec, quality, nvenc, prefix, gui.ffpath):
        tkinter.messagebox.showinfo("8mb-compressor", 'Compression successful.')
        print("Compression successful.")
    else:
        print("Compression failed.")

    # Clean up temporary files
    if os.path.exists('temp.mp4'):
        os.remove('temp.mp4')


if __name__ == "__main__":
    main()
"""Render simple original 2D animated stories from story_generator.py JSON.

Requires Pillow, ffmpeg, ffprobe, and edge-tts for narration.
Run --silent-test to verify rendering without network/TTS (no narration).
"""
import argparse
import asyncio
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 960, 540, 12


def cmd(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def duration(path):
    p = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(path)], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())


def ellipse(d, bounds, fill, outline=None, width=1):
    d.ellipse(tuple(map(int, bounds)), fill=fill, outline=outline, width=width)


def fox(d, x, y, bob):
    y += bob
    # tail behind body
    d.ellipse((x-92,y+36,x-8,y+104), fill='#e97c28')
    d.polygon([(x-85,y+48),(x-106,y+48),(x-96,y+77)], fill='#fff1d4')
    ellipse(d,(x-55,y+58,x+57,y+176),'#ed8735')
    ellipse(d,(x-32,y+84,x+34,y+165),'#fff3de')
    ellipse(d,(x-47,y+159,x-2,y+181),'#bb5e2c')
    ellipse(d,(x+5,y+159,x+49,y+181),'#bb5e2c')
    d.polygon([(x-61,y-9),(x-43,y-84),(x-5,y-34),(x+9,y-34),(x+48,y-84),(x+65,y-8)], fill='#ef8b34')
    d.polygon([(x-46,y-18),(x-38,y-59),(x-12,y-29)], fill='#ffd6b8')
    d.polygon([(x+19,y-29),(x+42,y-59),(x+49,y-18)], fill='#ffd6b8')
    ellipse(d,(x-66,y-42,x+66,y+72),'#f3943b')
    ellipse(d,(x-47,y+12,x+47,y+72),'#fff0d8')
    ellipse(d,(x-31,y-5,x-14,y+15),'#2e3244')
    ellipse(d,(x+14,y-5,x+31,y+15),'#2e3244')
    ellipse(d,(x-27,y-1,x-22,y+4),'white')
    ellipse(d,(x+18,y-1,x+23,y+4),'white')
    ellipse(d,(x-10,y+24,x+10,y+37),'#353340')
    d.arc((x-16,y+30,x+16,y+54),0,180,fill='#7b4536',width=3)


def bunny(d, x, y, bob):
    y += bob
    ellipse(d,(x-45,y+55,x+45,y+175),'#81c5f0')
    ellipse(d,(x-25,y+90,x+25,y+162),'#e5f6ff')
    ellipse(d,(x-44,y+159,x-1,y+180),'#5ca3d4')
    ellipse(d,(x+2,y+159,x+44,y+180),'#5ca3d4')
    ellipse(d,(x-47,y-122,x-10,y-12),'#81c5f0')
    ellipse(d,(x+10,y-122,x+47,y-12),'#81c5f0')
    ellipse(d,(x-36,y-108,x-19,y-24),'#f6bbd6')
    ellipse(d,(x+19,y-108,x+36,y-24),'#f6bbd6')
    ellipse(d,(x-60,y-41,x+60,y+70),'#89c9f2')
    ellipse(d,(x-40,y+15,x+40,y+66),'#e6f7ff')
    ellipse(d,(x-30,y-4,x-14,y+16),'#29354c')
    ellipse(d,(x+14,y-4,x+30,y+16),'#29354c')
    ellipse(d,(x-25,y, x-21,y+5),'white')
    ellipse(d,(x+19,y,x+23,y+5),'white')
    ellipse(d,(x-8,y+27,x+8,y+37),'#e67fa4')
    d.arc((x-16,y+29,x+16,y+51),0,180,fill='#54739c',width=3)


def font(size):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf']:
        if Path(p).exists():
            return ImageFont.truetype(p,size)
    return ImageFont.load_default()


def frame(scene, title, idx, t):
    im = Image.new('RGB',(W,H),'#bfe9ff')
    d = ImageDraw.Draw(im)
    # sky, sun and gently moving clouds
    ellipse(d,(735,45,835,145),'#ffdf69')
    for cx,cy in [(115,92),(405,125),(650,80)]:
        shift = int(12*math.sin(t*.45+cx))
        ellipse(d,(cx+shift,cy,cx+130+shift,cy+46),'#ffffff')
        ellipse(d,(cx+30+shift,cy-24,cx+93+shift,cy+39),'#ffffff')
    d.ellipse((-150,265,580,700),fill='#a1d78d')
    d.ellipse((390,275,1200,750),fill='#7fc58e')
    d.rectangle((0,435,W,H),fill='#79bd75')
    for j in range(12):
        fx = 45+j*83
        fy = 446+(j%3)*25
        ellipse(d,(fx-7,fy-7,fx+7,fy+7),['#ffb8c7','#ffe187','#e1c4ff'][j%3])
        ellipse(d,(fx-3,fy-3,fx+3,fy+3),'#fff7df')
    # soft character shadows
    ellipse(d,(210,468,400,490),'#6cae6d')
    ellipse(d,(565,468,735,490),'#6cae6d')
    fox(d,305+int(12*math.sin(t*.7)),280,int(5*math.sin(t*2.5)))
    bunny(d,650+int(9*math.sin(t*.6+.8)),278,int(5*math.sin(t*2.4+1)))
    d.rounded_rectangle((25,18,560,62),radius=18,fill='#ffffff',outline='#b5d2e2',width=2)
    d.text((44,25),title[:34],font=font(23),fill='#34405c')
    d.rounded_rectangle((350,485,610,527),radius=16,fill='#ffffff')
    d.text((375,492),f'Scene {idx} of 6',font=font(19),fill='#53658b')
    return im


async def narrate(text, dest):
    import edge_tts
    await edge_tts.Communicate(text, 'en-US-AriaNeural', rate='-8%').save(str(dest))


def make_video(story, output, silent_test=False):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise RuntimeError('ffmpeg and ffprobe must be installed')
    scenes=story['scenes']
    if not scenes:
        raise ValueError('Story has no scenes')
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        clips=[]
        for i,scene in enumerate(scenes,1):
            narration=scene['narration']
            audio=tmp/f'audio{i}.mp3'
            if not silent_test:
                asyncio.run(narrate(narration,audio))
                seconds=max(3.0,duration(audio)+0.8)
            else:
                seconds=3.0
            frames=math.ceil(seconds*FPS)
            clip=tmp/f'scene{i}.mp4'
            ff=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0']
            if silent_test:
                ff+=['-f','lavfi','-i','anullsrc=channel_layout=stereo:sample_rate=44100']
            else:
                ff+=['-i',str(audio)]
            ff+=['-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','27','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-t',str(frames/FPS),'-movflags','+faststart',str(clip)]
            proc=subprocess.Popen(ff,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                for f in range(frames):
                    proc.stdin.write(frame(scene,story['title'],i,f/FPS).tobytes())
                proc.stdin.close()
                err=proc.stderr.read().decode(errors='replace')
                if proc.wait()!=0:
                    raise RuntimeError(f'ffmpeg failed on scene {i}: {err}')
            except BaseException:
                proc.kill()
                proc.wait()
                raise
            clips.append(clip)
            print(f'Scene {i}/{len(scenes)} rendered ({seconds:.1f}s)',flush=True)
        concat=tmp/'clips.txt'
        concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in clips),encoding='utf-8')
        cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(output)])
    print(f'Created video: {output} ({output.stat().st_size:,} bytes)')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',default='output/episode.json')
    p.add_argument('--output',default='output/cartoon.mp4')
    p.add_argument('--silent-test',action='store_true',help='Offline video test with silent audio; not for publishing')
    a=p.parse_args()
    story=json.loads(Path(a.input).read_text(encoding='utf-8'))
    make_video(story,a.output,a.silent_test)


if __name__=='__main__':
    main()

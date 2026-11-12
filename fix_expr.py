# Repairs a Dissidia 012 costume model (GMO) whose face expressions do not
# change: restores the expression data's target texture names, and rebuilds
# the expression sheets in the face textures' colours and palettes.

import struct,re,sys

if len(sys.argv) !=3:
	print("\n")
	print("Usage: python3 fix_expr.py input_edat output_edat")
	print("Input edat should be the largest edat file in the mod folder, which contains the GMO. Output edat will be the fixed file.")
	print("\n")
	sys.exit()

d=bytearray(open(sys.argv[1],'rb').read())
srcs=[m.start() for m in re.finditer(rb'source:p_[a-z]{3}\d{3}_\d\da\.tm2',bytes(d))]
for m in list(re.finditer(rb'target[^:][\x20-\x7e]{11}\.tm2',bytes(d))):
    h=m.start(); nxt=min(s for s in srcs if s>h); base=bytes(d[nxt+7:nxt+18])
    d[h+6:h+18]=b':'+base; print('target name restored at',hex(h),'->',bytes(d[h:h+22]).decode())
pos=[i for i in range(len(d)) if d.startswith(b'MIG.00.1PSP',i)]
def info(g0):
    res={}
    def blocks(off,end):
        while off+16<=end:
            bid,unk,size,nxt,dat=struct.unpack_from('<HHIII',d,off)
            if size<16: return
            yield bid,off,size,dat
            if bid in (2,3): yield from blocks(off+dat,off+size)
            off+=size
    end=g0+16+struct.unpack_from('<I',d,g0+16+4)[0]
    for bid,off,size,dat in blocks(g0+16,end):
        if bid in (4,5):
            b=off+dat
            hl,_,fmt,order,w,h,bpp=struct.unpack_from('<HHHHHHH',d,b)
            res[bid]=(b+struct.unpack_from('<I',d,b+0x1c)[0],fmt,order,w,h)
    return res
targets=[(m.start(),m.group()) for m in re.finditer(rb'target:p_[a-z]{3}\d{3}_(\d\d)\.tm2\x00\x00',bytes(d))]
def fix(face_i,sheet_i,tlist):
    f=info(pos[face_i]); s=info(pos[sheet_i])
    fio,ffmt,fo_order,fw,fh=f[4]; fpo,fpf=f[5][0],f[5][1]; sio,sfmt,so_order,sw,sh=s[4]; spo,spf=s[5][0],s[5][1]
    assert fo_order==0 and so_order==0 and ffmt==5 and sfmt==5 and fpf==3 and spf==3,'texture format this script does not handle'
    fpal=[tuple(d[fpo+i*4:fpo+i*4+4]) for i in range(256)]; spal=[tuple(d[spo+i*4:spo+i*4+4]) for i in range(256)]
    fstride=(fw+15)//16*16; sstride=(sw+15)//16*16
    face=lambda x,y: fpal[d[fio+y*fstride+x]]
    px=[[spal[d[sio+y*sstride+x]] for x in range(sw)] for y in range(sh)]
    out=[[None]*sw for _ in range(sh)]; cache={}
    def nearest(c):
        if c not in cache:
            cache[c]=min(range(256),key=lambda k:(fpal[k][0]-c[0])**2+(fpal[k][1]-c[1])**2+(fpal[k][2]-c[2])**2+(255-fpal[k][3])**2)
        return cache[c]
    for (off,name),sx in zip(tlist,(0,48,96)):
        x0,y0,w,h=struct.unpack_from('<4I',d,off+len(name))
        for k in range(5):
            sy=48*k
            if sy+h>sh: continue
            for j in range(h):
                for i in range(w):
                    u=face(x0+i,y0+j); o0=px[j][sx+i]; ok=px[sy+j][sx+i]
                    out[sy+j][sx+i]=nearest(tuple(max(0,min(255,ok[n]+u[n]-o0[n])) for n in range(3)))
    for y in range(sh):
        for x in range(sw):
            d[sio+y*sstride+x]=out[y][x] if out[y][x] is not None else nearest(px[y][x][:3])
    d[spo:spo+1024]=d[fpo:fpo+1024]
    print('expression sheet',sheet_i,'rebuilt for face texture',face_i)
# per model: textures are [face, ..., sheet]; the sheet is the 128x256 one after its face
faces=[i for i,p in enumerate(pos) if info(p)[4][3:]==(256,256)]
sheets=[i for i,p in enumerate(pos) if info(p)[4][3:]==(128,256)]
for n,sheet in enumerate(sheets):
    face=max(i for i in faces if i<sheet and (n==0 or i>sheets[n-1]) and True) if False else [i for i in faces if i<sheet and (n==0 or i>sheets[n-1])][0]
    fix(face,sheet,targets[3*n:3*n+3])
open(sys.argv[2],'wb').write(d)

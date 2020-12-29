import vapoursynth as vs
from vsutil import depth, split, join, plane
import kagefunc as kgf
import insaneAA
import fvsfunc as fvf
import havsfunc as hvf
import mvsfunc as mvf
import finedehalo

core = vs.core
core.max_cache_size = 1000

src = core.ffms2.Source(r'E:\Anime Remux\00000.mkv')
src = core.std.AssumeFPS(src, fpsnum=24000, fpsden=1001)

src = core.fb.FillBorders(src, 2,2,2,2, "fillmargins")
src = finedehalo.fine_dehalo(src, darkstr=0, brightstr=0.5, showmask=0, rx=1.8, ry=1.8, thmi=50, thma=95, useMtEdge=True)

Y, U, V = split(src)
descaledY = insaneAA.revert_upscale(Y, descale_strength=0.28, kernel='bicubic', descale_width=1280, descale_height=720, bicubic_b=1/3, bicubic_c=1/3) # I don't think so
resizedY = core.resize.Bicubic(descaledY, 1280, 720, src_left=0.5)
resizedU = core.resize.Bicubic(U, 1280, 720, src_left=0.5)
resizedV = core.resize.Bicubic(V, 1280, 720, src_left=0.5)
out = join([resizedY, resizedU, resizedV])

src16 = mvf.Depth(out, depth=16, dither=3)

y = plane(src16, 0)
pf = core.dfttest.DFTTest(y, sigma=4, tbsize=3, opt=3)
den = hvf.SMDegrain(y, tr=2, thSAD=32, thSADC=32, blksize=8, overlap=4, prefilter=pf)
out = core.std.ShufflePlanes([den, src16, src16], [0,1,2], src16.format.color_family)

y = plane(out, 0)
db = fvf.GradFun3(y, smode=2, thr_det=2).neo_f3kdb.Deband(grainy=15, sample_mode=4, keep_tv_range=True, output_depth=16)

out = core.std.ShufflePlanes([db, out, out], [0, 1, 2], out.format.color_family)

sub = core.sub.TextFile(out, r'C:\Users\George\Desktop\Hanasaku 01 Verificat.ass')
sub = core.sub.TextFile(sub, r'C:\Users\George\Desktop\Hanasaku cantec.ass')
sub = core.sub.TextFile(sub, r'C:\Users\George\Desktop\credite evo.ass')

out = core.fmtc.bitdepth(sub, bits=10)

# Wtf is this?

out.set_output()
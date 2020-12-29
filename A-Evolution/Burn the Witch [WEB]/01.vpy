import vapoursynth as vs
from vsutil import depth, split, join, plane
import vsTAAmbk as taa
import havsfunc as hvf


core = vs.core
core.max_cache_size = 4096

src = core.ffms2.Source(r'F:\Downloads\[Erai-raws] Burn the Witch [1080p][Multiple Subtitle]\[Erai-raws] Burn the Witch - 01 [1080p][Multiple Subtitle].mkv').std.AssumeFPS(fpsnum=24000, fpsden=1001).resize.Spline36(1280, 720)

Y, U, V = split(src)

aa = taa.TAAmbk(Y, aatype='Eedi3')
src = join([aa, U, V])

src = depth(src, 16)

Y, U, V = split(src)

sigma = 4

pre = core.fft3dfilter.FFT3DFilter(Y, sigma=sigma*0.8, sigma2=sigma*0.6, sigma3=sigma*0.4, sigma4=sigma*0.2, bw=16, bh=16, ow=8, oh=8, bt=2, ncpu=4)

denoise = hvf.SMDegrain(Y, tr=1, thSAD=300, thSADC=150, thSCD1=200, thSCD2=200, contrasharp=True, RefineMotion=True, limit=4, limitc=3, pel=1, prefilter=pre, search=3, blksize=16, overlap=8)

denoised = join([denoise, U, V])

db_args = dict(iterations=2, threshold=4, radius=16)
db = join([core.placebo.Deband(plane(denoised, 0), grain=6, **db_args), core.placebo.Deband(plane(denoised, 1), grain=0, **db_args), core.placebo.Deband(plane(denoised, 2), grain=0, **db_args)])
db = join([db, plane(denoised, 1), plane(denoised, 2)])

sub = core.sub.TextFile(db, r'C:\Users\George\Desktop\Burn\Burn_the_Witch_-_01_REVERIFICAT.ass')

out = depth(sub, 10)

out.set_output()
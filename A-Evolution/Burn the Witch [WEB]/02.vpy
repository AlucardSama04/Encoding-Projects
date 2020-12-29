import vapoursynth as vs
from vsutil import get_y, depth, split, join, plane
import vsTAAmbk as taa
import havsfunc as hvf
import finedehalo

core = vs.core
core.max_cache_size = 4096

src = core.ffms2.Source(r'F:\Downloads\[Erai-raws] Burn the Witch [1080p][Multiple Subtitle]\[Erai-raws] Burn the Witch - 02 [1080p][Multiple Subtitle].mkv').std.AssumeFPS(fpsnum=24000, fpsden=1001).resize.Bicubic(1280, 720, filter_param_a=1/3, filter_param_b=1/3)

Y = get_y(src)

aa = taa.TAAmbk(Y, aatype=6)

src = core.std.ShufflePlanes([aa, src, src], planes=[0, 1, 2], colorfamily=vs.YUV)
src = depth(src, 16)

sigma = 4

pre = core.fft3dfilter.FFT3DFilter(src, sigma=sigma*0.8, sigma2=sigma*0.6, sigma3=sigma*0.4, sigma4=sigma*0.2, bw=16, bh=16, ow=8, oh=8, bt=2, ncpu=4, planes=[0])

denoise = hvf.SMDegrain(src, tr=2, thSAD=400, thSADC=200, thSCD1=300, thSCD2=300, contrasharp=True, RefineMotion=True, limit=4, limitc=3, pel=1, prefilter=pre, search=3, blksize=16, overlap=8, plane=[0])

denoised = core.std.ShufflePlanes([denoise, src, src], [0, 1, 2], vs.YUV)

db_args = dict(iterations=2, threshold=4, radius=16)
db = join([core.placebo.Deband(plane(denoised, 0), grain=6, **db_args), core.placebo.Deband(plane(denoised, 1), grain=0, **db_args), core.placebo.Deband(plane(denoised, 2), grain=0, **db_args)])
db = join([db, plane(denoised, 1), plane(denoised, 2)])

sub = core.sub.TextFile(db, r'C:\Users\George\Desktop\Burn2\Burn_the_Witch_-_02_REVERIFICAT.ass')

out = depth(sub, 10)
out.set_output()
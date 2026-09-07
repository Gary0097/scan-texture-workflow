from pathlib import Path
import time,json
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.fft import fft2,ifft2,fftfreq
Image.MAX_IMAGE_PIXELS=400000000
out=Path('output/full-frequency-review');out.mkdir(parents=True,exist_ok=True)
t=time.perf_counter()
src=Image.open('output/texture-confirmation/01_扫描白点修复.tif')
a=np.array(src);height,width=a.shape;n=192;step=48;pad=n
p=np.pad(a,((pad,pad),(pad,pad)),mode='reflect')
w=np.outer(np.hanning(n),np.hanning(n)).astype(np.float32);ww=w*w
fy,fx=np.meshgrid(fftfreq(n),fftfreq(n),indexing='ij');r=np.hypot(fx,fy)
band=(r>.045)&(r<.23)&(fy>0)
acc=np.zeros((n,p.shape[1]),np.float32);den=np.zeros_like(acc)
result=np.zeros((height,width),np.uint16)
@lru_cache(maxsize=256)
def rejection(iy,ix):
 vx,vy=fx[iy,ix],fy[iy,ix];h=np.ones((n,n))
 for k in (1,2,3):
  if k*np.hypot(vx,vy)>.48:continue
  for sign in (-1,1):
   dist=(fx-sign*k*vx)**2+(fy-sign*k*vy)**2
   h*=1-np.exp(-dist/(2*.026**2))
 h[r<.025]=1
 return h.astype(np.float32)
count=0;clipped=0;maxerr=0;sumshift=0.;minimum=255.;maximum=0.
for y in range(0,p.shape[0]-n+1,step):
 for x in range(0,p.shape[1]-n+1,step):
  patch=p[y:y+n,x:x+n].astype(np.float32);mean=np.sum(patch*w)/w.sum()
  f=fft2((patch-mean)*w);power=abs(f)**2
  iy,ix=np.unravel_index(np.argmax(np.where(band,power,0)),power.shape)
  conf=power[iy,ix]/(np.median(power[band])+1e-8)
  if conf>30:f*=rejection(iy,ix)
  filtered=ifft2(f).real+mean*w
  acc[:,x:x+n]+=filtered*w;den[:,x:x+n]+=ww;count+=1
 lo=max(y,pad);hi=min(y+step,pad+height)
 if hi>lo:
  b=acc[lo-y:hi-y,pad:pad+width]/np.maximum(den[lo-y:hi-y,pad:pad+width],1e-12)
  minimum=min(minimum,float(b.min()));maximum=max(maximum,float(b.max()))
  clipped+=int(np.count_nonzero((b<0)|(b>255)))
  sumshift+=float(np.sum(b-a[lo-pad:hi-pad],dtype=np.float64))
  result[lo-pad:hi-pad]=np.rint(np.clip(b,0,255)*257).astype(np.uint16)
 acc[:-step]=acc[step:];acc[-step:]=0;den[:-step]=den[step:];den[-step:]=0
 if y%(step*20)==0:
  print(json.dumps({'processed_rows':max(0,min(height,y+step-pad)),'total_rows':height,'seconds':round(time.perf_counter()-t,1)}),flush=True)
print('Saving full TIFF',flush=True)
dest=out/'全尺寸去波纹底图_局部频域宽带_审核版16位.tif'
Image.fromarray(result).save(dest,compression='tiff_lzw',dpi=(2540,2540))
preview=Image.fromarray((result//257).astype(np.uint8));preview.resize((1900,1500),Image.Resampling.LANCZOS).save(out/'整图预览.png')
for name,x,y in [('中心',8500,6500),('左上',1500,1500),('右下',16000,12000)]:
 Image.fromarray(result[y:y+1200,x:x+1600]).save(out/(name+'_原尺寸局部16位.tif'),compression='tiff_lzw',dpi=(2540,2540))
 preview.crop((x,y,x+1600,y+1200)).save(out/(name+'_原尺寸局部.png'))
check=Image.open(dest)
report={'source':str(src.filename),'output':str(dest),'size':check.size,'mode':check.mode,'dpi':[float(v) for v in check.info['dpi']],'seconds':time.perf_counter()-t,'windows':count,'unclipped_range':[minimum,maximum],'clipped_pixels':clipped,'mean_gray_shift':sumshift/(height*width),'parameters':{'window':192,'stride':48,'notch_sigma':.026,'confidence_threshold':30},'status':'review_only_residual_lines_not_accepted_for_production'}
assert check.size==(19000,15000) and check.mode=='I;16'
for x,y in [(0,0),(8500,6500),(18900,14900)]:
 assert np.array_equal(np.array(check.crop((x,y,x+100,y+100))),result[y:y+100,x:x+100])
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'审核说明.txt').write_text('全尺寸局部频域宽带审核版\n19000×15000 像素，16 位灰度 TIFF，2540 DPI。\n沿用局部宽带试验，保留原稿灰度映射；未应用先前的对比度拉伸。白点修复母版作为输入。\n本版供审核，残留细线与颗粒仍可能存在；未做无缝接边。请在 ArtForm 使用与前次相同的尺寸、深度及白色凸起设置比较，记录参数。\n整图 PNG 是缩小预览，细节应查看全尺寸 TIFF 或原尺寸局部。16 位工作文件不代表恢复了扫描原本缺失的信息。\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)

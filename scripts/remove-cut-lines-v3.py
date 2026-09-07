from pathlib import Path
import json,time
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,label,find_objects
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
Image.MAX_IMAGE_PIXELS=400000000
out=Path('output/clean-base-v3');out.mkdir(parents=True,exist_ok=True)
t=time.perf_counter()
path='output/full-frequency-review/全尺寸去波纹底图_局部频域宽带_审核版16位.tif'
a=np.array(Image.open(path));height,width=a.shape
m=a>=220*257;lab,n=label(m);objects=find_objects(lab);del lab
changes=[];mask=np.zeros(a.shape,np.uint8)
for sl in objects:
 if sl is None:continue
 sy,sx=sl;y0=max(0,sy.start-1);y1=min(height,sy.stop+1);x0=max(0,sx.start-1);x1=min(width,sx.stop+1)
 ph,pw=y1-y0,x1-x0;target=a[y0:y1,x0:x1].astype(np.float32)
 best=None;score=np.inf
 for dy,dx in [(0,16),(0,-16),(16,0),(-16,0),(16,16),(-16,-16),(32,0),(-32,0),(0,32),(0,-32),(32,32),(-32,-32)]:
  yy=y0+dy;xx=x0+dx
  if yy<0 or xx<0 or yy+ph>height or xx+pw>width:continue
  patch=a[yy:yy+ph,xx:xx+pw]
  if patch.max()>=220*257:continue
  valid=target<220*257
  err=float(np.mean((patch.astype(np.float32)[valid]-target[valid])**2)) if valid.any() else abs(float(patch.mean())-140*257)
  if err<score:score=err;best=(yy,xx,patch.copy())
 if best is None:raise RuntimeError('No clean donor at '+str([x0,y0]))
 yy,xx,patch=best;a[y0:y1,x0:x1]=patch;mask[y0:y1,x0:x1]=255
 changes.append({'target':[x0,y0,x1,y1],'donor':[xx,yy,xx+pw,yy+ph]})
assert not np.any(a>=220*257)
Image.fromarray(a).save(out/'01_亮点邻域仿制修复_16位.tif',compression='tiff_lzw',dpi=(2540,2540))
Image.fromarray(mask).save(out/'01_图章修补位置.png');del mask,m
(out/'图章取样记录.json').write_text(json.dumps(changes,ensure_ascii=False),encoding='utf-8')
print('Clone repair complete: '+str(len(changes)),flush=True)
b=np.empty_like(a);sigma=12;halo=64
for y in range(0,height,512):
 end=min(height,y+512);start=max(0,y-halo);stop=min(height,end+halo)
 tile=gaussian_filter(a[start:stop].astype(np.float32),sigma=sigma,mode='reflect',truncate=4)
 b[y:end]=np.rint(tile[y-start:end-start]).astype(np.uint16)
 if y%2048==0:print('Clean surface rows '+str(end)+'/'+str(height),flush=True)
dest=out/'02_去切割线_仅底部花纹_全尺寸16位.tif'
Image.fromarray(b).save(dest,compression='tiff_lzw',dpi=(2540,2540))
Image.fromarray((b//257).astype(np.uint8)).resize((1900,1500),Image.Resampling.LANCZOS).save(out/'整图预览.png')
font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc');fig,axes=plt.subplots(2,3,figsize=(15,8))
metrics={}
for col,(name,x,y) in enumerate([('中心',8500,6500),('左上',1500,1500),('右下',16000,12000)]):
 before=a[y:y+800,x:x+1000].astype(np.float32)/257;after=b[y:y+800,x:x+1000].astype(np.float32)/257
 Image.fromarray(b[y:y+1200,x:x+1600]).save(out/(name+'_原尺寸局部16位.tif'),compression='tiff_lzw',dpi=(2540,2540))
 axes[0,col].imshow(after,cmap='gray',vmin=20,vmax=200);axes[0,col].set_title(name+'：处理后原尺寸区域',fontproperties=font)
 gy,gx=np.gradient(after);normal=np.stack([-gx*.16,-gy*.16,np.ones_like(gx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 light=np.array([-.45,-.55,.7]);light/=np.linalg.norm(light)
 axes[1,col].imshow(.2+.8*np.clip(normal@light,0,1),cmap='gray',vmin=0,vmax=1);axes[1,col].set_title('斜光诊断（非实际雕刻深度）',fontproperties=font)
 pre=before-gaussian_filter(before,5);post=after-gaussian_filter(after,5)
 metrics[name]={'fine_detail_rms_before':float(np.sqrt(np.mean(pre**2))),'fine_detail_rms_after':float(np.sqrt(np.mean(post**2)))}
for ax in axes.flat:ax.axis('off')
fig.tight_layout();fig.savefig(out/'三处局部与斜光检查.png',dpi=130);plt.close(fig)
check=Image.open(dest);assert check.size==(19000,15000) and check.mode=='I;16'
assert np.array_equal(np.array(check.crop((8500,6500,8600,6600))),b[6500:6600,8500:8600])
report={'source':path,'size':check.size,'mode':check.mode,'cloned_components':len(changes),'brightness_threshold_8bit':220,'remaining_pixels_ge220':int(np.count_nonzero(b>=220*257)),'smoothing_sigma_px':sigma,'metrics':metrics,'seconds':time.perf_counter()-t,'status':'visual_review_required_not_seamless'}
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'处理说明.txt').write_text('去切割线底图 v3\n先对上版中灰度 >=220 的亮点进行邻域取样仿制，再对全图以 12 像素高斯尺度清除残线频段。邻域仿制是脚本复制同图源块，不是调用 PS 图章笔刷。取样记录和修补位置随附。\n19000×15000，16 位灰度，2540 DPI。没有重新拉伸灰度、没有锐化、未做无缝。\n本版优先消除密集切割线；同尺度的细小底纹也会被平滑，不宣称完全无损恢复。斜光预览不是 ArtForm 实际验证，请按相同尺寸和高度设置复核。\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)

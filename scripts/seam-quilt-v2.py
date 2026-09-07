from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import json
Image.MAX_IMAGE_PIXELS=1300000000
out=Path('output/seam-quilt-v2');out.mkdir(parents=True,exist_ok=True)
src=np.array(Image.open('output/clean-base-v3/02_去切割线_仅底部花纹_全尺寸16位.tif'))
H,W=src.shape
b=np.roll(src,(H//2,W//2),(0,1)).copy()
def path(cost):
 cost=gaussian_filter(cost,1);h,w=cost.shape
 start=int(np.argmin(cost[:8].mean(0)+cost[-8:].mean(0)))
 d=np.full(w,np.inf);d[start]=cost[0,start];back=np.empty((h,w),np.int8)
 for y in range(1,h):
  prev=np.stack([np.r_[np.inf,d[:-1]],d,np.r_[d[1:],np.inf]])
  ix=prev.argmin(0);d=prev[ix,np.arange(w)]+cost[y];back[y]=ix-1
 p=np.empty(h,np.int32);p[-1]=start
 for y in range(h-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p
def stitch(v,donor,l,r,overlap):
 # Per-row shortest cut through low mismatch; only a narrow smooth blend.
 target=v[:,l:r];step=10
 diff=(target[::step,::step].astype(np.float32)-donor[::step,::step].astype(np.float32))/257
 k=overlap//step
 left=path(diff[:,:k]**2);right=path(diff[:,-k:]**2)+(r-l)//step-k
 ys=np.arange(v.shape[0]);sample=np.arange(len(left))*step
 lp=np.interp(ys,sample,left*step);rp=np.interp(ys,sample,right*step)
 for y in range(0,v.shape[0],256):
  yy=slice(y,min(y+256,v.shape[0]));x=np.arange(r-l)[None,:]
  alpha=np.clip((x-lp[yy,None]+300)/600,0,1)*np.clip((rp[yy,None]-x+300)/600,0,1)
  alpha=alpha*alpha*(3-2*alpha)
  v[yy,l:r]=np.rint(target[yy].astype(np.float32)*(1-alpha)+donor[yy].astype(np.float32)*alpha).astype(np.uint16)
 return {'left_range':[int(lp.min()),int(lp.max())],'right_range':[int(rp.min()),int(rp.max())]}
# Keep the donor's vertical ordering compatible with the periodic outer border.
donor_source=np.roll(src,H//2,axis=0)
l=W//2-2600;r=W//2+2600;overlap=1200
scores=[]
for x in range(800,W-(r-l)-800,500):
 d=donor_source[::30,x:x+r-l:30].astype(np.float32);t=b[::30,l:r:30].astype(np.float32)
 scores.append((float(np.mean(np.min((d[:,:40]-t[:,:40])**2,axis=1))+np.mean(np.min((d[:,-40:]-t[:,-40:])**2,axis=1))),x))
dx=min(scores)[1]
vinfo=stitch(b,donor_source[:,dx:dx+r-l],l,r,overlap);del donor_source
print('vertical joined donor x='+str(dx),flush=True)
# Horizontal bridge is taken from the already vertically repaired image.
# This keeps x-edge continuity while repairing the four-way intersection.
lo=H//2-2300;hi=H//2+2300
scores=[]
for y in range(400,H-(hi-lo)-400,400):
 if y<hi and y+hi-lo>lo:continue
 d=b[y:y+hi-lo:30,::30].astype(np.float32);t=b[lo:hi:30,::30].astype(np.float32)
 scores.append((float(np.mean(np.min((d[:35]-t[:35])**2,axis=0))+np.mean(np.min((d[-35:]-t[-35:])**2,axis=0))),y))
dy=min(scores)[1]
donor=b[dy:dy+hi-lo].copy();hinfo=stitch(b.T,donor.T,lo,hi,1000);del donor
print('horizontal joined donor y='+str(dy),flush=True)
b=np.roll(b,(-H//2,-W//2),(0,1))
Image.fromarray(b).save(out/'自然纹理接边_全尺寸16位.tif',compression='tiff_lzw',dpi=(2540,2540))
im=Image.fromarray((b//257).astype(np.uint8));im.resize((1900,1500),Image.Resampling.LANCZOS).save(out/'单幅预览.png')
sm=im.resize((950,750),Image.Resampling.LANCZOS);grid=Image.new('L',(1900,1500))
for y in (0,750):
 for x in (0,950):grid.paste(sm,(x,y))
grid.save(out/'2x2平铺审核.png')
(out/'处理记录.json').write_text(json.dumps({'method':'same-source donor strips and minimum-error irregular cuts; no reflection','donor_x':dx,'donor_y_in_shifted_image':dy,'vertical':vinfo,'horizontal':hinfo,'size':[W,H],'blend_width_px':120},indent=2),encoding='utf-8')
print('DONE',flush=True)

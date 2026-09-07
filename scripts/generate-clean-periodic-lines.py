from pathlib import Path
import numpy as np,cv2,json,time,zipfile
from scipy.ndimage import gaussian_filter,map_coordinates,spline_filter
from PIL import Image
Image.MAX_IMAGE_PIXELS=400000000
out=Path('output/generated-clean-lines');out.mkdir(parents=True,exist_ok=True)
W,H=19000,15000;NY,NX=1320,850;pitch=H/NY;slope=NX*pitch/W
# Periodic smooth modulation derived from approved base; new linework, not tracing.
img=Image.open('output/seam-quilt-v2/单幅预览.png').resize((950,750),Image.Resampling.BILINEAR)
f=gaussian_filter(np.array(img,dtype=np.float64),6,mode='wrap')
low,high=np.percentile(f,[1,99]);f=np.clip((f-low)/(high-low),0,1)
f=gaussian_filter(f,2,mode='wrap')
dy=(np.roll(f,-1,axis=0)-np.roll(f,1,axis=0))/40
A=min(260.,.48/(abs(dy).max()+1e-12))
coeff=spline_filter(f,order=3,mode='grid-wrap')
def sample(x,y):
 return map_coordinates(coeff,[np.mod(y,H)/20,np.mod(x,W)/20],order=3,mode='grid-wrap',prefilter=False)
def point(x,k,side):
 q=k*pitch+slope*x
 tone=sample(x,q);duty=.64-.36*tone
 edgeq=q+side*.5*pitch*duty
 return edgeq+A*(sample(x,edgeq)-.5)
def derivative(x,k,side):return (point(x+1,k,side)-point(x-1,k,side))/2
x=np.linspace(0,W,int(np.ceil(W/24))+1)
xr=np.arange(W,dtype=np.float64)+.5
raster=np.full((H,W),255,np.uint8);count=0;err=0.;t=time.perf_counter()
svg=out/'01_新生成连续波纹线_四边周期.svg'
with svg.open('w',encoding='utf-8') as h:
 h.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="190mm" height="150mm" viewBox="0 0 {W} {H}"><title>新生成可变宽度黑白周期波纹线</title><defs><clipPath id="tile"><rect width="{W}" height="{H}"/></clipPath></defs><rect width="{W}" height="{H}" fill="#fff"/><g fill="#000" clip-path="url(#tile)">\n')
 for k in range(-NX-30,NY+30):
  top=point(x,k,-1);bottom=point(x,k,1)
  if top.min()>H or bottom.max()<0:continue
  dt=derivative(x,k,-1);db=derivative(x,k,1)
  def curve(xx,yy,dd):
   seg=[]
   for i in range(len(xx)-1):
    delta=(xx[i+1]-xx[i])/3
    seg.append(f'C{xx[i]+delta:.3f},{yy[i]+delta*dd[i]:.3f} {xx[i+1]-delta:.3f},{yy[i+1]-delta*dd[i+1]:.3f} {xx[i+1]:.3f},{yy[i+1]:.3f}')
   return ''.join(seg)
  h.write(f'<path d="M{x[0]:.3f},{top[0]:.3f}'+curve(x,top,dt)+f'L{x[-1]:.3f},{bottom[-1]:.3f}'+curve(x[::-1],bottom[::-1],db[::-1])+'Z"/>\n')
  upper=point(xr,k,-1);lower=point(xr,k,1)
  first=np.ceil(upper-.5).astype(np.int32);last=np.ceil(lower-.5).astype(np.int32)
  for offset in range(int((last-first).max())):
   rows=first+offset;valid=(rows<last)&(rows>=0)&(rows<H)
   raster[rows[valid],np.flatnonzero(valid)]=0
  if count%100==0:
   mid=(x[:-1]+x[1:])/2;delta=np.diff(x)
   herm=.5*(top[:-1]+top[1:])+delta*(dt[:-1]-dt[1:])/8
   err=max(err,float(abs(herm-point(mid,k,-1)).max()))
  count+=1
  if count%400==0:print('generated ribbons',count,flush=True)
 h.write('</g></svg>')
# Save strictly binary full-size image. SVG is the geometry master.
Image.fromarray(raster).convert('1',dither=Image.Dither.NONE).save(out/'02_纯黑白线层_全尺寸.tif',compression='group4',dpi=(2540,2540))
Image.fromarray(raster).save(out/'02_纯黑白线层_全尺寸.png',dpi=(2540,2540))
Image.fromarray(raster).resize((1900,1500),Image.Resampling.LANCZOS).save(out/'03_整体显示预览.png')
for name,xx,yy in [('中心',8500,6500),('左上',1500,1500),('右下',16000,12000)]:
 Image.fromarray(raster[yy:yy+1000,xx:xx+1400]).save(out/(name+'_线条放大审核.png'))
xs=np.arange(-700,700)%W;ys=np.arange(-500,500)%H
Image.fromarray(raster[np.ix_(ys,xs)]).save(out/'四角交汇_原尺寸.png')
preview=Image.open(out/'03_整体显示预览.png').resize((950,750),Image.Resampling.LANCZOS);grid=Image.new('L',(2850,2250))
for yy in range(3):
 for xx in range(3):grid.paste(preview,(xx*950,yy*750))
grid.save(out/'04_3x3平铺显示预览.png')
with zipfile.ZipFile(out/'矢量线层SVG.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:z.write(svg,svg.name)
testx=np.linspace(0,W,250);testy=np.linspace(0,H,200);xx,yy=np.meshgrid(testx,testy)
fd=(sample(xx,yy+1)-sample(xx,yy-1))/2
periodic_lr=max(abs(point(np.array([W]),k,s)[0]-point(np.array([0]),k+NX,s)[0]) for k in [0,100,300] for s in [-1,1])
periodic_tb=max(abs(point(testx,k+NY,s)-point(testx,k,s)-H).max() for k in [-200,0,100] for s in [-1,1])
report={'mode':'new_generated_not_scanned_extraction','size_px':[W,H],'physical_mm':[190,150],'dpi':2540,'vertical_periods':NY,'horizontal_phase_shift_periods':NX,'base_angle_degrees':float(np.degrees(np.arctan(slope))),'base_pitch_y_px':pitch,'warp_amplitude_px':A,'sampled_mapping_derivative_min':float((1+A*fd).min()),'duty_range':[.28,.64],'cubic_midpoint_error_px':err,'left_right_vector_error_px':float(periodic_lr),'top_bottom_vector_error_px':float(periodic_tb),'ribbons':count,'raster_unique_values':np.unique(raster).tolist(),'seconds':time.perf_counter()-t,'status':'geometry_checks_complete_visual_review_pending'}
(out/'生成与检查记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(report,flush=True)

from pathlib import Path
import xml.etree.ElementTree as ET,re,json
import numpy as np,fitz
from PIL import Image
Image.MAX_IMAGE_PIXELS=400000000
root=Path('output/generated-clean-lines');r=json.loads((root/'生成与检查记录.json').read_text(encoding='utf-8'))
x,y,w,h=8500,6500,600,400;slope=850*(15000/1320)/19000
pieces=[]
for _,el in ET.iterparse(root/'01_新生成连续波纹线_四边周期.svg',events=('end',)):
 if el.tag.endswith('path'):
  d=el.attrib['d'];start=float(re.match(r'M[^,]+,([-0-9.]+)',d).group(1))
  if start+slope*(x+w)+500>=y and start+slope*x-500<=y+h:pieces.append(ET.tostring(el,encoding='unicode'))
 el.clear()
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/><g fill="black">'+''.join(pieces)+'</g></svg>'
doc=fitz.open(stream=svg.encode(),filetype='svg');p=doc[0].get_pixmap(alpha=False);a=np.frombuffer(p.samples,np.uint8).reshape(h,w,p.n)[:,:,0]
b=np.array(Image.open(root/'02_纯黑白线层_全尺寸.png').crop((x,y,x+w,y+h)))
r['exported_svg_roi_binary_agreement']=float(np.mean((a<128)==(b<128)))
r['exported_svg_roi']=[x,y,w,h]
Image.fromarray(a).save(root/'SVG实际回读_局部.png');(root/'生成与检查记录.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(r['exported_svg_roi_binary_agreement'])

from pathlib import Path
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS=400000000
out=Path('output/blender-review');out.mkdir(parents=True,exist_ok=True)
a=np.array(Image.open('output/seam-quilt-v2/自然纹理接边_全尺寸16位.tif'))
Image.fromarray(a).resize((3800,3000),Image.Resampling.BILINEAR).save(out/'overview_height_16bit.png')
# Original-resolution crop straddles the four-tile junction. No resizing.
ys=np.arange(-800,800)%15000;xs=np.arange(-1000,1000)%19000
c=a[np.ix_(ys,xs)]
Image.fromarray(c).save(out/'junction_height_16bit.png')
np.save(out/'junction_height.npy',c.astype(np.float32)/65535)
print('Prepared overview and native 2000x1600 junction crop')

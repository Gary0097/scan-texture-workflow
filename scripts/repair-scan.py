"""Apply this scan's recorded clone rectangles; never reuse on a different scan."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=400000000
src=np.array(Image.open('input/原图.tif'))
if src.shape != (15000,19000) or src.dtype != np.uint8:
    raise ValueError('Expected this project original 19000x15000 8-bit grayscale scan')
out=src.copy()
for x0,y0,x1,y1,dx,dy in json.loads(Path('scripts/stamp-patches.json').read_text(encoding='utf-8-sig')):
    donor=src[y0+dy:y1+dy,x0+dx:x1+dx]
    if donor.shape != out[y0:y1,x0:x1].shape: raise ValueError('Invalid clone coordinates')
    out[y0:y1,x0:x1]=donor
folder=Path('output/texture-confirmation');folder.mkdir(parents=True,exist_ok=True)
Image.fromarray(out).save(folder/'01_扫描白点修复.tif',compression='tiff_lzw',dpi=(2540,2540))

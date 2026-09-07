import bpy, math, json
from pathlib import Path
from mathutils import Vector
import numpy as np
root=Path(r'output/blender-review')
bpy.ops.wm.read_factory_settings(use_empty=True)
def setup(scene,scale):
 scene.render.engine='CYCLES';scene.cycles.samples=16
 scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new(scene.name+' World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.16,.16,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
 scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'
 for name,loc,power in [('侧光_左前',(-scale,-scale*.65,scale*.3),2.5),('补光_右后',(scale,scale*.5,scale),.6)]:
  data=bpy.data.lights.new(name,'SUN');data.energy=power;data.angle=.12;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
 camdata=bpy.data.cameras.new('审核相机');cam=bpy.data.objects.new('审核相机',camdata);scene.collection.objects.link(cam);cam.location=(0,-scale*.82,scale*1.15);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=scale;camdata.clip_start=.00001;camdata.clip_end=100;scene.camera=cam
def mat(name,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(.42,.42,.42,1)
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.42,.42,.42,1);p.inputs['Roughness'].default_value=.78
 if image:
  t=n.new('ShaderNodeTexImage');t.image=image;t.extension='REPEAT';t.interpolation='Linear';t.location=(-600,20)
  tex=n.new('ShaderNodeTexCoord');tex.location=(-1000,20);mult=n.new('ShaderNodeVectorMath');mult.operation='SCALE';mult.inputs[3].default_value=3;mult.location=(-800,20)
  m.node_tree.links.new(tex.outputs['UV'],mult.inputs[0]);m.node_tree.links.new(mult.outputs[0],t.inputs['Vector'])
  bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0005;bump.inputs['Strength'].default_value=1;bump.location=(-280,20);bump.label='预览高度 0.5 mm，非加工深度'
  m.node_tree.links.new(t.outputs['Color'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
def meshgrid(scene,name,nx,ny,w,h):
 xx,yy=np.meshgrid(np.linspace(-w/2,w/2,nx),np.linspace(-h/2,h/2,ny));verts=np.stack([xx.ravel(),yy.ravel(),np.zeros(nx*ny)],1)
 row,col=np.meshgrid(np.arange(ny-1),np.arange(nx-1),indexing='ij');i=(row*nx+col).ravel();faces=np.stack([i,i+1,i+nx+1,i+nx],1)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts.tolist(),[],faces.tolist());mesh.update();ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob)
 uv=mesh.uv_layers.new();co=np.stack([(verts[:,0]+w/2)/w,(verts[:,1]+h/2)/h],1);uv.data.foreach_set('uv',co[faces.ravel()].astype(np.float32).ravel())
 for p in mesh.polygons:p.use_smooth=True
 return ob
overview=bpy.context.scene;overview.name='01_3x3整体审核_凹凸预览';setup(overview,.68)
im=bpy.data.images.load(str(root/'overview_height_16bit.png'));im.colorspace_settings.name='Non-Color';im.pack()
ob=meshgrid(overview,'3x3平铺_仅凹凸显示',2,2,.57,.45);ob.data.materials.append(mat('灰色哑光_3x3',im))
detail=bpy.data.scenes.new('02_四角接缝_真实位移');setup(detail,.025)
di=bpy.data.images.load(str(root/'junction_height_16bit.png'));di.colorspace_settings.name='Non-Color';di.pack()
obj=meshgrid(detail,'接缝局部_原图每4像素一个网格',501,401,.02,.016);obj.data.materials.append(mat('灰色哑光_真实起伏'))
texture=bpy.data.textures.new('16位接缝高度_原尺寸','IMAGE');texture.image=di;texture.extension='EXTEND'
mod=obj.modifiers.new('凸起高度_当前0.5毫米_可调','DISPLACE');mod.texture=texture;mod.texture_coords='UV';mod.uv_layer=obj.data.uv_layers[0].name;mod.direction='Z';mod.strength=.0005;mod.mid_level=0
obj['说明']='白色凸起。修改置换强度控制高度；0.0005 米=0.5毫米，仅预览。网格间距0.04毫米；细节精验需加密。'
for scene in (overview,detail):scene.render.image_settings.file_format='PNG'
txt=bpy.data.texts.new('先读我_中文操作说明');txt.write('顶部场景列表切换：\n01：3×3 总览，查看重复、横竖接缝。采用凹凸显示，不是真实几何。\n02：四角交汇处，真实置换，白色凸起；网格每4原图像素采样。\n鼠标中键拖动旋转，滚轮缩放；数字小键盘0回到相机。\n右上场景下拉切换 01/02。按Z再按R显示灯光效果。\n当前0.5毫米仅预览高度，不是加工深度。\n整体使用3800×3000的16位缩小贴图；局部为原尺寸2000×1600，未缩小。\n原始19000×15000 TIFF未改动。\n')
bpy.context.window.scene=overview
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_lights=True;area.spaces.active.shading.use_scene_world=True
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_start=.00001
bpy.ops.wm.save_as_mainfile(filepath=str(root/'木纹接边审核.blend'))
for scene,name in [(overview,'01_整体灯光审核.png'),(detail,'02_接缝真实起伏审核.png')]:
 scene.render.filepath=str(root/name);bpy.ops.render.render(write_still=True,scene=scene.name)
print('REVIEW_PROJECT_COMPLETE',flush=True)

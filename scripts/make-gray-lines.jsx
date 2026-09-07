(function(){
var root='__PROJECT_ROOT__/output/composite-review/';
var old=app.displayDialogs;app.displayDialogs=DialogModes.NO;
try{
// Rebuild from approved complete base and line files, not an edited document.
var base=app.open(new File(root+'../seam-quilt-v2/自然纹理接边_全尺寸16位.tif'));
var d=base.duplicate('灰色线层_组合审核',true);
var ls=app.open(new File(root+'../generated-clean-lines/02_纯黑白线层_全尺寸.png'));
var lw=ls.duplicate('灰线临时',true);lw.bitsPerChannel=BitsPerChannelType.SIXTEEN;lw.activeLayer.duplicate(d,ElementPlacement.PLACEATBEGINNING);lw.close(SaveOptions.DONOTSAVECHANGES);app.activeDocument=d;d.layers[0].duplicate();
d.selection.deselect();var line=d.layers[0];d.activeLayer=line;
line.adjustLevels(0,255,1,128,255);line.name='02_灰色线层_灰值128_正片叠底';line.opacity=100;line.blendMode=BlendMode.MULTIPLY;
d.layers[1].visible=false;d.layers[1].name='备份_纯黑白线层_隐藏';
var f=new File(root+'08_灰色线层_全尺寸分层_v3.tif');if(f.exists)throw new Error('Output exists');
var opt=new TiffSaveOptions();opt.layers=true;opt.imageCompression=TIFFEncoding.TIFFZIP;opt.layerCompression=LayerCompression.ZIP;opt.embedColorProfile=true;
d.saveAs(f,opt,false,Extension.LOWERCASE);
var crop=d.duplicate('灰线局部',true);crop.crop([UnitValue(8500,'px'),UnitValue(6500,'px'),UnitValue(9900,'px'),UnitValue(7500,'px')]);crop.bitsPerChannel=BitsPerChannelType.EIGHT;crop.saveAs(new File(root+'09_灰线原尺寸局部.png'),new PNGSaveOptions(),true);crop.close(SaveOptions.DONOTSAVECHANGES);
var sm=d.duplicate('灰线整体',true);sm.resizeImage(UnitValue(1140,'px'),UnitValue(900,'px'),null,ResampleMethod.BICUBIC);sm.bitsPerChannel=BitsPerChannelType.EIGHT;var jpg=new JPEGSaveOptions();jpg.quality=10;sm.saveAs(new File(root+'10_灰线整体预览.jpg'),jpg,true);sm.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument=d;return 'GRAY_OK '+d.width.as('px')+'x'+d.height.as('px')+' layers='+d.layers.length+' bits='+d.bitsPerChannel+' bytes='+f.length;
}finally{app.displayDialogs=old;}
})();

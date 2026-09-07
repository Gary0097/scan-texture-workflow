#target photoshop
(function(){
var basePath='__PROJECT_ROOT__/output/';var out=basePath+'composite-review/';
var old=app.displayDialogs,u=app.preferences.rulerUnits;app.displayDialogs=DialogModes.NO;app.preferences.rulerUnits=Units.PIXELS;
function log(s){var f=new File(out+'progress.txt');f.encoding='UTF8';f.open('a');f.writeln(s);f.close();}
function png(d,n){d.saveAs(new File(out+n+'.png'),new PNGSaveOptions(),true,Extension.LOWERCASE);}
try{
var source=app.open(new File(basePath+'seam-quilt-v2/自然纹理接边_全尺寸16位.tif'));
var d=source.duplicate('底图与新线层_组合审核',true);d.activeLayer.name='01_已确认接边底图';
var lineSource=app.open(new File(basePath+'generated-clean-lines/02_纯黑白线层_全尺寸.png'));
var lineWork=lineSource.duplicate('线层传入临时副本',true);lineWork.bitsPerChannel=BitsPerChannelType.SIXTEEN;
var line=lineWork.activeLayer.duplicate(d,ElementPlacement.PLACEATBEGINNING);lineWork.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument=d;line.name='02_独立黑白线层_正片叠底预览';line.blendMode=BlendMode.MULTIPLY;line.opacity=100;line.fillOpacity=100;
var psd=new PhotoshopSaveOptions();psd.layers=true;d.saveAs(new File(out+'01_底图与线层_全尺寸分层.psd'),psd,false,Extension.LOWERCASE);log('FULL_LAYERED_SAVED');
var detail=d.duplicate('组合原尺寸局部',true);detail.crop([UnitValue(8500,'px'),UnitValue(6500,'px'),UnitValue(9900,'px'),UnitValue(7500,'px')]);detail.bitsPerChannel=BitsPerChannelType.EIGHT;png(detail,'02_组合原尺寸局部');detail.close(SaveOptions.DONOTSAVECHANGES);
var small=d.duplicate('组合整体预览',true);small.resizeImage(UnitValue(1900,'px'),UnitValue(1500,'px'),null,ResampleMethod.BICUBIC);small.bitsPerChannel=BitsPerChannelType.EIGHT;png(small,'03_组合整体预览');
var grid=small.duplicate('组合审核_3x3平铺',true);var tile=grid.activeLayer;tile.isBackgroundLayer=false;tile.name='第1行_第1列';grid.resizeCanvas(UnitValue(5700,'px'),UnitValue(4500,'px'),AnchorPosition.TOPLEFT);
for(var y=0;y<3;y++){for(var x=0;x<3;x++){if(x===0&&y===0)continue;var l=tile.duplicate();l.translate(x*1900,y*1500);l.name='第'+(y+1)+'行_第'+(x+1)+'列';}}
grid.saveAs(new File(out+'04_组合3x3平铺审核.psd'),psd,false,Extension.LOWERCASE);png(grid,'04_组合3x3平铺审核');
var view=grid.duplicate('组合平铺显示预览',true);view.resizeImage(UnitValue(1900,'px'),UnitValue(1500,'px'),null,ResampleMethod.BICUBIC);png(view,'05_组合3x3显示预览');view.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument=d;log('COMPLETE '+d.width.as('px')+'x'+d.height.as('px')+' layers='+d.layers.length+'; grid='+grid.layers.length);
return 'COMPOSITE_OK '+d.width.as('px')+'x'+d.height.as('px')+' layers='+d.layers.length;
}catch(e){log('ERROR '+e.message+' line '+e.line);throw e;}finally{app.displayDialogs=old;app.preferences.rulerUnits=u;}
})();

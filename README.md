# 扫描纹理分离与周期线层：同事交接版

本项目是针对 **19000×15000、2540 DPI、190×150 mm** 样本的实验工作流，不是通用一键修图产品。处理采用 Python 数值算法和 Photoshop 脚本，不调用 AI 生图服务。请先阅读 `docs/算法与验收.md`。

## 最快上手

1. 解压项目包到有充足空间的目录。Windows 安装 Python（本机依赖版本见 requirements.txt），运行 `python -m pip install -r requirements.txt`。
2. 所有命令均在项目根目录执行。
3. 只生成新线层：运行 `python scripts/generate-clean-periodic-lines.py`，然后 `python scripts/check-generated-svg.py`。已附小尺寸底纹调制图，无须原扫描即可运行这一步。输出在 output/generated-clean-lines。
4. 使用交接成品：将独立的“成品素材包.zip”解压到项目根目录，保留 output 目录结构。Photoshop 可直接打开其中分层 TIFF；不必重算。
5. 重做灰线：启动 Photoshop 后执行 `powershell.exe -NoProfile -File run-photoshop.ps1 -Name make-gray-lines.jsx`。脚本从完整底图和完整线层重建，保留隐藏黑白备份。输出文件已存在时会停止，请先改输出版本名称。

## 从原扫描重算

将本次原始扫描放在 input/原图.tif，按顺序执行：

```text
python scripts/repair-scan.py
python scripts/full-frequency-review.py
python scripts/remove-cut-lines-v3.py
python scripts/seam-quilt-v2.py
python scripts/generate-clean-periodic-lines.py
python scripts/check-generated-svg.py
```

前置修补使用本样本既有取样坐标，**不能直接应用于另一张扫描**。底图完整链路原本分阶段运行；打包后做了语法与资源检查，未重新跑全尺寸链路。不要将其视为已验证的一键生产程序。

## Photoshop / Blender

- 黑白线合成：`powershell.exe -NoProfile -File run-photoshop.ps1 -Name ps-composite-review.jsx`。生成分层 PSD、局部和 3×3 审核图。
- 灰线版本：灰值 128/255 的线层正片叠底，合成像素随底图变化。是视觉变体，尚待客户确认；独立黑白线文件不改。
- Blender：先 `python scripts/prepare-blender-height.py`，再用自己的 Blender 程序运行 `blender --background --python scripts/build-blender-review.py`。必须后台运行；脚本清空 Blender 当前场景。
- Blender 第一场景是凹凸显示；第二场景为接缝局部真实位移。0.5 mm 仅作审核，不能当作客户最终雕刻深度。

## 文件和交接状态

- 源码包：算法、PS 调用入口、说明、参数记录、小预览。
- 成品素材包：已确认接边底图、完整二值线层、SVG、黑白与灰线分层 TIFF。
- 原扫描、客户 PDF、聊天截图不放入仓库；需从原资料另行取得。
- 历史失败版未混入默认流程：旧镜像接边有竖条，扫描轮廓描摹有杂点与接边问题，已放弃。
- 使用和交付权限依原项目授权；本包未擅自赋予客户素材开源许可。

GitHub 私有仓库：https://github.com/Gary0097/scan-texture-workflow 。仓库只放源码及小预览；大图使用独立素材包交接。同事需仓库拥有者授予访问权限，或直接使用项目 ZIP。

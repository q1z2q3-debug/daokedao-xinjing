---
name: sancai-wuyun-3d
description: 生成或修改「三才五蕴」的可旋转三维模型页：五蕴杯器（色为杯底、受想行识四瓣竖壁）与五蕴管壁（五蕴五瓣纵壁、横放无底、壁厚可调），产出零外链、离线可开的单文件 HTML（three.js 内联）。用于用户要三维杯／管模型、可拖动旋转、调管壁厚看「由薄到厚至实心」、把五蕴讲成一只器，或要在这两只器上换配色、换取景、加预设档位时。
---

# 五蕴三维模型

一句话：**杯以容，管以通**。先读 `references/geometry-3d.md` 拿几何与渲染契约，不要凭印象改角度和配位。

## 构建

模板与库都在 `assets/templates/`、`vendor/`。改完模板一律走构建脚本，不要手拼 three.js：

```bash
python3 scripts/build.py --list
python3 scripts/build.py cup  --out 五蕴杯器-3D.html
python3 scripts/build.py pipe --out 五蕴管壁-壁厚可调.html
```

- 模板里必须有 `/*__THREE__*/` 与 `/*__ORBIT__*/` 两处占位，脚本会换成 `vendor/` 的 three r128 与 OrbitControls 源码。
- 直接改产出的 HTML 无效：下次构建会覆盖。
- `vendor/` 不在时可以重新取：`https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js` 与 `.../examples/js/controls/OrbitControls.js`。

## 页面契约

- 单文件自包含：CSS、JS、三维库、CanvasTexture 全内联；除 XML 命名空间外零外链，断网可开。
- 模型表面不写字。五蕴用颜色辨：五字与彩色圆点只出现在右侧图例。
- 杯与管的配色各自成套，不混用（色值见 references）。
- 导航行 `<div class="navline">` 是站点导航，页面搬去别处时改这一行，不要把相对链接留在成品里。
- 壁厚滑杆是**重建几何**（改内半径），不是缩放；实心态把内半径夹到 `0.0016`。

## 自检

`html` skill 的 `scripts/shot.py <html>` 跑桌面＋移动各一屏，看 `consoleErrors` 是否为空，再**实际看截图**确认主体可见、五色分得开、移动端不横向溢出。黑屏不报错也算失败。另查 `window.__sceneReady === true`。

## 常改点

- 换配色：改模板里 `srgb(hex)` 的色值，必须保留 `convertSRGBToLinear()`，否则洗色。
- 换取景：改 `fitView()` 的 `FIT_R` 与 `DIR`，不要写死相机距离。
- 加档位：预设按钮与滑杆共用同一个 `setWall(t)`，新增档位只加按钮与数值。
- 缺瓣漏水图：三维不做缺瓣，缺瓣仍用 `sancai-wuyun-diagrams` 的 SVG 版；两者几何必须一致（四瓣 90°／五瓣 72°、通体）。

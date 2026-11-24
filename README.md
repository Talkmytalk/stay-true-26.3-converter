# Stay True → Minecraft Java 26.3 转换工具

非官方兼容转换工具，原资源包作者为 **HaiMcFly / haimcyfly**。本项目与原作者、Mojang 无关联。

仓库只提供转换代码与贴图坐标映射，不包含 Stay True 或 Minecraft 的图片，也不提供转换后资源包的下载。请从原作者处取得原包，在本地生成兼容包。

## 使用方法

需要 Python 3.9+、Pillow，以及以下两个本地文件：

1. 作者发布的 [Stay True 1.21.5.zip（CurseForge 文件 6534716）](https://www.curseforge.com/minecraft/texture-packs/stay-true/files/6534716)。不要解压或改动，工具会检查文件校验值。
2. 你已安装的 **Minecraft Java 26.3 客户端 JAR**。例如 `.minecraft/versions/26.3/26.3.jar`；部分启动器会使用实例名称命名客户端 JAR。不能使用 Fabric Loader、安装器或服务端 JAR 代替。

下载本仓库源码并解压，在该目录执行：

```sh
python -m pip install -r requirements.txt
python convert.py --input "Stay True 1.21.5.zip" --minecraft-jar "26.3.jar" --output "Stay True 26.3 - Local Port.zip"
```

将生成的 ZIP 放入游戏实例的 `resourcepacks` 文件夹，在游戏中启用，无需解压。旁边的 `.report.json` 记录转换内容和检查结果。Fabric 下连接纹理需要另行安装适配 26.3 的 [Continuity](https://modrinth.com/mod/continuity)。

## 兼容范围

- 专门针对 Java **26.3 / 资源包格式 97.1**，不声称支持 26.4 或其他版本。
- 复用已有贴图，调整锁链、柱子、盔甲架、太阳、鱿鱼的路径。
- 按新 UV 布局拼接告示牌和悬挂告示牌，更新植物模型光照字段与树叶物品模型。
- 修复原包中的部分过期连接纹理规则、箱子父模型和切制砂岩状态。
- 保留云杉树叶物品的原版绿色染色；白桦叶使用原包自身颜色。
- 不绘制新增方块或幼年动物变体的贴图；没有覆盖的部分沿用原版。
- 旧 GUI 图集及可选替代贴图保持原有状态；无效路径的可选文件收纳至 ZIP 的 `optional_original_assets` 中。
- OptiFine 专属的自定义颜色功能并非全部由 Continuity 提供，本工具不承诺完整复现这些功能。

## 验证

本地生成包通过了 26.3 + Fabric Loader 0.20.1 + Continuity 3.0.1 + Sodium 0.9.2 的资源加载和模型烘焙检查。此检查不等于已逐一目视检查所有方块。

可在本地核对云杉染色及白桦颜色回归检查：

```sh
python verify.py --pack "Stay True 26.3 - Local Port.zip" --minecraft-jar "26.3.jar"
```

## 作者与许可

原作：[Stay True by haimcyfly](https://www.curseforge.com/minecraft/texture-packs/stay-true)。原作许可为 [All Rights Reserved](https://www.curseforge.com/minecraft/texture-packs/stay-true/license)。本工具的 MIT 许可仅适用于本仓库新增的转换代码和坐标数据，**不授予原作或 Minecraft 资源的转载权限，也不适用于生成的资源包**。

## English

Unofficial local converter for Stay True 1.21.5 → Minecraft Java 26.3. Download the original pack from its author, supply your own installed 26.3 client JAR, install Pillow, and run the command above. This repository ships no artwork or converted resource-pack ZIP. Existing art is reused; new content falls back to vanilla. The spruce inventory tint fix is included. Upstream artwork remains All Rights Reserved; MIT covers only this converter's original code/data.

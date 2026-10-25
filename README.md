# lakeview-cabin-2 汉化项目

## 游戏信息
- 原名：Lakeview Cabin 2
- 中文名：湖景小屋2（暂译）
- 开发商：Roope Tamminen（HypnoGames，个人开发者，兼发行商）
- 发行平台：Steam（AppID 1291790；Windows / macOS）
- 引擎：Unity 2019.4.34f1（Mono 后端，含 PlayMaker、DOTween、Cinemachine）
- 本机版本：Steam Windows x64，BuildID 13433015（以现有安装文件哈希为准）
- 原语言：英语（界面/字幕/音频均仅英语）

## 游戏简介
《Lakeview Cabin 2》是《Lakeview Cabin Collection》的续作，一款像素风格的动作生存恐怖游戏。玩家同时操控四名伙伴，利用场景中各种物品设陷阱、做规划，对抗恐怖敌人，主打涌现式玩法。游戏共四个章节：夏日别墅遇袭求生、恐怖片影迷见面会捉凶手、电视剧制片厂多时间线探索、末日废土阻止邪恶。包含初代 Flash 游戏重制版与各章附加模式，支持单人或 2 人本地/远程同乐合作。Steam 评价"压倒性好评"。

来源：[Steam 商店页面](https://store.steampowered.com/app/1291790/Lakeview_Cabin_2/)

> 内容提示：开发商声明本作包含涉及像素角色的暴力和性场景（R-rated），翻译时需保留原文的成人恐怖基调。

## 汉化目标
- 范围：游戏内常规文本 + 图片文字（菜单、标题、便条、标牌等贴图）
- 目标语言：简体中文
- 翻译路线：API（程序请求）
- 图片文字翻译：启用（用户明确选择）

## 图片文字流程
- 选择记录：`localization_project.json`；未决定时可先提取常规文本，不能默认启用图片步骤。
- 启用时：常规解包 → `game-image-extract` → `game-translate`（常规/图片数据集独立）→ `game-image-repack` → 引擎回填。

## 技术栈
| 环节 | 工具 | 版本 |
|------|------|------|
| 提取 | UnityPy + TypeTreeGenerator（修正节点对齐/数组）；本地图片三级流程 | UnityPy 1.25.4 / Unity 2019.4.34f1 |
| 翻译 | 共用API流程；DeepSeek（本机优先级接口） | translation_workflow.py 当前工作区版 |
| 回填 | UnityPy序列化资源替换；Noto Sans SC Regular中文字体 | UnityPy 1.25.4 / 字重400静态实例 |

## 文本提取
- 引擎：Unity 2019.4.34f1，Mono。只读扫描全部 level / sharedassets / resources 序列化资源。
- 工具/命令：`python Analysis/extract_assets.py`；`python Analysis/extract_text_actions.py`。
- 修正旧扫描：TypeTreeGenerator 的 m_Enabled 需要四字节对齐；与基本 string 类型同名的托管数组需恢复 vector 节点。旧 fsm_text_extract.json 没有正确读取动作参数，不作为正式原文。
- 解析 93 处 UI 文本、332959 个 PlayMaker 字符串值（1193 个不同值），导出 3015 张不同贴图。5 个零尺寸运行时字体纹理没有像素数据，单独记录在 Analysis/errors.json，不作为图片素材。
- 常规原文：`lakeview-cabin-2_text.csv`，4 条片尾字幕片段。`Analysis/source_mapping.json` 保留原始字幕、定位和排除说明；回填仅替换片段，保留人员名及空行布局。
- 33 个文本赋值状态核对后，游戏动态文本仅用于分辨率数字；PlayMaker 内部事件、存档键、对象名和 debug UI 不翻译。SecretKey 的 Solve 仅由 BuildString 生成，未发现显示消费者。
- 图片导出：`ImageText/exported/`；引擎来源：`ImageText/provenance.json`；三级流程工作快照：`ImageText/work/`。已视觉查看36张校准样本，未声明任何已校准普通字体族。
- 图片抽取完成：3015张全量GPU PP-OCRv6 medium；415张有效本地Qwen复核，1张镜像字幕回复越界被拒收，当前对话Agent直接裁决。367张候选/抽查图由对话Agent查看并记录；最终22条源文、28处坐标，详见 ImageText/extraction_report.json。
- 27张保留原图清单见 ImageText/scope_exclusions.json，包括开发校准/字体图、数字/方向/品牌图形以及极小的不可可靠转写文本；其余预测排除并非已确认无字。正式图片CSV是明确确认的可翻译子集，不宣称全游戏零漏字。
- 局部Qwen故障恢复：Analysis/run_image_qwen_resilient.py 仅在本项目保留错误证据并路由当前对话复核，未修改共用工具或把错误当模型结论。

## 翻译
- 路线：API，共用 translation_workflow.py / run_api_round.py。接口按工作区 api.local.jsonc 的已启用优先级与故障切换配置执行；凭据不入库。当前首选 yjapi / deepseek-v4.1-flash，具体真实调用记录保留在本地 reports/api_runs。
- 常规文本术语：已完成全文提取、独立语义审校和冻结，r2，non_translate 保留 Denis；人物名单不进入翻译片段，不改原拼写。
- 常规文本：4条全部完成API正式翻译、草稿校验及独立六维语义审校；无遗留争议，程序最终导出通过，正式文件 lakeview-cabin-2_text_translated.csv。已安装，实机状态待用户测试。
- 占位符：由共用程序保护；字幕空行及原人员名单由回填映射保留。
- 图片文本：独立 TranslateFiles/image-text 子工程；22条全部完成术语提取、独立术语语义审校、试译校准、正式翻译及独立六维审校。r2冻结7项专名，保护标题换行、Z/X按键及作者/公司/平台名。
- 图片正式译文：lakeview-cabin-2_images_text_translated.csv；源文/译文哈希、22条对齐及全部程序门槛通过，真实审校结果另存 reports/delivery_review_evidence.json。无遗留争议，不增加额外全文复审。
- 图片合入：game-image-repack 验证生成overlay描述，再由 Analysis/render_image_patch.py 生成12张同尺寸中文贴图、28处文本，已查看全部静态预览。保留透明背景、空心字、镜像字幕、初代金色标题及所有未翻译图形。

## 回填
- 支持本机版本：Steam Windows x64，BuildID 13433015；以 Analysis/source_hashes.json 的原文件哈希为准。
- 构建：`python Analysis/scan_sprite_slices.py` → `game-image-repack build --mode overlay` → `python Analysis/render_image_patch.py` → `python Analysis/build_patch.py` → `python Analysis/verify_patch.py`。
- 安装：`python Analysis/install_patch.py install`；已于2026-10-26安装到 Game 指向的真实游戏目录，7个文件全部与项目内载荷SHA-256一致，见 Repack/install_receipt.json。
- 修改：level10；sharedassets1.assets、sharedassets4.assets、sharedassets10.assets、sharedassets18.assets、sharedassets40.assets、sharedassets41.assets。对应1处片尾字幕、12张贴图、20个文字精灵网格、1个动态TrueType字体。
- 字体：Noto Sans SC 字重400静态实例；字体缺字检查通过。片尾空行及原姓名保留。
- 精灵：保留原始m_Rect、pivot及像素单位；把受影响的英文tight mesh改为完整矩形，恢复其透明边距范围并保持源图UV位置，避免中文被原英文字母轮廓裁掉。
- 静态验证：全部图片预览已查看；12张纹理像素回读一致；20个精灵从写回后的资产实际导出，与中文PNG原切片逐像素一致；所有未修改对象的raw payload与原件相同。见 Repack/static_validation.json。
- 备份：Repack/Originals；载荷副本：Repack/Files。恢复命令：`python Analysis/install_patch.py restore`。安装/恢复均先核对全部文件版本哈希，再写入并回读核验。
- 实机验证：待用户测试。Agent未启动游戏，也未控制桌面。具体检查顺序见 TESTING.md，待测记录位于 TranslateFiles/reports/in_game_check.pending.json；未将pending伪装为通过。

## 已知问题
- 尚未实机确认字体、布局、运行与存档；当前仅静态验收及安装哈希通过。
- 27张保留清单含开发参考素材、数字/罗马数字/字形/品牌图形，以及不能可靠转写的极小装饰文字、报纸/罐体标签和手写痕迹，保持原图。全量OCR和筛选抽查不能证明全游戏没有漏字。
- 原游戏大量菜单与玩法说明使用图形图标，维持原设计。原版姓名、按键、编号和方向符号不作中文替换。


## 版本记录
- 2026-10-25 - 初始化汉化项目工作区（start-translate skill）

- 2026-10-25 - 接手旧工程，修正Unity序列化解析，提取正式字幕原文并启动图片文字流程；用户指定API、图片汉化启用、自行实机测试。

- 2026-10-26 - 完成4条字幕及22条图片原文的API正式翻译、独立审校和导出；生成12张中文贴图，修复20个精灵文字网格；7个文件静态核验并安装，等待用户首轮测试。

## 2026-10-26 首轮实机反馈核对
- 用户截图：暂停菜单为扳手/箭头图标；交互物旁边显示两个方框。对照原版贴图后，两者均与原版设计一致。
- PauseMenuIcons与GuiKeyboardButtonPrompts所在sharedassets2.assets，安装后SHA-256仍与原文件完全一致。sharedassets4.assets中补充键位贴图及两个相关精灵也逐对象与原备份一致。
- 默认键盘映射包含Z=Pick、X=Throw、↑=Use；双人键盘备用映射为C=Pick、V=Throw、W=Use。同一套方框图形被不同键位复用，因此没有把公共贴图写死成Z/X。
- 调查记录：Analysis/user_feedback_20261026/investigation.json。此次没有修改游戏文件；这两张截图不能代替全部中文字体/布局实测。

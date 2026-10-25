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
| 翻译 |  |  |
| 回填 |  |  |

## 文本提取
- 引擎：Unity 2019.4.34f1，Mono。只读扫描全部 level / sharedassets / resources 序列化资源。
- 工具/命令：`python Analysis/extract_assets.py`；`python Analysis/extract_text_actions.py`。
- 修正旧扫描：TypeTreeGenerator 的 m_Enabled 需要四字节对齐；与基本 string 类型同名的托管数组需恢复 vector 节点。旧 fsm_text_extract.json 没有正确读取动作参数，不作为正式原文。
- 解析 93 处 UI 文本、332959 个 PlayMaker 字符串值（1193 个不同值），导出 3015 张不同贴图。5 个零尺寸运行时字体纹理没有像素数据，单独记录在 Analysis/errors.json，不作为图片素材。
- 常规原文：`lakeview-cabin-2_text.csv`，4 条片尾字幕片段。`Analysis/source_mapping.json` 保留原始字幕、定位和排除说明；回填仅替换片段，保留人员名及空行布局。
- 33 个文本赋值状态核对后，游戏动态文本仅用于分辨率数字；PlayMaker 内部事件、存档键、对象名和 debug UI 不翻译。SecretKey 的 Solve 仅由 BuildString 生成，未发现显示消费者。
- 图片导出：`ImageText/exported/`；引擎来源：`ImageText/provenance.json`；三级流程工作快照：`ImageText/work/`。已视觉查看36张校准样本，未声明任何已校准普通字体族。
- 图片 OCR / 视觉确认正在进行，最终范围及未决项待补充。

## 翻译
- 路线：API，共用 translation_workflow.py / run_api_round.py。接口按工作区 api.local.jsonc 的已启用优先级与故障切换配置执行；凭据不入库。当前首选 yjapi / deepseek-v4.1-flash，具体真实调用记录保留在本地 reports/api_runs。
- 常规文本术语：已完成全文提取、独立语义审校和冻结，r2，non_translate 保留 Denis；人物名单不进入翻译片段，不改原拼写。
- 常规试译：全部4条，主Agent整体校准接受，未发现机械错误；正式翻译和独立审校待图片抽取完成后继续。
- 占位符：由共用程序保护；字幕空行及原人员名单由回填映射保留。
- 图片文本：独立 TranslateFiles/image-text 子工程，等待视觉确认后的原文，不混用常规文本状态。

## 回填
- 工具/命令：
- 步骤：
- 验证方法：

## 已知问题

## 版本记录
- 2026-10-25 - 初始化汉化项目工作区（start-translate skill）

- 2026-10-25 - 接手旧工程，修正Unity序列化解析，提取正式字幕原文并启动图片文字流程；用户指定API、图片汉化启用、自行实机测试。


## 本次数据集
仅翻译已视觉确认的图片原文；普通文本翻译状态保持独立。

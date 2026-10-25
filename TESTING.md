# 首轮游戏测试

状态：已完成静态检查并安装，7个文件哈希核验一致；实机结果由你自行确认。Agent 未启动游戏或操作桌面。

1. 从 Steam 正常启动《Lakeview Cabin 2》，检查标题中文、出品行和版权行是否清晰。
2. 检查人数选择（1～4人）、控制器选择中的玩家1/玩家2、确定和返回。切换选项，留意实心与空心文字是否正常、有没有裁掉笔画。
3. 进入初代《湖景小屋1》入口，检查方向键移动、Z/X互动提示。实际按键保持原游戏设置。
4. 进入一段普通游戏，打开暂停界面并继续，确认没有资源读取异常。大量菜单本来就是图标，并非漏译。
5. 有机会看到片尾时，检查“导演/协助制作/纪念 Denis/剧终”等字幕是否缺字或裁切。无需为了首轮测试立即打通游戏。

如发现问题，请给出：截图、所在界面/章节、窗口或全屏模式、分辨率，以及怎样进入该画面。不要覆盖项目内备份。

## 范围说明

- 常规字幕4条；图片原文22条，映射28处可翻译位置。
- 保留原有人员姓名、公司/平台名、按键、数字、罗马数字和图形标识。
- 极小装饰标签、报纸小字等无法从原像素可靠转写的内容保留原图；具体27张清单在 ImageText/scope_exclusions.json。
- 全量OCR及抽查不能证明全游戏没有漏字，实机测试继续记录发现的问题。

## 恢复原版

退出游戏后在 PowerShell 执行：

```powershell
python D:/StaticHanHua/Projects/lakeview-cabin-2/Analysis/install_patch.py restore
```

重新安装本次汉化：

```powershell
python D:/StaticHanHua/Projects/lakeview-cabin-2/Analysis/install_patch.py install
```

程序会先核对全部文件哈希，不覆盖未知版本。原文件保存在项目 Repack/Originals，汉化文件副本保存在 Repack/Files，清单在 Repack/manifest.json。

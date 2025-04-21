# tenkeiparadoxx-translation

**首先，这是一个适用于 Fanza Game 天啓パラドクス X 的翻译项目**

本仓库的文件主要用于 **Windows 平台 DMM Game Player 端**，如果你只需要安卓版，请移步[DMM-Mod](https://github.com/anosu/DMM-Mod)

### 项目组成

> 如果你只关心怎么使用，可以不看此部分

包括两个部分

-   BepInEx 插件（游戏 Mod），用于实现翻译的功能，如文本和字体的替换
-   翻译文本及后端，用于为插件提供实时获取翻译的接口

源码中`TenparaMod`为插件的 Visual Studio 项目

`app.js`为托管在 Vercel 上的后端，提供 http 接口

`translation`文件夹中存放了翻译后的文本，以类似字典的 JSON 形式

-   `names`中存放了所有的角色名称及其翻译
-   `titles`中存放了所有剧情的标题及其翻译
-   `scenes`中存放了所有剧情的剧本及其翻译，以`SceneAssetId`来进行区分和组织

### 插件功能

-   为游戏提供剧情翻译，包括主线、活动、角色以及商店购买剧情
-   去除游戏内动态添加的马赛克，这并不包括 Spine 源文件上的马赛克。也就是说马赛克也许会变小，但绝不会消失
-   不保证翻译同步更新到游戏的最新进度

### 使用方法

-   首先确保你已经安装了游戏的客户端（DMM Game Player 版）并且知道游戏的可执行文件（`tenkeiparadox_x.exe`）所在的文件夹路径

-   从本仓库的[Releases](https://github.com/anosu/tenkeiparadoxx-translation/releases)页面（← 如果你不知道在哪儿那就直接点这里）找到最新发布的版本（带有绿色的`Latest`标识），展开`Assets`选项卡（默认应该就是展开的），下载名为`TenparaMod.7z`或类似的压缩包，不要下载`Source code`，那是源码

-   将下载的压缩包解压你会得到`winhttp.dll`，`BepInEx`等文件和文件夹，将所有这些文件复制（或直接解压）到与游戏的可执行文件（`tenkeiparadox_x.exe`）相同的目录，你的`BepInEx`文件夹、`winhttp.dll`文件以及`tenkeiparadox_x.exe`应该在同一个目录下。如果你之前下载过旧版本可以先将旧版本删除或者直接全部覆盖（如果后面没问题的话）

-   正常启动游戏。注意：首次启动或者游戏更新之后，插件会有一个初始化的过程，此时你只会看到一个控制台窗口，等待其初始化完成游戏才会正常启动，此过程中 BepInEx 会从其官网下载对应游戏 Unity 版本的补丁来对游戏进行修改以支持插件的运行，如果你使用 ACGP 之类的加速器并且在此过程中看到了控制台窗口出现了红色的报错那么说明你可能无法直连其官网，请打开梯子来解决此问题。

-   当插件初始化完成并且游戏正常启动后（控制台窗口没有出现红色的报错），那么此时应该已经可以正常使用了。插件首次运行之后会在`BepInEx\config`目录下生成 BepInEx 和 mod 本身的配置文件，分别为`BepInEx.cfg`和`TenparaMod.cfg`，如果你需要修改插件的设置（如关闭翻译或者去除马赛克的功能），请修改`TenparaMod.cfg`之后重新启动游戏。如果你需要隐藏控制台窗口，请在`BepInEx.cfg`中找到`[Logging.Console]`选项，并将`Enabled`的值设置为`false`

### 剧本&脚本

见[scripts/README.md](https://github.com/anosu/tenkeiparadoxx-translation/tree/main/scripts/README.md)

### 其他

-   翻译提供者：corvette_tw
-   翻译使用 SakuraLLM v0.10
-   如果想补充或修正翻译可以为本仓库提交 PR，后续应该会上传提取剧本的脚本
-   正常使用过程中如果遇到问题可以提交 issue 或者直接在群里@我（如果可以的话）

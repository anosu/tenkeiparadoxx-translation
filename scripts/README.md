### 剧本&脚本

关于剧本的提取，这里提供了现成的脚本，如果你会 Python 那么应该不用教，如果不会建议学一下或者问 GPT

安装依赖

```shell
python -m venv .venv
pip install -r requirements.txt
```

填入 Token，设置剧本下载的目录

```python
token = "Bearer token"
download_scenes_dir = Path("scenes")
```

> 关于 Token 的获取
>
> 浏览器打开游戏页面并且 F12 打开开发者工具，切到`网络/Network`标签，点击进入游戏，然后在网络请 > 求中找到`master`、`finalize`之类的请求，`请求头/Request Headers`中找到`Authorization`， > 其值即为 Token
>
> Token 单次登录有效，重新登录后之前的 Token 立刻失效

运行脚本

```python
python main.py
```

脚本默认会从接口获取已有的剧本，同时获取用户拥有的剧本，下载缺失的剧本到指定的目录

默认的格式为 Galtransl 翻译支持的 JSON 格式，同时会提取剧本中的角色名称生成 JSON 文件

你可以直接注释掉`exists`函数或者删掉其传参，这样默认会下载用户所拥有的所有剧本

```python
# existed_scenes = set(
#     httpx.get("https://tenkeiparadox.ntr.best/existed/scenes").json()
# )
# def exists(downloader: ScriptDownloader, asset_id: str | int) -> bool:
#     return str(asset_id) in existed_scenes

# 或者
downloader.download(scene_dir=download_scenes_dir)
```

脚本同时还会在当前目录下生成一个`scenes.json`文件用来记录剧本及其路径信息做备份或调试用

### 可选

-   为已有的`titles.json`(`translation/titles/zh_Hans.json`)生成新增的剧情标题，并且以 Galtransl 的格式保存一份到当前目录(`titles_gtl.json`)

# DouYin Spider 设置指南

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
conda activate myenv

# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖 （如果很慢的话，可以使用镜像 设定环境变量
# export NVM_NODEJS_ORG_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/
# 然后正常使用
# nvm install <version>）
npm install
```

### 2. 配置认证信息

在项目根目录创建 `.env` 文件，内容如下：

```env
# 抖音爬虫Cookie配置
DY_COOKIES=你的抖音Cookie

# 抖音直播Cookie配置  
DY_LIVE_COOKIES=你的抖音直播Cookie
```

### 3. 获取Cookie的方法

#### 获取抖音Cookie (DY_COOKIES)：
1. 在浏览器中打开 [https://www.douyin.com](https://www.douyin.com)
2. 登录你的抖音账号
3. 按 `F12` 打开开发者工具
4. 点击 `Network` 标签
5. 刷新页面或进行任何操作
6. 找到任意一个请求，点击查看详情
7. 在 `Request Headers` 中找到 `Cookie` 字段
8. 复制整个Cookie值（包括所有分号分隔的键值对）
9. 将Cookie值粘贴到 `.env` 文件的 `DY_COOKIES` 中

#### 获取抖音直播Cookie (DY_LIVE_COOKIES)：
1. 在浏览器中打开 [https://live.douyin.com](https://live.douyin.com)
2. 登录你的抖音账号
3. 重复上述步骤3-8
4. 将Cookie值粘贴到 `.env` 文件的 `DY_LIVE_COOKIES` 中

### 4. 运行项目

```bash
# 运行爬虫
python main.py

# 运行直播监听
python dy_live/server.py
```

## ⚠️ 注意事项

1. **必须登录后的Cookie才有效** - 未登录的Cookie无法使用
2. **Cookie会过期** - 如果遇到认证错误，请重新获取Cookie
3. **遵守法律法规** - 本项目仅供学习交流使用
4. **不要频繁请求** - 避免对服务器造成过大压力

## 🔧 故障排除

### 常见错误：

1. **ModuleNotFoundError: No module named 'bs4'**
   - 解决：运行 `pip install beautifulsoup4`

2. **KeyError: 's_v_web_id'**
   - 解决：检查 `.env` 文件是否正确配置，确保Cookie包含 `s_v_web_id` 字段

3. **认证配置错误**
   - 解决：按照上述步骤重新获取并配置Cookie

### 检查配置：

运行以下命令检查配置是否正确：

```bash
python -c "
from utils.common_util import init
try:
    auth, base_path = init()
    print('✅ 配置正确！')
    print(f'Cookie keys: {list(auth.cookie.keys())}')
except Exception as e:
    print(f'❌ 配置错误: {e}')
"
```

## 📚 使用说明

### 爬取单个作品
```python
from dy_apis.douyin_api import DouyinAPI
from builder.auth import DouyinAuth

# 创建认证对象
auth = DouyinAuth()
auth.perepare_auth("你的Cookie", "", "")

# 爬取作品信息
api = DouyinAPI()
work_info = api.get_work_info(auth, "https://www.douyin.com/video/作品ID")
```

### 搜索作品
```python
# 搜索关键词
results = api.search_general_work(auth, "关键词", sort_type='0')
```

更多API使用方法请参考 `dy_apis/douyin_api.py` 文件。

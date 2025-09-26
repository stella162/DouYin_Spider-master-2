# 🎥 抖音直播监听使用指南

## 🚀 快速开始

### 1. 基本使用

```bash
# 监听指定直播间ID
python live_monitor.py 81804234251

# 监听指定直播间URL
python live_monitor.py https://live.douyin.com/81804234251
```

### 2. 获取直播间ID

**方法1：从URL获取**
- 打开抖音直播页面
- 复制地址栏中的URL
- 例如：`https://live.douyin.com/81804234251`
- 直播间ID就是最后的数字：`81804234251`

**方法2：从分享链接获取**
- 点击直播间的分享按钮
- 复制链接
- 从链接中提取数字部分

### 3. 配置认证

确保 `.env` 文件中包含有效的直播Cookie：

```env
DY_LIVE_COOKIES=你的抖音直播Cookie
```

**获取Cookie的方法**：
1. 在浏览器中打开 [https://live.douyin.com](https://live.douyin.com)
2. 登录你的抖音账号
3. 按 `F12` 打开开发者工具
4. 点击 `Network` 标签
5. 刷新页面或进行任何操作
6. 找到任意一个请求，复制其Cookie值
7. 将Cookie值粘贴到 `.env` 文件的 `DY_LIVE_COOKIES` 中

## 📱 监听内容

程序会实时显示以下信息：

- **[进入]** 用户进入直播间
- **[消息]** 用户发送弹幕
- **[礼物]** 用户送出礼物
- **[点赞]** 用户点赞
- **[关注]** 用户关注主播
- **[房间信息]** 直播间统计信息（在线人数等）

## 🔧 故障排除

### 常见问题：

1. **认证配置错误**
   ```
   ❌ 直播认证配置错误！
   ```
   - 解决：检查 `.env` 文件中的 `DY_LIVE_COOKIES` 是否正确配置

2. **直播间不存在或已关闭**
   ```
   ❌ 错误: 无法获取直播间信息
   ```
   - 解决：检查直播间ID是否正确，确认直播间是否正在直播

3. **网络连接问题**
   ```
   ❌ 错误: 连接超时
   ```
   - 解决：检查网络连接，尝试重新运行

4. **Cookie过期**
   ```
   ❌ 错误: 认证失败
   ```
   - 解决：重新获取Cookie并更新 `.env` 文件

### 检查配置：

```bash
# 检查认证配置
python -c "
import utils.common_util as common_util
try:
    common_util.load_env()
    auth = common_util.dy_live_auth
    print('✅ 直播认证配置正确！')
    print(f'Cookie keys: {list(auth.cookie.keys())}')
except Exception as e:
    print(f'❌ 配置错误: {e}')
"
```

## 📊 高级功能

### 搜索直播间

```python
from dy_apis.douyin_api import DouyinAPI
from builder.auth import DouyinAuth

# 创建认证对象
auth = DouyinAuth()
auth.perepare_auth("你的Cookie", "", "")

# 搜索直播
api = DouyinAPI()
results = api.search_live(auth, "关键词")
for live in results['data']:
    print(f"直播间: {live['lives']['title']}")
    print(f"主播: {live['lives']['author']['nickname']}")
    print(f"ID: {live['lives']['room_id']}")
```

### 获取直播间信息

```python
# 获取直播间详细信息
live_info = api.get_live_info(auth, "直播间ID")
print(f"房间状态: {live_info['room_status']}")
print(f"房间标题: {live_info['room_title']}")
```

## ⚠️ 注意事项

1. **遵守法律法规** - 本项目仅供学习交流使用
2. **不要频繁请求** - 避免对服务器造成过大压力
3. **Cookie会过期** - 定期更新认证信息
4. **直播间状态** - 只有正在直播的房间才能监听
5. **网络稳定** - 确保网络连接稳定，避免监听中断

## 🎯 使用示例

```bash
# 监听热门直播间
python live_monitor.py 81804234251

# 监听搜索结果中的直播间
python live_monitor.py 123456789

# 停止监听：按 Ctrl+C
```

## 📝 日志说明

程序运行时会显示彩色日志：
- 🟢 绿色：正常信息
- 🔵 蓝色：重要信息
- 🟡 黄色：警告信息
- 🔴 红色：错误信息

监听过程中按 `Ctrl+C` 可以安全停止程序。

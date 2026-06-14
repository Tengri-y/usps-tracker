# USPS Tracking Spider System

稳定、高效的美国邮政(USPS)包裹物流轨迹提取系统。通过反爬虫技术绕过USPS反爬机制，实现自动化物流数据采集。

## 🎯 核心功能

✅ **自动化追踪** - 批量查询USPS包裹物流轨迹
✅ **反爬虫检测** - 使用undetected-chromedriver绕过webdriver检测
✅ **智能代理轮换** - 高质量代理池自动轮换，避免IP被封
✅ **真实行为模拟** - 模拟真实用户行为（鼠标、延迟、输入等）
✅ **数据库存储** - SQLAlchemy ORM支持多种数据库
✅ **错误恢复** - 指数退避重试机制
✅ **日志追踪** - 完整的操作日志和错误追踪
✅ **API接口** - 可选REST API接口

## 🚀 快速开始

### 安装依赖

```bash
git clone https://github.com/Tengri-y/usps-tracker.git
cd usps-tracker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 快速示例

```python
from core.tracker_service import TrackerService
from config.settings import settings

tracker = TrackerService(settings)
result = tracker.track_package("9400111899223456789")
print(result)
```

## 📁 项目结构

```
usps-tracker/
├── config/              # 配置模块
│   ├── settings.py      # 全局设置
│   └── constants.py     # 常量定义
├── core/                # 核心功能
│   ├── proxy_manager.py    # 代理管理
│   ├── browser_manager.py  # 浏览器管理
│   ├── extractor.py        # 数据提取
│   └── tracker_service.py  # 追踪服务
├── utils/               # 工具函数
│   ├── logger.py        # 日志
│   ├── ua_rotator.py    # UA轮换
│   └── headers_builder.py  # Headers构建
├── scripts/             # 脚本示例
├── tests/               # 测试
├── .env.example         # 环境配置示例
├── requirements.txt     # 依赖
└── docker-compose.yml   # Docker编排
```

## 🔧 配置

编辑 `.env` 文件配置代理：

```env
PROXY_ENABLED=true
PROXY_LIST=http://proxy1.com:8080,http://proxy2.com:8080,http://proxy3.com:8080
HEADLESS=true
BROWSER_TIMEOUT=30
REQUEST_DELAY_MIN=2
REQUEST_DELAY_MAX=5
```

## 📚 更多文档

- [代理管理指南](docs/proxy_manager.md)
- [浏览器管理指南](docs/browser_manager.md)
- [故障排查](docs/troubleshooting.md)

## ⚠️ 免责声明

本项目仅供学习和研究使用。使用者需自行承担所有法律责任。

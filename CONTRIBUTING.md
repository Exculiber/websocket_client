# 贡献指南

感谢您对 WebSocket 探测工具的关注！我们欢迎所有形式的贡献。

## 🤝 如何贡献

### 报告 Bug
- 使用 GitHub Issues 报告 bug
- 请详细描述问题，包括：
  - 操作系统和版本
  - Python 版本
  - 错误信息和堆栈跟踪
  - 重现步骤

### 功能请求
- 在 GitHub Issues 中提出新功能建议
- 描述功能的使用场景和价值

### 代码贡献
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 🛠️ 开发环境设置

### 安装依赖
```bash
cd python
pip install -r requirements.txt
pip install -r requirements-build.txt
```

### 运行测试
```bash
cd python
python test_probe.py
python test_compatibility.py
```

### 构建二进制文件
```bash
cd python
python build_binary.py
```

## 📝 代码规范

- 使用 Python 3.7+ 语法
- 遵循 PEP 8 代码风格
- 添加适当的类型注解
- 编写清晰的文档字符串
- 确保所有测试通过

## 🚀 发布流程

1. 更新版本号
2. 更新 CHANGELOG.md
3. 构建二进制文件
4. 创建 Release Tag
5. 发布到 PyPI（如果适用）

## 📞 联系我们

- GitHub Issues: [项目 Issues 页面]
- 邮箱: [您的邮箱]

感谢您的贡献！🎉

#!/bin/bash

echo "🚀 腾讯云财务信息管理系统 - 项目设置脚本"
echo "=========================================="

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

echo "✅ Node.js版本: $(node --version)"

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到npm，请先安装npm"
    exit 1
fi

echo "✅ npm版本: $(npm --version)"

# 安装依赖
echo "📦 安装项目依赖..."
npm install

# 创建环境变量文件
if [ ! -f .env.local ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env.local
    echo "✅ 已创建 .env.local 文件"
    echo "⚠️  请编辑 .env.local 文件，填入您的腾讯云API凭证"
else
    echo "✅ .env.local 文件已存在"
fi

echo ""
echo "🎉 项目设置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 编辑 .env.local 文件，填入您的腾讯云API凭证"
echo "2. 运行 'npm run dev' 启动开发服务器"
echo "3. 访问 http://localhost:3000 查看应用"
echo ""
echo "📚 更多信息请查看 README.md 文件" 
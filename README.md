# XJTU Web Manager

一个用于管理网站收藏和文件的PyQt5应用程序。

## 文件结构

- `website_manager.py` - 主程序文件，包含PyQt5 GUI界面
- `data.json` - 存储网站分类和网站信息
- `file.json` - 存储文件信息
- `index.html` - 主页
- `netdisk.html` - 网盘页面
- `mobile.css` - 移动端样式文件
- `mobile.js` - 移动端JavaScript文件
- `test_redirect.html` - 测试重定向页面

## 功能

1. 网站分类管理（添加、删除、编辑分类）
2. 网站管理（添加、删除、编辑网站，支持分类）
3. 文件管理（添加、删除、编辑文件信息）

## 使用方法

运行以下命令启动程序：
```bash
python website_manager.py
```

## 数据文件格式

### data.json
```json
{
  "categories": [
    {
      "id": 1,
      "name": "分类名称",
      "websites": [
        {
          "id": 101,
          "name": "网站名称",
          "url": "https://example.com",
          "description": "网站描述"
        }
      ]
    }
  ]
}
```

### file.json
```json
{
  "files": [
    {
      "id": 1,
      "name": "文件名",
      "size": "文件大小",
      "previewUrl": "预览链接",
      "downloadUrl": "下载链接"
    }
  ]
}
```
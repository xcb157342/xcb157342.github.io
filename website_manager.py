import sys
import json
import os
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QMessageBox, QTabWidget, QFormLayout, 
                             QGroupBox, QComboBox, QFileDialog, QDialog, QInputDialog, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QTreeWidget, 
                             QTreeWidgetItem)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from github import Github

class WebsiteManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_file = 'data.json'
        self.file_data_file = 'file.json'
        self.notification_file = 'notification.json'
        self.data = {"categories": []}
        self.file_data = {"files": []}
        self.notification_data = {"notifications": []}
        self.init_ui()
        self.load_data()
        self.load_file_data()
        self.load_notification_data()
        self.update_category_list()
        self.update_file_list()
        self.update_notification_list()
        
    def init_ui(self):
        self.setWindowTitle('网站收藏管理器')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # 创建分类管理标签页
        self.category_tab = QWidget()
        self.website_tab = QWidget()
        self.file_tab = QWidget()  # 添加文件管理标签页
        self.notification_tab = QWidget()  # 添加通知管理标签页
        
        self.tab_widget.addTab(self.category_tab, "分类管理")
        self.tab_widget.addTab(self.website_tab, "网站管理")
        self.tab_widget.addTab(self.file_tab, "文件管理")  # 添加文件管理标签页
        self.tab_widget.addTab(self.notification_tab, "通知管理")  # 添加通知管理标签页
        
        self.setup_category_tab()
        self.setup_website_tab()
        self.setup_file_tab()  # 设置文件管理标签页
        self.setup_notification_tab()  # 设置通知管理标签页
        
    def showEvent(self, event):
        # 窗口显示时更新列表
        super().showEvent(event)
        self.update_website_list()
        
    def setup_category_tab(self):
        layout = QVBoxLayout()
        
        # 添加分类表单
        form_group = QGroupBox("添加新分类")
        form_layout = QFormLayout()
        
        self.category_name_input = QLineEdit()
        form_layout.addRow("分类名称:", self.category_name_input)
        
        add_category_btn = QPushButton("添加分类")
        add_category_btn.clicked.connect(self.add_category)
        form_layout.addRow(add_category_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 分类列表
        list_group = QGroupBox("现有分类")
        list_layout = QVBoxLayout()
        
        self.category_list = QListWidget()
        list_layout.addWidget(self.category_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 上移按钮
        move_up_btn = QPushButton("上移")
        move_up_btn.clicked.connect(self.move_category_up)
        button_layout.addWidget(move_up_btn)
        
        # 下移按钮
        move_down_btn = QPushButton("下移")
        move_down_btn.clicked.connect(self.move_category_down)
        button_layout.addWidget(move_down_btn)
        
        # 删除分类按钮
        delete_category_btn = QPushButton("删除选中分类")
        delete_category_btn.clicked.connect(self.delete_category)
        button_layout.addWidget(delete_category_btn)
        
        # 刷新按钮
        refresh_category_btn = QPushButton("刷新")
        refresh_category_btn.clicked.connect(self.refresh_categories)
        button_layout.addWidget(refresh_category_btn)
        
        list_layout.addLayout(button_layout)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        self.category_tab.setLayout(layout)
        
    def setup_website_tab(self):
        layout = QVBoxLayout()
        
        # 添加网站表单
        form_group = QGroupBox("添加新网站")
        form_layout = QFormLayout()
        
        self.website_name_input = QLineEdit()
        form_layout.addRow("网站名称:", self.website_name_input)
        
        self.website_url_input = QLineEdit()
        form_layout.addRow("网站URL:", self.website_url_input)
        
        self.website_category_combo = QComboBox()
        form_layout.addRow("所属分类:", self.website_category_combo)
        
        self.website_desc_input = QTextEdit()
        self.website_desc_input.setMaximumHeight(100)
        form_layout.addRow("网站描述:", self.website_desc_input)
        
        # 添加自动获取描述按钮
        fetch_desc_btn = QPushButton("自动获取描述")
        fetch_desc_btn.clicked.connect(self.fetch_website_description)
        form_layout.addRow(fetch_desc_btn)
        
        add_website_btn = QPushButton("添加网站")
        add_website_btn.setObjectName("add_website_btn")
        add_website_btn.clicked.connect(self.add_website)
        form_layout.addRow(add_website_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 网站列表（风琴式分类显示）
        list_group = QGroupBox("现有网站")
        list_layout = QVBoxLayout()
        
        # 使用QTreeWidget实现风琴式分类显示
        self.website_tree = QTreeWidget()
        self.website_tree.setHeaderLabels(["网站名称", "URL", "描述"])
        self.website_tree.setColumnWidth(0, 150)
        self.website_tree.setColumnWidth(1, 200)
        self.website_tree.setAlternatingRowColors(True)
        list_layout.addWidget(self.website_tree)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 上移按钮
        move_up_btn = QPushButton("上移")
        move_up_btn.clicked.connect(self.move_website_up)
        button_layout.addWidget(move_up_btn)
        
        # 下移按钮
        move_down_btn = QPushButton("下移")
        move_down_btn.clicked.connect(self.move_website_down)
        button_layout.addWidget(move_down_btn)
        
        # 编辑网站按钮
        edit_website_btn = QPushButton("编辑选中网站")
        edit_website_btn.clicked.connect(self.edit_website)
        button_layout.addWidget(edit_website_btn)
        
        # 删除网站按钮
        delete_website_btn = QPushButton("删除选中网站")
        delete_website_btn.clicked.connect(self.delete_website)
        button_layout.addWidget(delete_website_btn)
        
        # 上传到GitHub按钮
        upload_github_btn = QPushButton("上传到GitHub")
        upload_github_btn.clicked.connect(self.upload_to_github)
        button_layout.addWidget(upload_github_btn)
        
        # 刷新按钮
        refresh_website_btn = QPushButton("刷新")
        refresh_website_btn.clicked.connect(self.refresh_websites)
        button_layout.addWidget(refresh_website_btn)
        
        list_layout.addLayout(button_layout)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        self.website_tab.setLayout(layout)
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "加载错误", f"无法加载数据文件: {str(e)}")
                self.data = {"categories": []}
        else:
            # 创建默认数据结构
            self.data = {"categories": []}
            
    def load_file_data(self):
        if os.path.exists(self.file_data_file):
            try:
                with open(self.file_data_file, 'r', encoding='utf-8') as f:
                    self.file_data = json.load(f)
                # 确保文件数据结构存在
                if "files" not in self.file_data:
                    self.file_data["files"] = []
            except Exception as e:
                QMessageBox.warning(self, "加载错误", f"无法加载文件数据: {str(e)}")
                self.file_data = {"files": []}
        else:
            # 创建默认文件数据结构
            self.file_data = {"files": []}
            
    def load_notification_data(self):
        if os.path.exists(self.notification_file):
            try:
                with open(self.notification_file, 'r', encoding='utf-8') as f:
                    self.notification_data = json.load(f)
                # 确保通知数据结构存在
                if "notifications" not in self.notification_data:
                    self.notification_data["notifications"] = []
            except Exception as e:
                QMessageBox.warning(self, "加载错误", f"无法加载通知数据: {str(e)}")
                self.notification_data = {"notifications": []}
        else:
            # 创建默认通知数据结构
            self.notification_data = {"notifications": []}
            
    def save_data(self):
        try:
            # 保存主数据文件
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                
            # 保存文件数据到单独的文件
            with open(self.file_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_data, f, ensure_ascii=False, indent=2)
                
            # 保存通知数据到单独的文件
            with open(self.notification_file, 'w', encoding='utf-8') as f:
                json.dump(self.notification_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "保存错误", f"无法保存数据: {str(e)}")
            
    def update_category_list(self):
        # 更新分类列表显示
        self.category_list.clear()
        self.website_category_combo.clear()
        
        for category in self.data["categories"]:
            item = QListWidgetItem(category["name"])
            item.setData(Qt.UserRole, category["id"])
            self.category_list.addItem(item)
            self.website_category_combo.addItem(category["name"], category["id"])
            
    def add_category(self):
        name = self.category_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入分类名称")
            return
            
        # 检查是否已存在同名分类
        for category in self.data["categories"]:
            if category["name"] == name:
                QMessageBox.warning(self, "重复分类", "该分类已存在")
                return
                
        # 生成新的分类ID
        new_id = max([c["id"] for c in self.data["categories"]], default=0) + 1
        
        # 添加新分类
        self.data["categories"].append({
            "id": new_id,
            "name": name,
            "websites": []
        })
        
        self.save_data()
        self.update_category_list()
        
        # 清空输入框
        self.category_name_input.clear()
        
        QMessageBox.information(self, "成功", "分类添加成功")
        
    def delete_category(self):
        current_item = self.category_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要删除的分类")
            return
            
        category_id = current_item.data(Qt.UserRole)
        category_name = current_item.text()
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除分类 '{category_name}' 吗？这将同时删除该分类下的所有网站。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除分类
            self.data["categories"] = [c for c in self.data["categories"] if c["id"] != category_id]
            self.save_data()
            self.update_category_list()
            self.update_website_list()
            QMessageBox.information(self, "成功", "分类删除成功")
            
    def move_category_up(self):
        current_row = self.category_list.currentRow()
        if current_row <= 0:
            QMessageBox.warning(self, "操作错误", "已到达最顶部，无法上移")
            return
            
        # 交换数据中的位置
        self.data["categories"][current_row], self.data["categories"][current_row-1] = \
            self.data["categories"][current_row-1], self.data["categories"][current_row]
            
        self.save_data()
        self.update_category_list()
        
        # 更新选中项
        self.category_list.setCurrentRow(current_row-1)
        QMessageBox.information(self, "成功", "分类上移成功")
        
    def move_category_down(self):
        current_row = self.category_list.currentRow()
        if current_row >= self.category_list.count() - 1 or current_row < 0:
            QMessageBox.warning(self, "操作错误", "已到达最底部，无法下移")
            return
            
        # 交换数据中的位置
        self.data["categories"][current_row], self.data["categories"][current_row+1] = \
            self.data["categories"][current_row+1], self.data["categories"][current_row]
            
        self.save_data()
        self.update_category_list()
        
        # 更新选中项
        self.category_list.setCurrentRow(current_row+1)
        QMessageBox.information(self, "成功", "分类下移成功")
            
    def fetch_website_description(self):
        url = self.website_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "输入错误", "请先输入网站URL")
            return
            
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "输入错误", "URL必须以http://或https://开头")
            return
            
        try:
            # 发送HTTP请求获取网页内容
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 获取网页内容
            content = response.text
            
            # 尝试提取标题
            title = ""
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
            
            # 尝试提取描述
            description = ""
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()
            else:
                # 尝试使用Open Graph描述
                og_desc_match = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE)
                if og_desc_match:
                    description = og_desc_match.group(1).strip()
            
            # 构建描述文本
            desc_text = ""
            if title:
                desc_text += f"标题: {title}\n\n"
            if description:
                desc_text += f"描述: {description}\n\n"
            if not title and not description:
                # 如果没有找到标题和描述，尝试获取页面前200个字符
                # 移除HTML标签
                clean_content = re.sub(r'<[^>]+>', '', content)
                clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                desc_text = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
            
            # 将获取到的描述填入描述框
            self.website_desc_input.setPlainText(desc_text)
            
            QMessageBox.information(self, "成功", "已成功获取网站描述信息")
            
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法获取网站内容: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取描述时发生错误: {str(e)}")
    
    def add_website(self):
        name = self.website_name_input.text().strip()
        url = self.website_url_input.text().strip()
        description = self.website_desc_input.toPlainText().strip()
        
        if not name or not url:
            QMessageBox.warning(self, "输入错误", "请填写网站名称和URL")
            return
            
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "输入错误", "URL必须以http://或https://开头")
            return
            
        # 获取选中的分类ID
        category_id = self.website_category_combo.currentData()
        if category_id is None:
            QMessageBox.warning(self, "选择错误", "请先选择一个分类")
            return
            
        # 找到对应的分类
        category = None
        for cat in self.data["categories"]:
            if cat["id"] == category_id:
                category = cat
                break
                
        if not category:
            QMessageBox.warning(self, "错误", "找不到指定的分类")
            return
            
        # 生成新的网站ID
        new_id = max([w["id"] for c in self.data["categories"] for w in c["websites"]], default=0) + 1
        
        # 添加新网站
        new_website = {
            "id": new_id,
            "name": name,
            "url": url,
            "description": description
        }
        
        category["websites"].append(new_website)
        self.save_data()
        
        # 清空输入框
        self.website_name_input.clear()
        self.website_url_input.clear()
        self.website_desc_input.clear()
        
        QMessageBox.information(self, "成功", "网站添加成功")
        
    def edit_website(self):
        current_item = self.website_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要编辑的网站")
            return
            
        # 获取网站ID（只有网站项才有UserRole数据）
        website_id = current_item.data(0, Qt.UserRole)
        if website_id is None:
            QMessageBox.warning(self, "选择错误", "请选择一个具体的网站，而不是分类")
            return
        
        # 查找网站信息
        website = None
        category_id = None
        for category in self.data["categories"]:
            for w in category["websites"]:
                if w["id"] == website_id:
                    website = w
                    category_id = category["id"]
                    break
            if website:
                break
                
        if not website:
            QMessageBox.warning(self, "错误", "找不到选中的网站")
            return
            
        # 填充表单数据
        self.website_name_input.setText(website["name"])
        self.website_url_input.setText(website["url"])
        self.website_desc_input.setPlainText(website["description"])
        
        # 设置分类选择
        index = self.website_category_combo.findData(category_id)
        if index >= 0:
            self.website_category_combo.setCurrentIndex(index)
            
        # 保存当前编辑的网站ID
        self.current_editing_website_id = website_id
        
        # 更改按钮文本为"更新网站"
        # 找到添加按钮并更改其功能
        add_btn = self.website_tab.findChild(QPushButton, "add_website_btn")
        if not add_btn:
            # 如果找不到，就查找第一个QPushButton（添加按钮应该在前面）
            buttons = self.website_tab.findChildren(QPushButton)
            if buttons:
                add_btn = buttons[0]  # 添加按钮应该是第一个
                
        if add_btn:
            add_btn.setText("更新网站")
            add_btn.clicked.disconnect()  # 断开原有的连接
            add_btn.clicked.connect(self.update_website)
            
        # 添加取消编辑按钮
        cancel_edit_btn = self.website_tab.findChild(QPushButton, "cancel_edit_btn")
        if not cancel_edit_btn:
            cancel_edit_btn = QPushButton("取消编辑")
            cancel_edit_btn.setObjectName("cancel_edit_btn")
            cancel_edit_btn.clicked.connect(self.cancel_edit)
            # 找到正确的按钮布局
            button_layout = self.website_tab.findChild(QHBoxLayout)
            if button_layout:
                button_layout.addWidget(cancel_edit_btn)
            
        # 切换到网站管理标签页
        self.tab_widget.setCurrentWidget(self.website_tab)
        
        QMessageBox.information(self, "提示", "请在表单中修改网站信息，然后点击'更新网站'按钮保存更改")
        
    def cancel_edit(self):
        # 恢复添加按钮的功能和文本
        self.restore_add_button()
        
        # 清空输入框
        self.website_name_input.clear()
        self.website_url_input.clear()
        self.website_desc_input.clear()
        
        # 删除编辑状态标记
        if hasattr(self, 'current_editing_website_id'):
            delattr(self, 'current_editing_website_id')
            
        # 移除取消编辑按钮
        cancel_edit_btn = self.website_tab.findChild(QPushButton, "cancel_edit_btn")
        if cancel_edit_btn:
            # 从布局中移除按钮
            layout = cancel_edit_btn.parent()
            if layout and hasattr(layout, 'layout') and layout.layout():
                layout.layout().removeWidget(cancel_edit_btn)
            # 删除按钮
            cancel_edit_btn.deleteLater()
            
        QMessageBox.information(self, "提示", "已取消编辑")
        
    def update_website(self):
        name = self.website_name_input.text().strip()
        url = self.website_url_input.text().strip()
        description = self.website_desc_input.toPlainText().strip()
        
        if not name or not url:
            QMessageBox.warning(self, "输入错误", "请填写网站名称和URL")
            return
            
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "输入错误", "URL必须以http://或https://开头")
            return
            
        # 获取选中的分类ID
        category_id = self.website_category_combo.currentData()
        if category_id is None:
            QMessageBox.warning(self, "选择错误", "请先选择一个分类")
            return
            
        # 检查是否正在编辑网站
        if not hasattr(self, 'current_editing_website_id'):
            QMessageBox.warning(self, "错误", "没有正在编辑的网站")
            return
            
        website_id = self.current_editing_website_id
            
        # 找到对应的分类和网站
        category = None
        website = None
        for cat in self.data["categories"]:
            if cat["id"] == category_id:
                category = cat
                # 如果网站原本就在这个分类中，找到它
                for w in cat["websites"]:
                    if w["id"] == website_id:
                        website = w
                        break
                break
                
        if not category:
            QMessageBox.warning(self, "错误", "找不到指定的分类")
            return
            
        # 如果网站原本不在这个分类中，需要从原分类中移除并添加到新分类
        if not website:
            # 从原分类中移除
            for cat in self.data["categories"]:
                cat["websites"] = [w for w in cat["websites"] if w["id"] != website_id]
                
            # 创建更新后的网站对象
            updated_website = {
                "id": website_id,
                "name": name,
                "url": url,
                "description": description
            }
            
            # 添加到新分类
            category["websites"].append(updated_website)
        else:
            # 直接更新网站信息
            website["name"] = name
            website["url"] = url
            website["description"] = description
            
        self.save_data()
        
        # 恢复按钮功能
        self.restore_add_button()
        
        # 清空输入框
        self.website_name_input.clear()
        self.website_url_input.clear()
        self.website_desc_input.clear()
        
        # 更新列表
        self.update_website_list()
        
        # 删除编辑状态标记
        if hasattr(self, 'current_editing_website_id'):
            delattr(self, 'current_editing_website_id')
            
        QMessageBox.information(self, "成功", "网站更新成功")
        
    def restore_add_button(self):
        # 恢复添加按钮的功能和文本
        buttons = self.website_tab.findChildren(QPushButton)
        if buttons:
            add_btn = buttons[0]  # 添加按钮应该是第一个
            add_btn.setText("添加网站")
            try:
                add_btn.clicked.disconnect()  # 断开所有连接
            except:
                pass
            add_btn.clicked.connect(self.add_website)
            
        # 移除取消编辑按钮
        cancel_edit_btn = self.website_tab.findChild(QPushButton, "cancel_edit_btn")
        if cancel_edit_btn:
            # 从布局中移除按钮
            layout = cancel_edit_btn.parent()
            if layout and hasattr(layout, 'removeWidget'):
                layout.removeWidget(cancel_edit_btn)
            # 删除按钮
            cancel_edit_btn.deleteLater()
            
    def delete_website(self):
        current_item = self.website_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要删除的网站")
            return
            
        # 获取网站ID（只有网站项才有UserRole数据）
        website_id = current_item.data(0, Qt.UserRole)
        if website_id is None:
            QMessageBox.warning(self, "选择错误", "请选择一个具体的网站，而不是分类")
            return
            
        # 获取网站名称
        website_name = current_item.text(0)
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除网站 '{website_name}' 吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 在所有分类中查找并删除该网站
            for category in self.data["categories"]:
                category["websites"] = [w for w in category["websites"] if w["id"] != website_id]
                
            self.save_data()
            self.update_website_list()
            QMessageBox.information(self, "成功", "网站删除成功")
        
    def move_website_up(self):
        current_item = self.website_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要移动的网站")
            return
            
        # 获取网站ID（只有网站项才有UserRole数据）
        website_id = current_item.data(0, Qt.UserRole)
        if website_id is None:
            QMessageBox.warning(self, "选择错误", "请选择一个具体的网站，而不是分类")
            return
            
        # 查找网站所在的分类和位置
        found_category = None
        found_website_index = -1
        
        for category in self.data["categories"]:
            for i, website in enumerate(category["websites"]):
                if website["id"] == website_id:
                    found_category = category
                    found_website_index = i
                    break
            if found_category:
                break
                
        if not found_category or found_website_index == -1:
            QMessageBox.warning(self, "错误", "找不到选中的网站")
            return
            
        # 检查是否已到达顶部
        if found_website_index <= 0:
            QMessageBox.warning(self, "操作错误", "已到达分类顶部，无法上移")
            return
            
        # 交换位置
        found_category["websites"][found_website_index], found_category["websites"][found_website_index-1] = \
            found_category["websites"][found_website_index-1], found_category["websites"][found_website_index]
            
        self.save_data()
        self.update_website_list()
        
        # 更新选中项
        # 需要重新找到该网站项并选中
        for i in range(self.website_tree.topLevelItemCount()):
            category_item = self.website_tree.topLevelItem(i)
            if category_item.data(0, Qt.UserRole) == found_category["id"]:
                website_item = category_item.child(found_website_index-1)
                if website_item:
                    self.website_tree.setCurrentItem(website_item)
                break
                
    def move_website_down(self):
        current_item = self.website_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要移动的网站")
            return
            
        # 获取网站ID（只有网站项才有UserRole数据）
        website_id = current_item.data(0, Qt.UserRole)
        if website_id is None:
            QMessageBox.warning(self, "选择错误", "请选择一个具体的网站，而不是分类")
            return
            
        # 查找网站所在的分类和位置
        found_category = None
        found_website_index = -1
        
        for category in self.data["categories"]:
            for i, website in enumerate(category["websites"]):
                if website["id"] == website_id:
                    found_category = category
                    found_website_index = i
                    break
            if found_category:
                break
                
        if not found_category or found_website_index == -1:
            QMessageBox.warning(self, "错误", "找不到选中的网站")
            return
            
        # 检查是否已到达底部
        if found_website_index >= len(found_category["websites"]) - 1:
            QMessageBox.warning(self, "操作错误", "已到达分类底部，无法下移")
            return
            
        # 交换位置
        found_category["websites"][found_website_index], found_category["websites"][found_website_index+1] = \
            found_category["websites"][found_website_index+1], found_category["websites"][found_website_index]
            
        self.save_data()
        self.update_website_list()
        
        # 更新选中项
        # 需要重新找到该网站项并选中
        for i in range(self.website_tree.topLevelItemCount()):
            category_item = self.website_tree.topLevelItem(i)
            if category_item.data(0, Qt.UserRole) == found_category["id"]:
                website_item = category_item.child(found_website_index+1)
                if website_item:
                    self.website_tree.setCurrentItem(website_item)
                break
                
    def update_website_list(self):
        # 更新网站列表显示（风琴式分类显示）
        self.website_tree.clear()
        
        # 为每个分类创建一个顶级项
        for category in self.data["categories"]:
            category_item = QTreeWidgetItem(self.website_tree, [category["name"]])
            category_item.setExpanded(True)  # 默认展开分类
            category_item.setData(0, Qt.UserRole, category["id"])  # 存储分类ID
            
            # 为每个网站创建子项
            for website in category["websites"]:
                website_item = QTreeWidgetItem(category_item, [
                    website["name"],
                    website["url"],
                    website["description"]
                ])
                website_item.setData(0, Qt.UserRole, website["id"])  # 存储网站ID
        
        # 展开所有分类
        self.website_tree.expandAll()
                
    def upload_to_github(self):
        # 获取GitHub访问令牌
        token, ok = QInputDialog.getText(self, "GitHub访问令牌", "请输入您的GitHub个人访问令牌:")
        if not ok or not token:
            return
            
        try:
            # 连接到GitHub
            g = Github(token)
            user = g.get_user()
            
            # 获取仓库信息
            repo_name, ok = QInputDialog.getText(self, "仓库信息", "请输入仓库名称 (格式: username/repo_name):")
            if not ok or not repo_name:
                return
                
            # 获取仓库
            repo = g.get_repo(repo_name)
            
            # 读取data.json文件内容
            with open(self.data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件SHA值（如果文件已存在）
            sha = None
            try:
                contents = repo.get_contents(self.data_file)
                sha = contents.sha
            except:
                pass  # 文件不存在
            
            # 上传文件
            if sha:
                # 更新现有文件
                repo.update_file(
                    path=self.data_file,
                    message="Update website data",
                    content=content,
                    sha=sha
                )
            else:
                # 创建新文件
                repo.create_file(
                    path=self.data_file,
                    message="Add website data",
                    content=content
                )
            
            QMessageBox.information(self, "成功", "数据已成功上传到GitHub仓库")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"上传失败: {str(e)}")

    def upload_file_to_github(self):
        # 获取GitHub访问令牌
        token, ok = QInputDialog.getText(self, "GitHub访问令牌", "请输入您的GitHub个人访问令牌:")
        if not ok or not token:
            return
            
        try:
            # 连接到GitHub
            g = Github(token)
            user = g.get_user()
            
            # 获取仓库信息
            repo_name, ok = QInputDialog.getText(self, "仓库信息", "请输入仓库名称 (格式: username/repo_name):")
            if not ok or not repo_name:
                return
                
            # 获取仓库
            repo = g.get_repo(repo_name)
            
            # 读取file.json文件内容
            with open(self.file_data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件SHA值（如果文件已存在）
            sha = None
            try:
                contents = repo.get_contents(self.file_data_file)
                sha = contents.sha
            except:
                pass  # 文件不存在
            
            # 上传文件
            if sha:
                # 更新现有文件
                repo.update_file(
                    path=self.file_data_file,
                    message="Update file data",
                    content=content,
                    sha=sha
                )
            else:
                # 创建新文件
                repo.create_file(
                    path=self.file_data_file,
                    message="Add file data",
                    content=content
                )
            
            QMessageBox.information(self, "成功", "文件数据已成功上传到GitHub仓库")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"上传失败: {str(e)}")

    def setup_file_tab(self):
        layout = QVBoxLayout()
        
        # 添加文件表单
        form_group = QGroupBox("添加新文件")
        form_layout = QFormLayout()
        
        self.file_name_input = QLineEdit()
        form_layout.addRow("文件名:", self.file_name_input)
        
        self.file_size_input = QLineEdit()
        form_layout.addRow("文件大小:", self.file_size_input)
        
        self.file_preview_url_input = QLineEdit()
        form_layout.addRow("预览链接:", self.file_preview_url_input)
        
        self.file_download_url_input = QLineEdit()
        form_layout.addRow("下载链接:", self.file_download_url_input)
        
        add_file_btn = QPushButton("添加文件")
        add_file_btn.clicked.connect(self.add_file)
        form_layout.addRow(add_file_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 文件列表
        list_group = QGroupBox("现有文件")
        list_layout = QVBoxLayout()
        
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(7)
        self.file_table.setHorizontalHeaderLabels(["文件名", "大小", "时间", "预览链接", "下载链接", "编辑", "删除"])
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        list_layout.addWidget(self.file_table)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 编辑文件按钮
        edit_file_btn = QPushButton("编辑选中文件")
        edit_file_btn.clicked.connect(self.edit_file)
        button_layout.addWidget(edit_file_btn)
        
        # 删除文件按钮
        delete_file_btn = QPushButton("删除选中文件")
        delete_file_btn.clicked.connect(self.delete_file)
        button_layout.addWidget(delete_file_btn)
        
        # 刷新按钮
        refresh_file_btn = QPushButton("刷新")
        refresh_file_btn.clicked.connect(self.refresh_files)
        button_layout.addWidget(refresh_file_btn)
        
        # 上传到GitHub按钮
        upload_file_github_btn = QPushButton("上传到GitHub")
        upload_file_github_btn.clicked.connect(self.upload_file_to_github)
        button_layout.addWidget(upload_file_github_btn)
        
        list_layout.addLayout(button_layout)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        self.file_tab.setLayout(layout)
        
    def setup_notification_tab(self):
        layout = QVBoxLayout()
        
        # 添加通知表单
        form_group = QGroupBox("添加新通知")
        form_layout = QFormLayout()
        
        self.notification_title_input = QLineEdit()
        form_layout.addRow("标题:", self.notification_title_input)
        
        self.notification_content_input = QTextEdit()
        self.notification_content_input.setMaximumHeight(100)
        form_layout.addRow("内容:", self.notification_content_input)
        
        self.notification_attachment_input = QLineEdit()
        form_layout.addRow("附件:", self.notification_attachment_input)
        
        self.notification_link_input = QLineEdit()
        form_layout.addRow("链接:", self.notification_link_input)
        
        add_notification_btn = QPushButton("添加通知")
        add_notification_btn.clicked.connect(self.add_notification)
        form_layout.addRow(add_notification_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 通知列表
        list_group = QGroupBox("现有通知")
        list_layout = QVBoxLayout()
        
        self.notification_table = QTableWidget()
        self.notification_table.setColumnCount(6)
        self.notification_table.setHorizontalHeaderLabels(["标题", "内容", "时间", "附件", "链接", "操作"])
        self.notification_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.notification_table.setSelectionBehavior(QTableWidget.SelectRows)
        list_layout.addWidget(self.notification_table)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 编辑通知按钮
        edit_notification_btn = QPushButton("编辑选中通知")
        edit_notification_btn.clicked.connect(self.edit_notification)
        button_layout.addWidget(edit_notification_btn)
        
        # 删除通知按钮
        delete_notification_btn = QPushButton("删除选中通知")
        delete_notification_btn.clicked.connect(self.delete_notification)
        button_layout.addWidget(delete_notification_btn)
        
        # 刷新按钮
        refresh_notification_btn = QPushButton("刷新")
        refresh_notification_btn.clicked.connect(self.refresh_notifications)
        button_layout.addWidget(refresh_notification_btn)
        
        list_layout.addLayout(button_layout)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        self.notification_tab.setLayout(layout)
        
    def add_file(self):
        name = self.file_name_input.text().strip()
        size = self.file_size_input.text().strip()
        preview_url = self.file_preview_url_input.text().strip()
        download_url = self.file_download_url_input.text().strip()
        
        if not name or not size or not preview_url or not download_url:
            QMessageBox.warning(self, "输入错误", "请填写所有字段")
            return
            
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 生成新的文件ID
        new_id = max([f["id"] for f in self.file_data["files"]], default=0) + 1
        
        # 添加新文件，包含时间字段
        new_file = {
            "id": new_id,
            "name": name,
            "size": size,
            "previewUrl": preview_url,
            "downloadUrl": download_url,
            "time": current_time
        }
        
        self.file_data["files"].append(new_file)
        self.save_data()
        self.update_file_list()
        
        # 清空输入框
        self.file_name_input.clear()
        self.file_size_input.clear()
        self.file_preview_url_input.clear()
        self.file_download_url_input.clear()
        
        QMessageBox.information(self, "成功", "文件添加成功")
        
    def edit_file(self, file_id=None):
        # 如果没有传入file_id，则从表格选择中获取
        if file_id is None:
            selected_rows = self.file_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "选择错误", "请先选择要编辑的文件")
                return
                
            row = selected_rows[0].row()
            file_id = int(self.file_table.item(row, 0).data(Qt.UserRole))
        
        # 查找文件信息
        file = None
        for f in self.file_data["files"]:
            if f["id"] == file_id:
                file = f
                break
                
        if not file:
            QMessageBox.warning(self, "错误", "找不到选中的文件")
            return
            
        # 填充表单数据
        self.file_name_input.setText(file["name"])
        self.file_size_input.setText(file["size"])
        self.file_preview_url_input.setText(file["previewUrl"])
        self.file_download_url_input.setText(file["downloadUrl"])
        
        # 保存当前编辑的文件ID
        self.current_editing_file_id = file_id
        
        # 更改按钮文本为"更新文件"
        buttons = self.file_tab.findChildren(QPushButton)
        if buttons:
            add_btn = buttons[0]  # 添加按钮应该是第一个
            add_btn.setText("更新文件")
            add_btn.clicked.disconnect()  # 断开原有的连接
            add_btn.clicked.connect(self.update_file)
            
        QMessageBox.information(self, "提示", "请在表单中修改文件信息，然后点击'更新文件'按钮保存更改")
        
    def update_file(self):
        # 检查是否正在编辑文件
        if not hasattr(self, 'current_editing_file_id'):
            QMessageBox.warning(self, "错误", "没有正在编辑的文件")
            return
            
        file_id = self.current_editing_file_id
        
        # 获取表单数据
        name = self.file_name_input.text().strip()
        size = self.file_size_input.text().strip()
        preview_url = self.file_preview_url_input.text().strip()
        download_url = self.file_download_url_input.text().strip()
        
        # 验证数据
        if not name or not size or not preview_url or not download_url:
            QMessageBox.warning(self, "输入错误", "请填写所有字段")
            return
            
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            
        # 查找并更新文件信息
        for file_info in self.file_data["files"]:
            if file_info["id"] == file_id:
                file_info["name"] = name
                file_info["size"] = size
                file_info["previewUrl"] = preview_url
                file_info["downloadUrl"] = download_url
                # 更新时间信息
                file_info["time"] = current_time
                break
        else:
            QMessageBox.warning(self, "错误", "未找到指定的文件")
            return
        
        # 保存数据
        self.save_data()
        
        # 更新显示
        self.update_file_list()
        
        # 恢复添加按钮
        self.restore_add_file_button()
        
        # 清空输入框
        self.file_name_input.clear()
        self.file_size_input.clear()
        self.file_preview_url_input.clear()
        self.file_download_url_input.clear()
        
        # 删除编辑状态标记
        if hasattr(self, 'current_editing_file_id'):
            delattr(self, 'current_editing_file_id')
        
        # 显示成功消息
        QMessageBox.information(self, "成功", "文件更新成功")
        
    def restore_add_file_button(self):
        # 恢复添加按钮的功能和文本
        buttons = self.file_tab.findChildren(QPushButton)
        if buttons:
            add_btn = buttons[0]  # 添加按钮应该是第一个
            add_btn.setText("添加文件")
            try:
                add_btn.clicked.disconnect()  # 断开所有连接
            except:
                pass
            add_btn.clicked.connect(self.add_file)
            
    def delete_file(self, file_id=None):
        # 如果没有传入file_id，则从表格选择中获取
        if file_id is None:
            selected_rows = self.file_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "选择错误", "请先选择要删除的文件")
                return
                
            row = selected_rows[0].row()
            file_id = int(self.file_table.item(row, 0).data(Qt.UserRole))
        
        # 查找文件名
        file_name = ""
        for f in self.file_data["files"]:
            if f["id"] == file_id:
                file_name = f["name"]
                break
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除文件 '{file_name}' 吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除文件
            self.file_data["files"] = [f for f in self.file_data["files"] if f["id"] != file_id]
                
            self.save_data()
            self.update_file_list()
            QMessageBox.information(self, "成功", "文件删除成功")
        
    def update_file_list(self):
        # 清空表格
        self.file_table.setRowCount(0)
        
        # 从文件数据中加载文件信息
        files = self.file_data.get("files", [])
        for file_info in files:
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            
            # 添加文件信息
            self.file_table.setItem(row_position, 0, QTableWidgetItem(file_info["name"]))
            self.file_table.setItem(row_position, 1, QTableWidgetItem(file_info["size"]))
            # 添加时间信息
            time_str = file_info.get("time", "")
            self.file_table.setItem(row_position, 2, QTableWidgetItem(time_str))
            
            # 预览按钮
            preview_btn = QPushButton("预览")
            preview_btn.clicked.connect(lambda checked, url=file_info["previewUrl"]: self.open_url(url))
            self.file_table.setCellWidget(row_position, 3, preview_btn)
            
            # 下载按钮
            download_btn = QPushButton("下载")
            download_btn.clicked.connect(lambda checked, url=file_info["downloadUrl"]: self.download_file(url))
            self.file_table.setCellWidget(row_position, 4, download_btn)
            
            # 编辑按钮
            edit_btn = QPushButton("编辑")
            edit_btn.setStyleSheet("background-color: #ffc107; color: black;")
            edit_btn.clicked.connect(lambda checked, fid=file_info["id"]: self.edit_file(file_id=fid))
            self.file_table.setCellWidget(row_position, 5, edit_btn)
            
            # 删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
            delete_btn.clicked.connect(lambda checked, fid=file_info["id"]: self.delete_file(file_id=fid))
            self.file_table.setCellWidget(row_position, 6, delete_btn)
            
    def refresh_categories(self):
        """刷新分类信息"""
        self.load_data()
        self.update_category_list()
        QMessageBox.information(self, "刷新成功", "分类信息已刷新")
        
    def refresh_websites(self):
        """刷新网站信息"""
        self.load_data()
        self.update_website_list()
        QMessageBox.information(self, "刷新成功", "网站信息已刷新")
        
    def refresh_files(self):
        """刷新文件信息"""
        self.load_file_data()
        self.update_file_list()
        QMessageBox.information(self, "刷新成功", "文件信息已刷新")
        
    def add_notification(self):
        title = self.notification_title_input.text().strip()
        content = self.notification_content_input.toPlainText().strip()
        attachment = self.notification_attachment_input.text().strip()
        link = self.notification_link_input.text().strip()
        
        if not title or not content:
            QMessageBox.warning(self, "输入错误", "请填写标题和内容")
            return
            
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 生成新的通知ID
        new_id = max([n["id"] for n in self.notification_data["notifications"]], default=0) + 1
        
        # 添加新通知，默认不置顶
        new_notification = {
            "id": new_id,
            "title": title,
            "content": content,
            "time": current_time,
            "attachment": attachment,
            "link": link,
            "pinned": False  # 默认不置顶
        }
        
        self.notification_data["notifications"].append(new_notification)
        self.save_data()
        self.update_notification_list()
        
        # 清空输入框
        self.notification_title_input.clear()
        self.notification_content_input.clear()
        self.notification_attachment_input.clear()
        self.notification_link_input.clear()
        
        QMessageBox.information(self, "成功", "通知添加成功")
        
    def edit_notification(self):
        selected_rows = self.notification_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "选择错误", "请先选择要编辑的通知")
            return
            
        row = selected_rows[0].row()
        notification_id = int(self.notification_table.item(row, 0).data(Qt.UserRole))
        
        # 查找通知信息
        notification = None
        for n in self.notification_data["notifications"]:
            if n["id"] == notification_id:
                notification = n
                break
                
        if not notification:
            QMessageBox.warning(self, "错误", "找不到选中的通知")
            return
            
        # 填充表单数据
        self.notification_title_input.setText(notification["title"])
        self.notification_content_input.setPlainText(notification["content"])
        self.notification_attachment_input.setText(notification["attachment"])
        self.notification_link_input.setText(notification["link"])
        
        # 保存当前编辑的通知ID
        self.current_editing_notification_id = notification_id
        
        # 更改按钮文本为"更新通知"
        buttons = self.notification_tab.findChildren(QPushButton)
        if buttons:
            add_btn = buttons[0]  # 添加按钮应该是第一个
            add_btn.setText("更新通知")
            add_btn.clicked.disconnect()  # 断开原有的连接
            add_btn.clicked.connect(self.update_notification)
            
        QMessageBox.information(self, "提示", "请在表单中修改通知信息，然后点击'更新通知'按钮保存更改")
        
    def update_notification(self):
        # 检查是否正在编辑通知
        if not hasattr(self, 'current_editing_notification_id'):
            QMessageBox.warning(self, "错误", "没有正在编辑的通知")
            return
            
        notification_id = self.current_editing_notification_id
        
        # 获取表单数据
        title = self.notification_title_input.text().strip()
        content = self.notification_content_input.toPlainText().strip()
        attachment = self.notification_attachment_input.text().strip()
        link = self.notification_link_input.text().strip()
        
        # 验证数据
        if not title or not content:
            QMessageBox.warning(self, "输入错误", "请填写标题和内容")
            return
            
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            
        # 查找并更新通知信息
        for notification in self.notification_data["notifications"]:
            if notification["id"] == notification_id:
                # 保存原始的置顶状态
                pinned = notification.get("pinned", False)
                
                notification["title"] = title
                notification["content"] = content
                notification["time"] = current_time
                notification["attachment"] = attachment
                notification["link"] = link
                notification["pinned"] = pinned  # 保持置顶状态
                break
        else:
            QMessageBox.warning(self, "错误", "未找到指定的通知")
            return
        
        # 保存数据
        self.save_data()
        
        # 更新显示
        self.update_notification_list()
        
        # 恢复添加按钮
        self.restore_add_notification_button()
        
        # 清空输入框
        self.notification_title_input.clear()
        self.notification_content_input.clear()
        self.notification_attachment_input.clear()
        self.notification_link_input.clear()
        
        # 删除编辑状态标记
        if hasattr(self, 'current_editing_notification_id'):
            delattr(self, 'current_editing_notification_id')
        
        # 显示成功消息
        QMessageBox.information(self, "成功", "通知更新成功")
        
    def restore_add_notification_button(self):
        # 恢复添加按钮的功能和文本
        buttons = self.notification_tab.findChildren(QPushButton)
        if buttons:
            add_btn = buttons[0]  # 添加按钮应该是第一个
            add_btn.setText("添加通知")
            try:
                add_btn.clicked.disconnect()  # 断开所有连接
            except:
                pass
            add_btn.clicked.connect(self.add_notification)
            
    def delete_notification(self):
        selected_rows = self.notification_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "选择错误", "请先选择要删除的通知")
            return
            
        row = selected_rows[0].row()
        notification_id = int(self.notification_table.item(row, 0).data(Qt.UserRole))
        
        # 查找通知标题
        notification_title = ""
        for n in self.notification_data["notifications"]:
            if n["id"] == notification_id:
                notification_title = n["title"]
                break
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除通知 '{notification_title}' 吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除通知
            self.notification_data["notifications"] = [n for n in self.notification_data["notifications"] if n["id"] != notification_id]
                
            self.save_data()
            self.update_notification_list()
            QMessageBox.information(self, "成功", "通知删除成功")
            
    def update_notification_list(self):
        # 清空表格
        self.notification_table.setRowCount(0)
        
        # 从通知数据中加载通知信息
        notifications = self.notification_data.get("notifications", [])
        
        # 按置顶状态排序，置顶的通知显示在前面
        pinned_notifications = [n for n in notifications if n.get("pinned", False)]
        unpinned_notifications = [n for n in notifications if not n.get("pinned", False)]
        sorted_notifications = pinned_notifications + unpinned_notifications
        
        for notification in sorted_notifications:
            row_position = self.notification_table.rowCount()
            self.notification_table.insertRow(row_position)
            
            # 添加通知信息，置顶的通知在标题前添加标记
            title_text = notification["title"]
            if notification.get("pinned", False):
                title_text = "📌 " + title_text  # 添加置顶标记
            
            title_item = QTableWidgetItem(title_text)
            title_item.setData(Qt.UserRole, notification["id"])  # 存储ID用于操作
            self.notification_table.setItem(row_position, 0, title_item)
            
            content_item = QTableWidgetItem(notification["content"])
            content_item.setData(Qt.UserRole, notification["id"])
            self.notification_table.setItem(row_position, 1, content_item)
            
            # 添加时间信息
            time_str = notification.get("time", "")
            time_item = QTableWidgetItem(time_str)
            time_item.setData(Qt.UserRole, notification["id"])
            self.notification_table.setItem(row_position, 2, time_item)
            
            # 添加附件信息
            attachment_item = QTableWidgetItem(notification.get("attachment", ""))
            attachment_item.setData(Qt.UserRole, notification["id"])
            self.notification_table.setItem(row_position, 3, attachment_item)
            
            # 添加链接信息
            link_item = QTableWidgetItem(notification.get("link", ""))
            link_item.setData(Qt.UserRole, notification["id"])
            self.notification_table.setItem(row_position, 4, link_item)
            
            # 操作按钮布局
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(2)
            
            # 置顶/取消置顶按钮
            pinned = notification.get("pinned", False)
            pin_btn_text = "取消置顶" if pinned else "置顶"
            pin_btn = QPushButton(pin_btn_text)
            pin_btn.setStyleSheet("background-color: #007bff; color: white; padding: 2px;")
            pin_btn.clicked.connect(lambda checked, nid=notification["id"]: self.toggle_notification_pin(nid))
            button_layout.addWidget(pin_btn)
            
            # 编辑按钮
            edit_btn = QPushButton("编辑")
            edit_btn.setStyleSheet("background-color: #ffc107; color: black; padding: 2px;")
            edit_btn.clicked.connect(lambda checked, nid=notification["id"]: self.edit_notification_by_id(nid))
            button_layout.addWidget(edit_btn)
            
            # 删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 2px;")
            delete_btn.clicked.connect(lambda checked, nid=notification["id"]: self.delete_notification_by_id(nid))
            button_layout.addWidget(delete_btn)
            
            # 创建一个widget来包含按钮布局
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.notification_table.setCellWidget(row_position, 5, button_widget)
            
    def edit_notification_by_id(self, notification_id):
        """通过ID编辑通知"""
        # 查找通知信息
        notification = None
        for n in self.notification_data["notifications"]:
            if n["id"] == notification_id:
                notification = n
                break
                
        if not notification:
            QMessageBox.warning(self, "错误", "找不到选中的通知")
            return
            
        # 填充表单数据
        self.notification_title_input.setText(notification["title"])
        self.notification_content_input.setPlainText(notification["content"])
        self.notification_attachment_input.setText(notification["attachment"])
        self.notification_link_input.setText(notification["link"])
        
        # 保存当前编辑的通知ID
        self.current_editing_notification_id = notification_id
        
        # 更改按钮文本为"更新通知"
        buttons = self.notification_tab.findChildren(QPushButton)
        if buttons:
            add_btn = buttons[0]  # 添加按钮应该是第一个
            add_btn.setText("更新通知")
            add_btn.clicked.disconnect()  # 断开原有的连接
            add_btn.clicked.connect(self.update_notification)
            
        # 切换到通知管理标签页
        self.tab_widget.setCurrentWidget(self.notification_tab)
        
        QMessageBox.information(self, "提示", "请在表单中修改通知信息，然后点击'更新通知'按钮保存更改")
        
    def delete_notification_by_id(self, notification_id):
        """通过ID删除通知"""
        # 查找通知标题
        notification_title = ""
        for n in self.notification_data["notifications"]:
            if n["id"] == notification_id:
                notification_title = n["title"]
                break
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除通知 '{notification_title}' 吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除通知
            self.notification_data["notifications"] = [n for n in self.notification_data["notifications"] if n["id"] != notification_id]
                
            self.save_data()
            self.update_notification_list()
            QMessageBox.information(self, "成功", "通知删除成功")
            
    def refresh_notifications(self):
        """刷新通知信息"""
        self.load_notification_data()
        self.update_notification_list()
        QMessageBox.information(self, "刷新成功", "通知信息已刷新")
        
    def toggle_notification_pin(self, notification_id):
        """切换通知的置顶状态"""
        # 查找通知
        notification = None
        for n in self.notification_data["notifications"]:
            if n["id"] == notification_id:
                notification = n
                break
                
        if not notification:
            QMessageBox.warning(self, "错误", "找不到指定的通知")
            return
            
        # 切换置顶状态
        notification["pinned"] = not notification.get("pinned", False)
        
        # 保存数据
        self.save_data()
        
        # 更新显示
        self.update_notification_list()
        
        # 显示成功消息
        status = "已置顶" if notification["pinned"] else "已取消置顶"
        QMessageBox.information(self, "成功", f"通知{status}")
        
    def open_url(self, url):
        # 创建模态对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("预览")
        dialog.setGeometry(100, 100, 1000, 700)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 创建WebView组件
        web_view = QWebEngineView()
        from PyQt5.QtCore import QUrl
        web_view.load(QUrl(url))  # 加载URL
        
        # 添加WebView到布局
        layout.addWidget(web_view)
        
        # 创建关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        
        # 添加按钮到布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # 设置对话框布局
        dialog.setLayout(layout)
        
        # 显示模态对话框
        dialog.exec_()
        
    def download_file(self, url):
        # 使用系统默认浏览器直接打开下载链接
        import webbrowser
        webbrowser.open(url)

def main():
    app = QApplication(sys.argv)
    # 设置全局字体为微软雅黑
    font = QFont("微软雅黑")
    font.setPointSize(9)  # 设置默认字体大小
    app.setFont(font)
    manager = WebsiteManager()
    manager.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
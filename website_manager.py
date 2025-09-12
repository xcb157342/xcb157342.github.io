import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QMessageBox, QTabWidget, QFormLayout, 
                             QGroupBox, QComboBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class WebsiteManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_file = 'data.json'
        self.data = {"categories": []}
        self.init_ui()
        self.load_data()
        self.update_category_list()
        
    def init_ui(self):
        self.setWindowTitle('网站收藏管理器')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # 创建分类管理标签页
        self.category_tab = QWidget()
        self.website_tab = QWidget()
        
        self.tab_widget.addTab(self.category_tab, "分类管理")
        self.tab_widget.addTab(self.website_tab, "网站管理")
        
        self.setup_category_tab()
        self.setup_website_tab()
        
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
        
        # 删除分类按钮
        delete_category_btn = QPushButton("删除选中分类")
        delete_category_btn.clicked.connect(self.delete_category)
        list_layout.addWidget(delete_category_btn)
        
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
        
        add_website_btn = QPushButton("添加网站")
        add_website_btn.setObjectName("add_website_btn")
        add_website_btn.clicked.connect(self.add_website)
        form_layout.addRow(add_website_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 网站列表
        list_group = QGroupBox("现有网站")
        list_layout = QVBoxLayout()
        
        self.website_list = QListWidget()
        list_layout.addWidget(self.website_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 编辑网站按钮
        edit_website_btn = QPushButton("编辑选中网站")
        edit_website_btn.clicked.connect(self.edit_website)
        button_layout.addWidget(edit_website_btn)
        
        # 删除网站按钮
        delete_website_btn = QPushButton("删除选中网站")
        delete_website_btn.clicked.connect(self.delete_website)
        button_layout.addWidget(delete_website_btn)
        
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
            
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "保存错误", f"无法保存数据文件: {str(e)}")
            
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
        current_item = self.website_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要编辑的网站")
            return
            
        # 获取网站ID
        website_id = current_item.data(Qt.UserRole)
        
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
            
        # 切换到网站管理标签页
        self.tab_widget.setCurrentWidget(self.website_tab)
        
        QMessageBox.information(self, "提示", "请在表单中修改网站信息，然后点击'更新网站'按钮保存更改")
        
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
            
    def delete_website(self):
        current_item = self.website_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择要删除的网站")
            return
            
        # 从项目文本中提取网站ID（最后一部分是ID）
        website_id = current_item.data(Qt.UserRole)
        
        # 确认删除
        website_name = current_item.text().split('] ')[1] if '] ' in current_item.text() else current_item.text()
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
        
    def update_website_list(self):
        # 更新网站列表显示
        self.website_list.clear()
        
        for category in self.data["categories"]:
            for website in category["websites"]:
                item_text = f"[{category['name']}] {website['name']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, website["id"])
                self.website_list.addItem(item)

def main():
    app = QApplication(sys.argv)
    manager = WebsiteManager()
    manager.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
// 移动端网站数据处理
let websiteData = [];
let currentWebsiteUrl = ''; // 存储当前网站的URL

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    loadData().then(() => {
        renderCategories();
        setupEventListeners();
        setupContextMenu(); // 设置悬浮菜单
        setupModalSystem(); // 设置模态框系统
    });
});

// 加载数据
async function loadData() {
    try {
        const response = await fetch('data.json');
        const data = await response.json();
        // 使用与桌面端相同的数据结构
        websiteData = data.categories;
    } catch (error) {
        console.error('加载数据失败:', error);
        // 如果加载失败，使用默认数据
        websiteData = [
            {
                id: 1,
                name: "学习资源",
                websites: [
                    {
                        id: 101,
                        name: "MDN Web Docs",
                        url: "https://developer.mozilla.org/zh-CN/",
                        description: "Web开发权威文档，包含HTML、CSS、JavaScript等技术资料"
                    }
                ]
            }
        ];
    }
}

// 渲染分类
function renderCategories() {
    const container = document.getElementById('categories-container');
    container.innerHTML = '';
    
    websiteData.forEach(category => {
        const accordion = document.createElement('div');
        accordion.className = 'accordion';
        accordion.innerHTML = `
            <div class="accordion-header" data-category-id="${category.id}">
                ${category.name}
            </div>
            <div class="accordion-content" id="category-${category.id}">
                <div class="website-list">
                    ${category.websites.map(website => `
                        <div class="website-item-mobile" data-url="${website.url}">
                            <h3>${website.name}</h3>
                            <p>${website.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.appendChild(accordion);
    });
    
    // 添加手风琴事件监听
    setupAccordionListeners();
    
    // 为网站卡片添加点击事件
    setupWebsiteClickEvents();
}

// 设置手风琴效果
function setupAccordionListeners() {
    const headers = document.querySelectorAll('.accordion-header');
    headers.forEach(header => {
        header.addEventListener('click', function() {
            const categoryId = this.getAttribute('data-category-id');
            const content = document.getElementById(`category-${categoryId}`);
            
            // 切换当前项的展开/收起状态
            this.classList.toggle('active');
            content.classList.toggle('active');
        });
    });
}

// 设置事件监听器
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const menuButton = document.getElementById('menuButton');
    const sidebarMenu = document.getElementById('sidebarMenu');
    const menuOverlay = document.getElementById('menuOverlay');
    
    // 搜索按钮点击事件
    searchButton.addEventListener('click', performSearch);
    
    // 回车键搜索
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // 菜单按钮点击事件
    menuButton.addEventListener('click', function() {
        sidebarMenu.classList.add('open');
        menuOverlay.classList.add('open');
        document.body.style.overflow = 'hidden'; // 防止背景滚动
    });
    
    // 关闭菜单事件
    function closeMenu() {
        sidebarMenu.classList.remove('open');
        menuOverlay.classList.remove('open');
        document.body.style.overflow = ''; // 恢复背景滚动
    }
    
    // 点击遮罩层关闭菜单
    menuOverlay.addEventListener('click', closeMenu);
    
    // 点击页面其他地方隐藏悬浮菜单
    document.addEventListener('click', function(e) {
        const contextMenu = document.getElementById('context-menu');
        if (contextMenu && !contextMenu.contains(e.target)) {
            contextMenu.classList.remove('visible');
        }
    });
}

// 执行搜索
function performSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    
    if (searchTerm === '') {
        // 如果搜索词为空，显示所有分类
        renderCategories();
        return;
    }
    
    // 过滤网站数据
    const filteredData = websiteData.map(category => {
        const filteredWebsites = category.websites.filter(website => 
            website.name.toLowerCase().includes(searchTerm) || 
            website.description.toLowerCase().includes(searchTerm)
        );
        return {
            ...category,
            websites: filteredWebsites
        };
    }).filter(category => category.websites.length > 0);
    
    // 渲染搜索结果
    renderSearchResults(filteredData);
}

// 渲染搜索结果
function renderSearchResults(data) {
    const container = document.getElementById('categories-container');
    container.innerHTML = '';
    
    if (data.length === 0) {
        container.innerHTML = '<div class="no-results">未找到匹配的网站</div>';
        return;
    }
    
    data.forEach(category => {
        const resultSection = document.createElement('div');
        resultSection.className = 'search-result-section';
        resultSection.innerHTML = `
            <h2 class="result-category">${category.name}</h2>
            <div class="website-list">
                ${category.websites.map(website => `
                    <div class="website-item-mobile" data-url="${website.url}">
                        <h3>${website.name}</h3>
                        <p>${website.description}</p>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(resultSection);
    });
    
    // 为搜索结果中的网站卡片添加点击事件
    setupWebsiteClickEvents();
}

// 设置网站卡片点击事件
function setupWebsiteClickEvents() {
    const websiteItems = document.querySelectorAll('.website-item-mobile');
    websiteItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            showContextMenu(e, url);
        });
    });
    
    // 也为搜索结果中的网站卡片添加右键菜单事件
    const searchResults = document.querySelectorAll('.search-result-section .website-item-mobile');
    searchResults.forEach(item => {
        item.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            showContextMenu(e, url);
        });
        
        // 添加长按触发悬浮菜单的功能（移动端）
        let touchTimer;
        item.addEventListener('touchstart', function(e) {
            const url = this.getAttribute('data-url');
            touchTimer = setTimeout(() => {
                showContextMenu(e, url);
            }, 500); // 长按500ms触发
        });
        
        item.addEventListener('touchend', function() {
            clearTimeout(touchTimer);
        });
        
        item.addEventListener('touchmove', function() {
            clearTimeout(touchTimer);
        });
    });
}

// 设置悬浮菜单
function setupContextMenu() {
    const contextMenu = document.getElementById('context-menu');
    const visitWebsite = document.getElementById('visit-website');
    const copyUrl = document.getElementById('copy-url');
    const openInBrowser = document.getElementById('open-in-browser');
    
    // 访问网站
    visitWebsite.addEventListener('click', function() {
        if (currentWebsiteUrl) {
            window.open(currentWebsiteUrl, '_blank');
        }
        contextMenu.classList.remove('visible');
    });
    
    // 复制网址
    copyUrl.addEventListener('click', function() {
        if (currentWebsiteUrl) {
            navigator.clipboard.writeText(currentWebsiteUrl).then(() => {
                showToast('网址已复制到剪贴板', 'success');
            }).catch(err => {
                console.error('复制失败:', err);
                showToast('复制失败', 'error');
            });
        }
        contextMenu.classList.remove('visible');
    });
    
    // 在浏览器中打开
    openInBrowser.addEventListener('click', function() {
        if (currentWebsiteUrl) {
            window.open(currentWebsiteUrl, '_blank');
        }
        contextMenu.classList.remove('visible');
    });
    
    // 点击页面其他地方隐藏悬浮菜单
    document.addEventListener('click', function(e) {
        if (contextMenu && !contextMenu.contains(e.target)) {
            contextMenu.classList.remove('visible');
        }
    });
}

// 模态框功能
function setupModalSystem() {
    const modalContainer = document.getElementById('modal-container');
    const modalCloseButtons = document.querySelectorAll('.modal-close');
    const menuItems = document.querySelectorAll('.menu-item');
    
    // 为菜单项添加点击事件
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const modalType = this.getAttribute('data-modal');
            if (modalType) {
                openModal(modalType);
            }
        });
    });
    
    // 为模态框关闭按钮添加事件
    modalCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });
    
    // 点击模态框背景关闭模态框
    modalContainer.addEventListener('click', function(e) {
        if (e.target === modalContainer) {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal);
            }
        }
    });
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal);
            }
        }
    });
}

// 打开模态框
function openModal(modalType) {
    const modalContainer = document.getElementById('modal-container');
    const modal = document.getElementById(`${modalType}-modal`);
    
    if (modal) {
        modalContainer.style.display = 'flex';
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // 防止背景滚动
    }
}

// 关闭模态框
function closeModal(modal) {
    const modalContainer = document.getElementById('modal-container');
    
    if (modal) {
        modal.classList.remove('active');
        
        // 检查是否还有其他模态框打开
        const activeModals = document.querySelectorAll('.modal.active');
        if (activeModals.length === 0) {
            modalContainer.style.display = 'none';
            document.body.style.overflow = ''; // 恢复背景滚动
        }
    }
}

// Toast提示功能
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // 添加图标
    let iconClass = '';
    switch (type) {
        case 'success':
            iconClass = 'fas fa-check-circle';
            break;
        case 'error':
            iconClass = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            iconClass = 'fas fa-exclamation-triangle';
            break;
        case 'info':
            iconClass = 'fas fa-info-circle';
            break;
        default:
            iconClass = 'fas fa-info-circle';
    }
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="${iconClass}"></i>
        </div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // 添加关闭按钮事件
    const closeButton = toast.querySelector('.toast-close');
    closeButton.addEventListener('click', function() {
        hideToast(toast);
    });
    
    // 自动隐藏
    setTimeout(() => {
        hideToast(toast);
    }, duration);
}

// 隐藏Toast
function hideToast(toast) {
    if (toast) {
        toast.style.animation = 'toastSlideOut 0.3s ease-out forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// 显示悬浮菜单
function showContextMenu(e, url) {
    e.preventDefault();
    e.stopPropagation();
    
    currentWebsiteUrl = url;
    
    const menu = document.getElementById('context-menu');
    
    // 获取菜单的宽度和高度
    menu.style.visibility = 'hidden';
    menu.classList.add('visible');
    const menuWidth = menu.offsetWidth;
    const menuHeight = menu.offsetHeight;
    menu.classList.remove('visible');
    menu.style.visibility = 'visible';
    
    // 获取视窗尺寸
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // 计算菜单位置
    let left = e.pageX;
    let top = e.pageY;
    
    // 判断右侧空间是否足够，不够则向左展开
    if (left + menuWidth > viewportWidth) {
        left = Math.max(10, left - menuWidth);
    }
    
    // 判断底部空间是否足够，不够则向上展开
    if (top + menuHeight > viewportHeight) {
        top = Math.max(10, top - menuHeight);
    }
    
    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
    menu.classList.add('visible');
}

// 隐藏悬浮菜单
function hideContextMenu() {
    const contextMenu = document.getElementById('context-menu');
    contextMenu.classList.remove('visible');
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            alert('网址已复制到剪贴板');
        }).catch(err => {
            console.error('复制失败:', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

// 降级复制方法
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            alert('网址已复制到剪贴板');
        } else {
            alert('复制失败，请手动复制');
        }
    } catch (err) {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制');
    }
    
    document.body.removeChild(textArea);
}

// 在浏览器中打开
function openInBrowser(url) {
    try {
        // 尝试多种方法在浏览器中打开
        if (navigator.userAgent.includes('MicroMessenger')) {
            // 微信环境
            alert('请在浏览器中打开此链接: ' + url);
        } else if (navigator.userAgent.includes('QQ')) {
            // QQ环境
            alert('请在浏览器中打开此链接: ' + url);
        } else {
            // 其他环境，尝试直接打开
            window.open(url, '_system') || window.open(url, '_blank');
        }
    } catch (e) {
        // 如果上述方法都失败，提示用户手动打开
        alert('请在浏览器中打开此链接: ' + url);
    }
}


// 测试函数 - 用于测试toast功能
function testToast() {
    showToast('这是一条信息提示', 'info');
    setTimeout(() => {
        showToast('这是一条成功提示', 'success');
    }, 1000);
    setTimeout(() => {
        showToast('这是一条警告提示', 'warning');
    }, 2000);
    setTimeout(() => {
        showToast('这是一条错误提示', 'error');
    }, 3000);
}

// 模态框功能测试函数
function testModal() {
    // 可以通过在浏览器控制台中调用openModal('favorites')来测试模态框
    console.log('可以在控制台中调用以下函数测试模态框:');
    console.log('openModal("favorites") - 打开收藏夹模态框');
    console.log('openModal("history") - 打开历史记录模态框');
    console.log('openModal("settings") - 打开设置模态框');
    console.log('openModal("about") - 打开关于模态框');
}

// 测试悬浮菜单功能
function testContextMenu() {
    console.log('测试悬浮菜单功能:');
    console.log('1. 点击任意网站卡片应该显示悬浮菜单');
    console.log('2. 可以在控制台中调用showContextMenu(event, "https://example.com")来测试');
    console.log('3. 移动端长按网站卡片应该显示悬浮菜单');
}
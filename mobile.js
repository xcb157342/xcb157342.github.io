// 移动端网站数据处理
let websiteData = [];
let currentWebsiteUrl = ''; // 存储当前网站的URL

// 页面可见性变化处理函数
function handleVisibilityChange() {
    if (!document.hidden) {
        // 页面变为可见时，重新加载访问历史并渲染dock栏
        renderFavoriteWebsites();
    }
}

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    loadData().then(() => {
        renderCategories();
        renderFavoriteWebsites(); // 渲染我的常去区域
        setupEventListeners();
        setupContextMenu(); // 设置悬浮菜单
        setupModalSystem(); // 设置模态框系统
        
        // 添加页面可见性变化监听器
        document.addEventListener('visibilitychange', handleVisibilityChange);
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
            
            if (!content.classList.contains('active')) {
                // 展开分类
                content.classList.add('active');
                // 为网站卡片添加动画延迟
                setTimeout(() => {
                    const websiteItems = content.querySelectorAll('.website-item-mobile');
                    websiteItems.forEach((item, index) => {
                        // 重置动画类
                        item.classList.remove('card-enter');
                        // 为每个卡片设置不同的延迟时间
                        item.style.animationDelay = `${index * 0.05}s`;
                        // 触发重排
                        void item.offsetWidth;
                        // 添加动画类
                        item.classList.add('card-enter');
                    });
                }, 10);
            } else {
                // 收起分类
                content.classList.remove('active');
                // 移除卡片动画类
                const websiteItems = content.querySelectorAll('.website-item-mobile');
                websiteItems.forEach(item => {
                    item.classList.remove('card-enter');
                });
            }
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
    
    // 为搜索结果中的网站卡片添加动画效果
    setTimeout(() => {
        const websiteItems = container.querySelectorAll('.website-item-mobile');
        websiteItems.forEach((item, index) => {
            // 为每个卡片设置不同的延迟时间
            item.style.animationDelay = `${index * 0.05}s`;
            // 触发重排
            void item.offsetWidth;
            // 添加动画类
            item.classList.add('card-enter');
        });
    }, 10);
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
    const favoriteWebsite = document.getElementById('favorite-website');
    
    // 访问网站
    visitWebsite.addEventListener('click', function() {
        if (currentWebsiteUrl) {
            // 获取网站名称
            let websiteName = '未知网站';
            const websiteElement = document.querySelector(`.website-item-mobile[data-url="${currentWebsiteUrl}"]`);
            if (websiteElement) {
                const titleElement = websiteElement.querySelector('h3');
                if (titleElement) {
                    websiteName = titleElement.textContent;
                }
            }
            
            // 记录访问历史
            recordVisitHistory(currentWebsiteUrl, websiteName);
            
            // 打开网站
            window.open(currentWebsiteUrl, '_blank');
        }
        contextMenu.classList.remove('visible');
    });
    
    // 复制网址
    copyUrl.addEventListener('click', function() {
        if (currentWebsiteUrl) {
            copyToClipboard(currentWebsiteUrl);
        }
        contextMenu.classList.remove('visible');
    });
    
    // 收藏网站
    favoriteWebsite.addEventListener('click', function() {
        if (currentWebsiteUrl) {
            // 获取网站名称（从当前页面的链接元素中获取）
            let websiteName = '未知网站';
            const websiteElement = document.querySelector(`.website-item-mobile[data-url="${currentWebsiteUrl}"]`);
            if (websiteElement) {
                const titleElement = websiteElement.querySelector('h3');
                if (titleElement) {
                    websiteName = titleElement.textContent;
                }
            }
            
            // 从localStorage获取现有的收藏夹数据
            const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
            
            // 检查是否已经收藏
            const isAlreadyFavorited = favorites.some(fav => fav.url === currentWebsiteUrl);
            
            if (isAlreadyFavorited) {
                showToast('该网站已在收藏夹中', 'info');
            } else {
                // 添加到收藏夹
                favorites.push({
                    name: websiteName,
                    url: currentWebsiteUrl,
                    timestamp: new Date().getTime()
                });
                
                // 保存到localStorage
                localStorage.setItem('favorites', JSON.stringify(favorites));
                
                showToast('已添加到收藏夹', 'success');
            }
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

// 关闭侧边栏
function closeSidebar() {
    const sidebarMenu = document.getElementById('sidebarMenu');
    const menuOverlay = document.getElementById('menuOverlay');
    
    if (sidebarMenu) {
        sidebarMenu.classList.remove('active');
    }
    
    if (menuOverlay) {
        menuOverlay.classList.remove('active');
    }
    
    // 恢复背景滚动
    document.body.style.overflow = '';
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
    
    // 为设置界面的按钮添加事件监听器
    setupSettingsButtons();
}

// 设置界面按钮功能
function setupSettingsButtons() {
    // 清除缓存按钮
    const clearCacheBtn = document.getElementById('clear-cache-btn');
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', function() {
            try {
                // 清除所有localStorage缓存
                localStorage.clear();
                showToast('本地缓存已清除', 'success');
                
                // 重新渲染收藏夹和常去网站
                renderFavoriteWebsites();
                updateFavoritesModal();
            } catch (error) {
                console.error('清除缓存时出错:', error);
                showToast('清除缓存失败', 'error');
            }
        });
    }
    
    // 清除所有数据按钮
    const clearDataBtn = document.getElementById('clear-data-btn');
    if (clearDataBtn) {
        clearDataBtn.addEventListener('click', function() {
            try {
                // 确认操作
                if (confirm('确定要清除所有数据吗？这将包括收藏夹和访问历史等所有数据。')) {
                    // 清除所有localStorage数据
                    localStorage.clear();
                    showToast('所有数据已清除', 'success');
                    
                    // 重新渲染收藏夹和常去网站
                    renderFavoriteWebsites();
                    updateFavoritesModal();
                    updateHistoryModal();
                }
            } catch (error) {
                console.error('清除数据时出错:', error);
                showToast('清除数据失败', 'error');
            }
        });
    }
}

// 打开模态框
function openModal(modalType) {
    const modalContainer = document.getElementById('modal-container');
    const modal = document.getElementById(`${modalType}-modal`);
    
    // 先关闭侧边栏
    closeSidebar();
    
    if (modal) {
        modalContainer.style.display = 'flex';
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // 防止背景滚动
        
        // 如果是收藏夹模态框，更新其内容
        if (modalType === 'favorites') {
            updateFavoritesModal();
        }
        // 如果是历史记录模态框，更新其内容
        else if (modalType === 'history') {
            updateHistoryModal();
        }
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

// 更新收藏夹模态框内容
function updateFavoritesModal() {
    const favoritesModal = document.getElementById('favorites-modal');
    const modalBody = favoritesModal.querySelector('.modal-body');
    
    // 从localStorage获取收藏夹数据
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    
    if (favorites.length === 0) {
        modalBody.innerHTML = '<p>暂无收藏网站</p>';
        return;
    }
    
    // 构建收藏夹列表HTML
    let favoritesHTML = '<div class="favorites-list">';
    favorites.forEach((favorite, index) => {
        favoritesHTML += `
            <div class="favorite-item" data-url="${favorite.url}">
                <div class="favorite-item-content">
                    <h3>${favorite.name}</h3>
                    <p>${favorite.url}</p>
                </div>
                <button class="unfavorite-btn" data-index="${index}">&times;</button>
            </div>
        `;
    });
    favoritesHTML += '</div>';
    
    // 更新模态框内容
    modalBody.innerHTML = favoritesHTML;
    
    // 为收藏项添加点击事件（打开网站）
    const favoriteItems = modalBody.querySelectorAll('.favorite-item');
    favoriteItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // 如果点击的是取消收藏按钮，则不打开网站
            if (e.target.classList.contains('unfavorite-btn')) {
                return;
            }
            
            const url = this.getAttribute('data-url');
            if (url) {
                window.open(url, '_blank');
            }
        });
    });
    
    // 为取消收藏按钮添加事件
    const unfavoriteButtons = modalBody.querySelectorAll('.unfavorite-btn');
    unfavoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const index = parseInt(this.getAttribute('data-index'));
            removeFavorite(index);
            
            // 重新更新模态框内容
            updateFavoritesModal();
        });
    });
}

// 更新历史记录模态框内容
function updateHistoryModal() {
    const historyModal = document.getElementById('history-modal');
    const modalBody = historyModal.querySelector('.modal-body');
    
    // 从localStorage获取历史记录数据
    const history = JSON.parse(localStorage.getItem('visitHistory') || '[]');
    
    if (history.length === 0) {
        modalBody.innerHTML = '<p>暂无访问历史</p>';
        return;
    }
    
    // 构建历史记录列表HTML
    let historyHTML = '<div class="history-list">';
    history.forEach((record, index) => {
        // 使用记录中的网站名称，如果没有则尝试从URL中提取
        let siteName = record.name || record.url;
        if (siteName === record.url) {
            try {
                const urlObj = new URL(record.url);
                siteName = urlObj.hostname.replace('www.', '');
            } catch (e) {
                // 如果URL解析失败，使用原始URL
            }
        }
        
        historyHTML += `
            <div class="history-item" data-url="${record.url}">
                <div class="history-item-content">
                    <h3>${siteName}</h3>
                    <div class="visit-time">${record.visitTime}</div>
                    <p>${record.url}</p>
                </div>
            </div>
        `;
    });
    historyHTML += '</div>';
    
    // 更新模态框内容
    modalBody.innerHTML = historyHTML;
    
    // 为历史记录项添加点击事件（打开网站）
    const historyItems = modalBody.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        item.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                // 获取网站名称
                let websiteName = '未知网站';
                const titleElement = this.querySelector('h3');
                if (titleElement) {
                    websiteName = titleElement.textContent;
                }
                
                // 打开网站
                window.open(url, '_blank');
            }
        });
    });
}

// 从收藏夹中移除网站
function removeFavorite(index) {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    favorites.splice(index, 1);
    localStorage.setItem('favorites', JSON.stringify(favorites));
    showToast('已取消收藏', 'success');
}

// 记录网站访问历史
function recordVisitHistory(url, name) {
    try {
        // 从localStorage获取现有的历史记录数据
        const history = JSON.parse(localStorage.getItem('visitHistory') || '[]');
        
        // 创建新的历史记录项
        const newRecord = {
            url: url,
            name: name,
            timestamp: new Date().getTime(),
            visitTime: new Date().toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            })
        };
        
        // 检查是否已经存在相同的URL记录
        const existingIndex = history.findIndex(record => record.url === url);
        
        if (existingIndex !== -1) {
            // 如果存在，更新时间并将其移到数组开头
            history.splice(existingIndex, 1);
            history.unshift(newRecord);
        } else {
            // 如果不存在，添加到数组开头
            history.unshift(newRecord);
        }
        
        // 限制历史记录数量，最多保留100条记录
        if (history.length > 100) {
            history.splice(100);
        }
        
        // 保存到localStorage
        localStorage.setItem('visitHistory', JSON.stringify(history));
        
        // 更新dock栏显示
        renderFavoriteWebsites();
    } catch (error) {
        console.error('记录访问历史时出错:', error);
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

// 获取网站图标
function getWebsiteIcon(url) {
    // 尝试获取网站的favicon
    try {
        const domain = new URL(url).origin;
        return `${domain}/favicon.ico`;
    } catch (e) {
        // 如果解析URL失败，返回默认图标
        return null;
    }
}

// 渲染我的常去区域
function renderFavoriteWebsites() {
    const favoritesContainer = document.getElementById('favorites-container');
    if (!favoritesContainer) return;
    
    try {
        // 从localStorage获取访问历史
        const history = JSON.parse(localStorage.getItem('visitHistory') || '[]');
        
        // 统计访问次数，按访问次数排序
        const visitCount = {};
        history.forEach(item => {
            visitCount[item.url] = (visitCount[item.url] || 0) + 1;
        });
        
        // 转换为数组并按访问次数排序
        const sortedWebsites = Object.entries(visitCount)
            .map(([url, count]) => ({ url, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 4); // 只取前4个
        
        // 获取favorites-section元素
        const favoritesSection = document.getElementById('favorites-section');
        
        // 如果没有访问历史，隐藏dock栏
        if (sortedWebsites.length === 0) {
            if (favoritesSection) {
                favoritesSection.style.display = 'none';
            }
            return;
        }
        
        // 显示dock栏
        if (favoritesSection) {
            favoritesSection.style.display = 'block';
        }
        
        // 渲染常去网站
        favoritesContainer.innerHTML = '';
        sortedWebsites.forEach(item => {
            // 查找网站信息
            let websiteInfo = null;
            for (const category of websiteData) {
                const website = category.websites.find(w => w.url === item.url);
                if (website) {
                    websiteInfo = website;
                    break;
                }
            }
            
            // 如果找不到网站信息，创建一个默认的
            if (!websiteInfo) {
                try {
                    websiteInfo = {
                        name: new URL(item.url).hostname,
                        url: item.url
                    };
                } catch (e) {
                    websiteInfo = {
                        name: item.url,
                        url: item.url
                    };
                }
            }
            
            const dockItem = document.createElement('div');
            dockItem.className = 'dock-item';
            dockItem.setAttribute('data-url', item.url);
            
            // 先创建带有默认图标的HTML
            dockItem.innerHTML = `
                <div class="website-icon">
                    <i class="fas fa-globe"></i>
                </div>
                <div class="website-name" title="${websiteInfo.name}">${websiteInfo.name}</div>
            `;
            
            favoritesContainer.appendChild(dockItem);
            
            // 然后尝试获取网站真实图标并替换
            const iconUrl = getWebsiteIcon(item.url);
            if (iconUrl) {
                const iconContainer = dockItem.querySelector('.website-icon');
                const img = document.createElement('img');
                img.src = iconUrl;
                img.alt = websiteInfo.name;
                img.onload = function() {
                    // 只有在图片加载成功时才替换
                    iconContainer.innerHTML = '';
                    iconContainer.appendChild(img);
                };
                img.onerror = function() {
                    // 如果图片加载失败，保留默认图标
                    console.log('图标加载失败:', iconUrl);
                };
            }
        });
        
        // 设置常去网站点击事件
        setupFavoriteClickEvents();
    } catch (error) {
        console.error('渲染常去网站区域时出错:', error);
        // 如果出错，隐藏dock栏
        const favoritesSection = document.getElementById('favorites-section');
        if (favoritesSection) {
            favoritesSection.style.display = 'none';
        }
    }
}

// 设置常去网站点击事件
function setupFavoriteClickEvents() {
    const dockItems = document.querySelectorAll('.dock-item');
    dockItems.forEach(item => {
        item.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                // 记录访问历史
                const websiteName = this.querySelector('.website-name').textContent;
                recordVisitHistory(url, websiteName);
                
                // 打开网站
                window.open(url, '_blank');
            }
        });
    });
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
async function copyToClipboard(text) {
    try {
        // 首先尝试使用现代Clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            showToast('网址已复制到剪贴板', 'success');
            return true;
        }
    } catch (err) {
        console.error('现代Clipboard API复制失败:', err);
    }
    
    // 如果现代API失败，尝试降级方法
    return fallbackCopyTextToClipboard(text);
}

// 降级复制方法
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    // 防止滚动到底部
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast('网址已复制到剪贴板', 'success');
            return true;
        } else {
            showToast('复制失败，请手动复制', 'error');
            return false;
        }
    } catch (err) {
        console.error('复制失败:', err);
        showToast('复制失败，请手动复制', 'error');
        return false;
    } finally {
        document.body.removeChild(textArea);
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
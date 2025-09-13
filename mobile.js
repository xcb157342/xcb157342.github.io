// 移动端网站数据处理
let websiteData = [];
let currentWebsiteUrl = ''; // 存储当前网站的URL

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    loadData().then(() => {
        renderCategories();
        setupEventListeners();
        setupContextMenu(); // 设置悬浮菜单
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
    const closeBtn = document.querySelector('.close-btn');
    
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
    
    // 点击关闭按钮关闭菜单
    closeBtn.addEventListener('click', closeMenu);
    
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
}

// 设置悬浮菜单
function setupContextMenu() {
    // 为所有网站卡片添加点击事件
    document.addEventListener('click', function(e) {
        // 检查是否点击了网站卡片
        const websiteItem = e.target.closest('.website-item-mobile');
        if (websiteItem) {
            const url = websiteItem.getAttribute('data-url');
            if (url) {
                showContextMenu(e, url);
            }
        }
    });
    
    // 为悬浮菜单项添加点击事件
    document.getElementById('visit-website').addEventListener('click', function() {
        if (currentWebsiteUrl) {
            window.open(currentWebsiteUrl, '_blank');
            hideContextMenu();
        }
    });
    
    document.getElementById('copy-url').addEventListener('click', function() {
        if (currentWebsiteUrl) {
            copyToClipboard(currentWebsiteUrl);
            hideContextMenu();
        }
    });
    
    document.getElementById('open-in-browser').addEventListener('click', function() {
        if (currentWebsiteUrl) {
            // 尝试使用不同的方法在浏览器中打开
            openInBrowser(currentWebsiteUrl);
            hideContextMenu();
        }
    });
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
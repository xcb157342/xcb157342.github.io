// 网站数据（从data.json加载）
let websiteData = [];

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    loadData().then(() => {
        renderCategories();
        setupEventListeners();
    });
});

// 加载数据
async function loadData() {
    try {
        const response = await fetch('data.json');
        const data = await response.json();
        // 转换数据格式以匹配现有代码
        websiteData = data.categories.map(category => ({
            id: category.id,
            category: category.name,
            websites: category.websites
        }));
    } catch (error) {
        console.error('加载数据失败:', error);
        // 如果加载失败，使用默认数据
        websiteData = [
            {
                id: 1,
                category: "学习资源",
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
                ${category.category}
            </div>
            <div class="accordion-content" id="category-${category.id}">
                <div class="website-grid">
                    ${category.websites.map(website => `
                        <div class="website-card">
                            <h3>${website.name}</h3>
                            <p>${website.description}</p>
                            <a href="${website.url}" target="_blank" class="visit-button">访问网站</a>
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
    
    // 搜索按钮点击事件
    searchButton.addEventListener('click', performSearch);
    
    // 回车键搜索
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
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
            <h2 class="result-category">${category.category}</h2>
            <div class="website-grid">
                ${category.websites.map(website => `
                    <div class="website-card">
                        <h3>${website.name}</h3>
                        <p>${website.description}</p>
                        <a href="${website.url}" target="_blank" class="visit-button">访问网站</a>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(resultSection);
    });
}
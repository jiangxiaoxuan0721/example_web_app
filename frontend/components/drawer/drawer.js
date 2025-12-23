// 抽屉组件
class Drawer {
    constructor(options = {}) {
        this.options = {
            size: 'default', // small, default, large, full
            direction: 'right', // left, right
            closable: true,
            maskClosable: true,
            showFooter: false,
            ...options
        };
        
        this.isOpen = false;
        this.overlay = null;
        this.drawer = null;
        this.content = null;
        
        this.init();
    }

    init() {
        this.createElements();
        this.bindEvents();
    }

    createElements() {
        // 创建遮罩层
        this.overlay = document.createElement('div');
        this.overlay.className = 'drawer-overlay';
        
        // 创建抽屉
        this.drawer = document.createElement('div');
        this.drawer.className = `drawer ${this.options.size} ${this.options.direction}`;
        
        // 创建抽屉内容
        this.drawer.innerHTML = `
            <div class="drawer-header">
                <div>
                    <h3 class="drawer-title">${this.options.title || ''}</h3>
                    ${this.options.subtitle ? `<div class="drawer-subtitle">${this.options.subtitle}</div>` : ''}
                </div>
                <div class="drawer-actions">
                    ${this.options.headerActions || ''}
                    ${this.options.closable ? '<button class="drawer-close" aria-label="关闭">×</button>' : ''}
                </div>
            </div>
            <div class="drawer-body">
                ${this.options.content || ''}
            </div>
            ${this.options.showFooter ? `
                <div class="drawer-footer">
                    ${this.options.footerActions || ''}
                </div>
            ` : ''}
        `;
        
        // 获取内容容器
        this.content = this.drawer.querySelector('.drawer-body');
        
        // 添加到页面
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.drawer);
    }

    bindEvents() {
        // 关闭按钮事件
        const closeBtn = this.drawer.querySelector('.drawer-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        // 遮罩层点击事件
        if (this.options.maskClosable) {
            this.overlay.addEventListener('click', () => this.close());
        }
        
        // ESC键关闭
        this.handleKeydown = (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        };
        document.addEventListener('keydown', this.handleKeydown);
        
        // 阻止抽屉内部点击事件冒泡
        this.drawer.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    open() {
        if (this.isOpen) return;
        
        this.isOpen = true;
        
        // 直接设置样式，确保显示
        this.overlay.style.display = 'block';
        this.overlay.style.opacity = '1';
        this.drawer.style.right = '0px';
        
        // 添加类名
        this.overlay.classList.add('open');
        this.drawer.classList.add('open');
        
        // 禁止页面滚动
        document.body.style.overflow = 'hidden';
        
        // 触发打开事件
        if (this.options.onOpen) {
            this.options.onOpen();
        }
    }

    close() {
        if (!this.isOpen) return;
        
        this.isOpen = false;
        
        // 移除类名
        this.overlay.classList.remove('open');
        this.drawer.classList.remove('open');
        
        // 等待动画完成后隐藏
        setTimeout(() => {
            this.overlay.style.display = 'none';
        }, 300);
        
        // 恢复页面滚动
        document.body.style.overflow = '';
        
        // 触发关闭事件
        if (this.options.onClose) {
            this.options.onClose();
        }
    }

    setContent(content) {
        if (this.content) {
            this.content.innerHTML = content;
        }
    }

    appendContent(content) {
        if (this.content) {
            this.content.innerHTML += content;
        }
    }

    setTitle(title) {
        const titleElement = this.drawer.querySelector('.drawer-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
    }

    setSubtitle(subtitle) {
        const subtitleElement = this.drawer.querySelector('.drawer-subtitle');
        if (subtitleElement) {
            subtitleElement.innerHTML = subtitle;
        } else if (subtitle) {
            const titleElement = this.drawer.querySelector('.drawer-title');
            if (titleElement) {
                const subtitleDiv = document.createElement('div');
                subtitleDiv.className = 'drawer-subtitle';
                subtitleDiv.innerHTML = subtitle;
                titleElement.parentNode.insertBefore(subtitleDiv, titleElement.nextSibling);
            }
        }
    }

    showLoading() {
        this.drawer.classList.add('loading');
    }

    hideLoading() {
        this.drawer.classList.remove('loading');
    }

    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
        
        // 更新尺寸
        this.drawer.className = `drawer ${this.options.size} ${this.options.direction} ${this.isOpen ? 'open' : ''}`;
        
        // 更新标题
        if (newOptions.title !== undefined) {
            this.setTitle(newOptions.title);
        }
        
        if (newOptions.subtitle !== undefined) {
            this.setSubtitle(newOptions.subtitle);
        }
        
        // 更新内容
        if (newOptions.content !== undefined) {
            this.setContent(newOptions.content);
        }
    }
    
    // 添加图片到抽屉
    addPicture(options = {}) {
        // 确保pictureManager已加载
        if (typeof pictureManager === 'undefined') {
            console.error('pictureManager未加载，请确保已引入picture.js');
            return;
        }
        
        // 创建唯一ID
        const pictureId = options.id || `picture-${Math.random().toString(36).substr(2, 9)}`;
        
        // 确定目标容器
        let targetContainer = options.appendTo;
        if (!targetContainer) {
            // 如果没有指定容器，则添加到抽屉内容中
            const pictureHtml = Drawer.createPictureContainer(pictureId, options);
            this.appendContent(pictureHtml);
            targetContainer = this.drawer.querySelector(`#${pictureId}`);
        }
        
        // 等待DOM更新后初始化图片组件
        setTimeout(() => {
            if (targetContainer && typeof pictureManager !== 'undefined') {
                // 如果是选择器字符串，则获取DOM元素
                if (typeof targetContainer === 'string') {
                    targetContainer = document.querySelector(targetContainer);
                }
                
                if (targetContainer) {
                    // 如果是直接添加到指定容器中，创建容器并追加
                    if (options.appendTo && typeof options.appendTo !== 'string') {
                        const pictureHtml = Drawer.createPictureContainer(pictureId, options);
                        // 创建一个临时div来解析HTML
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = pictureHtml;
                        // 追加到目标容器
                        targetContainer.appendChild(tempDiv.firstElementChild);
                        // 获取新添加的容器
                        targetContainer = targetContainer.querySelector(`#${pictureId}`);
                    }
                    
                    // 创建picture组件
                    pictureManager.create(pictureId, {
                        source: options.source || '',
                        title: options.title || '',
                        subtitle: options.subtitle || '',
                        width: '100%',
                        height: options.height || '300px',
                        fit: options.fit || 'contain',
                        showFullscreen: options.showFullscreen !== false,
                        showDownload: options.showDownload !== false,
                        appendTo: targetContainer,
                        onLoad: options.onLoad,
                        onError: options.onError
                    });
                }
            }
        }, 0);
    }

    destroy() {
        this.close();
        
        // 移除事件监听
        document.removeEventListener('keydown', this.handleKeydown);
        
        // 移除DOM元素
        if (this.overlay) {
            this.overlay.remove();
        }
        if (this.drawer) {
            this.drawer.remove();
        }
    }

    // 静态方法：创建信息展示区域
    static createInfoSection(title, items, options = {}) {
        const singleColumn = options.singleColumn || false;
        const gridClass = singleColumn ? 'info-grid single-column' : 'info-grid';
        
        const itemsHtml = items.map(item => `
            <div class="info-item">
                <label>${item.label}</label>
                <span class="${item.highlight ? 'value-highlight' : ''}">${item.value || '--'}</span>
            </div>
        `).join('');
        
        return `
            <div class="drawer-section">
                <h4 class="drawer-section-title">${title}</h4>
                ${options.subtitle ? `<div class="drawer-section-subtitle">${options.subtitle}</div>` : ''}
                <div class="${gridClass}">
                    ${itemsHtml}
                </div>
            </div>
        `;
    }

    // 静态方法：创建状态指示器
    static createStatusIndicator(text, type = 'info') {
        return `
            <div class="status-indicator ${type}">
                <span class="status-dot"></span>
                ${text}
            </div>
        `;
    }

    // 静态方法：创建时间线
    static createTimeline(items) {
        const itemsHtml = items.map(item => `
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-time">${item.time}</div>
                    <div class="timeline-text">${item.text}</div>
                </div>
            </div>
        `).join('');
        
        return `
            <div class="drawer-section">
                <h4 class="drawer-section-title">时间线</h4>
                <div class="drawer-timeline">
                    ${itemsHtml}
                </div>
            </div>
        `;
    }

    // 静态方法：创建图表容器
    static createChartContainer(title, chartId, options = {}) {
        return `
            <div class="drawer-section">
                <h4 class="drawer-section-title">${title}</h4>
                ${options.subtitle ? `<div class="drawer-section-subtitle">${options.subtitle}</div>` : ''}
                <div class="chart-container" style="height: ${options.height || '300px'};">
                    <canvas id="${chartId}"></canvas>
                </div>
            </div>
        `;
    }
    
    // 静态方法：创建图片容器
    static createPictureContainer(id, options = {}) {
        const pictureId = id || `picture-${Math.random().toString(36).substr(2, 9)}`;
        return `
            <div class="drawer-section">
                <div id="${pictureId}" class="drawer-picture-container"></div>
            </div>
        `;
    }
}

// 全局抽屉实例管理
const drawerManager = {
    instances: new Map(),
    
    create(id, options) {
        const drawer = new Drawer(options);
        this.instances.set(id, drawer);
        return drawer;
    },
    
    get(id) {
        return this.instances.get(id);
    },
    
    close(id) {
        const drawer = this.instances.get(id);
        if (drawer) {
            drawer.close();
        }
    },
    
    closeAll() {
        this.instances.forEach(drawer => drawer.close());
    },
    
    destroy(id) {
        const drawer = this.instances.get(id);
        if (drawer) {
            drawer.destroy();
            this.instances.delete(id);
        }
    },
    
    destroyAll() {
        this.instances.forEach(drawer => drawer.destroy());
        this.instances.clear();
    }
};

// 示例使用
/*
const drawer = drawerManager.create('detail-drawer', {
    title: '详细信息',
    subtitle: 'Case ID: CASE_001',
    size: 'default',
    content: `
        ${Drawer.createInfoSection('基本信息', [
            { label: '设备ID', value: 'TRANSFORMER_001' },
            { label: '故障类型', value: 'N-1', highlight: true },
            { label: '最低电压', value: '0.95 p.u.' },
            { label: '最大频偏', value: '0.2 Hz' }
        ])}
        ${Drawer.createStatusIndicator('系统稳定', 'success')}
    `,
    showFooter: true,
    footerActions: `
        <button class="btn btn-secondary" onclick="drawerManager.close('detail-drawer')">关闭</button>
        <button class="btn btn-primary">导出报告</button>
    `,
    onOpen: () => console.log('Drawer opened'),
    onClose: () => console.log('Drawer closed')
});

drawer.open();
*/
// 图片组件
class Picture {
    constructor(options = {}) {
        this.options = {
            source: '', // 图片URL、链接或base64数据
            title: '', // 图片标题
            subtitle: '', // 图片副标题
            width: '100%', // 图片宽度
            height: 'auto', // 图片高度
            fit: 'contain', // 图片适应方式: contain, cover, fill, none, scale-down
            lazy: false, // 是否懒加载
            fallback: '', // 加载失败时的备用图片
            alt: '', // 图片alt属性
            showFullscreen: true, // 是否显示全屏按钮
            showDownload: true, // 是否显示下载按钮
            ...options
        };
        
        this.container = null;
        this.image = null;
        this.loadingIndicator = null;
        this.errorIndicator = null;
        this.isLoaded = false;
        this.hasError = false;
        
        this.init();
    }

    init() {
        this.createElements();
        this.bindEvents();
        this.loadImage();
    }

    createElements() {
        // 创建容器
        this.container = document.createElement('div');
        this.container.className = 'picture-container';
        this.container.style.width = this.options.width;
        
        // 创建标题区域
        if (this.options.title) {
            const header = document.createElement('div');
            header.className = 'picture-header';
            header.innerHTML = `
                <h3 class="picture-title">${this.options.title}</h3>
                ${this.options.subtitle ? `<div class="picture-subtitle">${this.options.subtitle}</div>` : ''}
            `;
            this.container.appendChild(header);
        }
        
        // 创建图片包装器
        const wrapper = document.createElement('div');
        wrapper.className = 'picture-wrapper';
        wrapper.style.height = this.options.height;
        
        // 创建图片元素
        this.image = document.createElement(this.isHtmlLink() ? 'iframe' : 'img');
        this.image.className = 'picture-image';
        this.image.alt = this.options.alt || this.options.title;
        
        if (this.isHtmlLink()) {
            // 为iframe创建一个容器以保持宽高比
            const iframeWrapper = document.createElement('div');
            iframeWrapper.className = 'iframe-wrapper';
            iframeWrapper.style.position = 'relative';
            iframeWrapper.style.width = '100%';
            iframeWrapper.style.paddingTop = '56.25%'; // 16:9宽高比
            iframeWrapper.style.overflow = 'hidden';
            
            // 设置iframe样式
            this.image.src = this.options.source;
            this.image.style.position = 'absolute';
            this.image.style.top = '0';
            this.image.style.left = '0';
            this.image.style.width = '100%';
            this.image.style.height = '100%';
            this.image.style.border = 'none';
            this.image.style.borderRadius = '4px';
            
            // 将iframe添加到包装器中
            iframeWrapper.appendChild(this.image);
            
            // 保存iframe包装器引用
            this.iframeWrapper = iframeWrapper;
        } else {
            this.image.style.objectFit = this.options.fit;
            if (this.options.lazy) {
                this.image.loading = 'lazy';
            }
        }
        
        // 创建加载指示器
        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'picture-loading';
        this.loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
        `;
        
        // 创建错误指示器
        this.errorIndicator = document.createElement('div');
        this.errorIndicator.className = 'picture-error';
        this.errorIndicator.style.display = 'none';
        this.errorIndicator.innerHTML = `
            <div class="error-icon">⚠</div>
            <div class="error-text">图片加载失败</div>
            ${this.options.fallback ? '<button class="retry-btn">重试</button>' : ''}
        `;
        
        // 创建工具栏
        const toolbar = document.createElement('div');
        toolbar.className = 'picture-toolbar';
        toolbar.style.display = 'none';
        
        let toolbarButtons = '';
        if (this.options.showFullscreen && !this.isHtmlLink()) {
            toolbarButtons += '<button class="toolbar-btn fullscreen-btn" title="全屏查看">⛶</button>';
        }
        if (this.options.showDownload) {
            toolbarButtons += `<button class="toolbar-btn download-btn" title="下载">↓</button>`;
        }
        
        toolbar.innerHTML = toolbarButtons;
        
        // 组装元素
        if (this.iframeWrapper) {
            wrapper.appendChild(this.iframeWrapper);
        } else {
            wrapper.appendChild(this.image);
        }
        wrapper.appendChild(this.loadingIndicator);
        wrapper.appendChild(this.errorIndicator);
        wrapper.appendChild(toolbar);
        
        this.container.appendChild(wrapper);
        
        // 添加到页面
        if (this.options.appendTo) {
            this.options.appendTo.appendChild(this.container);
        }
    }

    bindEvents() {
        if (this.isHtmlLink()) {
            // iframe加载成功事件
            this.image.addEventListener('load', () => {
                this.isLoaded = true;
                this.loadingIndicator.style.display = 'none';
                this.container.classList.add('loaded');
                
                if (this.options.onLoad) {
                    this.options.onLoad(this.image);
                }
            });
            
            // iframe加载失败事件
            this.image.addEventListener('error', () => {
                this.hasError = true;
                this.loadingIndicator.style.display = 'none';
                this.errorIndicator.style.display = 'flex';
                
                if (this.options.onError) {
                    this.options.onError();
                }
            });
        } else {
            // 图片加载成功事件
            this.image.addEventListener('load', () => {
                this.isLoaded = true;
                this.loadingIndicator.style.display = 'none';
                this.container.classList.add('loaded');
                
                if (this.options.onLoad) {
                    this.options.onLoad(this.image);
                }
            });
            
            // 图片加载失败事件
            this.image.addEventListener('error', () => {
                this.hasError = true;
                this.loadingIndicator.style.display = 'none';
                this.errorIndicator.style.display = 'flex';
                
                if (this.options.fallback && !this.isHtmlLink()) {
                    this.image.src = this.options.fallback;
                }
                
                if (this.options.onError) {
                    this.options.onError();
                }
            });
        }
        
        // 重试按钮事件
        const retryBtn = this.errorIndicator.querySelector('.retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                this.errorIndicator.style.display = 'none';
                this.loadingIndicator.style.display = 'flex';
                this.loadImage();
            });
        }
        
        // 图片点击事件 - 80%全屏显示
        if (!this.isHtmlLink()) {
            this.image.addEventListener('click', () => {
                if (this.isLoaded && !this.hasError) {
                    this.openPartialFullscreen();
                }
            });
            // 添加点击样式提示
            this.image.style.cursor = 'pointer';
        }
        
        // 全屏按钮事件
        const fullscreenBtn = this.container.querySelector('.fullscreen-btn');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => {
                this.openFullscreen();
            });
        }
        
        // 下载按钮事件
        const downloadBtn = this.container.querySelector('.download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.download();
            });
        }
        
        // 鼠标悬停显示工具栏
        if (this.options.showFullscreen || this.options.showDownload) {
            this.container.addEventListener('mouseenter', () => {
                if (this.isLoaded && !this.hasError) {
                    toolbar.style.display = 'flex';
                }
            });
            
            this.container.addEventListener('mouseleave', () => {
                toolbar.style.display = 'none';
            });
        }
    }

    loadImage() {
        // 不论是img还是iframe，都需要设置src
        // 在createElements中已经设置了，但这里确保重新加载时也能正确设置
        if (this.image && this.options.source) {
            this.image.src = this.options.source;
        }
    }

    isHtmlLink() {
        if (!this.options.source) return false;
        return /\.(html?)(\?.*)?$/i.test(this.options.source) || 
               this.options.source.includes('wave_') && this.options.source.includes('.html');
    }

    openFullscreen() {
        if (this.hasError || this.isHtmlLink()) return;
        
        const modal = document.createElement('div');
        modal.className = 'picture-fullscreen-modal';
        
        const modalImg = document.createElement('img');
        modalImg.className = 'fullscreen-image';
        modalImg.src = this.image.src;
        modalImg.alt = this.options.alt || this.options.title;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'fullscreen-close';
        closeBtn.innerHTML = '×';
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.appendChild(modalImg);
        modal.appendChild(closeBtn);
        document.body.appendChild(modal);
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        // ESC键关闭
        const handleKeydown = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', handleKeydown);
            }
        };
        document.addEventListener('keydown', handleKeydown);
    }

    openPartialFullscreen() {
        if (this.hasError || this.isHtmlLink()) return;
        
        const modal = document.createElement('div');
        modal.className = 'picture-partial-fullscreen-modal';
        
        const modalImg = document.createElement('img');
        modalImg.className = 'partial-fullscreen-image';
        modalImg.src = this.image.src;
        modalImg.alt = this.options.alt || this.options.title;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'partial-fullscreen-close';
        closeBtn.innerHTML = '×';
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.appendChild(modalImg);
        modal.appendChild(closeBtn);
        document.body.appendChild(modal);
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        // ESC键关闭
        const handleKeydown = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', handleKeydown);
            }
        };
        document.addEventListener('keydown', handleKeydown);
    }

    download() {
        if (this.hasError) return;
        
        if (this.isHtmlLink()) {
            // 对于HTML链接，直接在新窗口打开
            window.open(this.options.source, '_blank');
            return;
        }
        
        // 创建下载链接
        const link = document.createElement('a');
        link.href = this.image.src;
        link.download = this.options.title || 'image';
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    updateSource(source) {
        this.options.source = source;
        this.isLoaded = false;
        this.hasError = false;
        this.loadingIndicator.style.display = 'flex';
        this.errorIndicator.style.display = 'none';
        
        // 重新创建元素（如果类型从img变为iframe或反之）
        const oldImage = this.image;
        const wrapper = this.image.parentElement;
        
        // 如果存在旧的iframe包装器，移除它
        if (this.iframeWrapper && this.iframeWrapper.parentElement) {
            this.iframeWrapper.parentElement.removeChild(this.iframeWrapper);
            this.iframeWrapper = null;
        }
        
        this.image = document.createElement(this.isHtmlLink() ? 'iframe' : 'img');
        this.image.className = 'picture-image';
        this.image.alt = this.options.alt || this.options.title;
        
        // 为新创建的元素添加事件监听
        const bindImageEvents = () => {
            if (this.isHtmlLink()) {
                // iframe加载成功事件
                this.image.addEventListener('load', () => {
                    this.isLoaded = true;
                    this.loadingIndicator.style.display = 'none';
                    this.container.classList.add('loaded');
                    
                    if (this.options.onLoad) {
                        this.options.onLoad(this.image);
                    }
                });
                
                // iframe加载失败事件
                this.image.addEventListener('error', () => {
                    this.hasError = true;
                    this.loadingIndicator.style.display = 'none';
                    this.errorIndicator.style.display = 'flex';
                    
                    if (this.options.onError) {
                        this.options.onError();
                    }
                });
            } else {
                // 图片加载成功事件
                this.image.addEventListener('load', () => {
                    this.isLoaded = true;
                    this.loadingIndicator.style.display = 'none';
                    this.container.classList.add('loaded');
                    
                    if (this.options.onLoad) {
                        this.options.onLoad(this.image);
                    }
                });
                
                // 图片加载失败事件
                this.image.addEventListener('error', () => {
                    this.hasError = true;
                    this.loadingIndicator.style.display = 'none';
                    this.errorIndicator.style.display = 'flex';
                });
            }
        };

        if (this.isHtmlLink()) {
            // 为iframe创建一个容器以保持宽高比
            const iframeWrapper = document.createElement('div');
            iframeWrapper.className = 'iframe-wrapper';
            iframeWrapper.style.position = 'relative';
            iframeWrapper.style.width = '100%';
            iframeWrapper.style.paddingTop = '56.25%'; // 16:9宽高比
            iframeWrapper.style.overflow = 'hidden';
            
            // 设置iframe样式
            this.image.src = this.options.source;
            this.image.style.position = 'absolute';
            this.image.style.top = '0';
            this.image.style.left = '0';
            this.image.style.width = '100%';
            this.image.style.height = '100%';
            this.image.style.border = 'none';
            this.image.style.borderRadius = '4px';
            
            // 将iframe添加到包装器中
            iframeWrapper.appendChild(this.image);
            
            // 保存iframe包装器引用
            this.iframeWrapper = iframeWrapper;
            
            // 替换元素
            wrapper.replaceChild(iframeWrapper, oldImage);
        } else {
            this.image.style.objectFit = this.options.fit;
            if (this.options.lazy) {
                this.image.loading = 'lazy';
            }
            
            // 替换元素
            wrapper.replaceChild(this.image, oldImage);
        }
        
        bindImageEvents();
        this.loadImage();
    }

    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }

    // 静态方法：创建图片画廊
    static createGallery(images, options = {}) {
        const gallery = document.createElement('div');
        gallery.className = 'picture-gallery';
        
        const imageElements = images.map((img, index) => {
            const picture = new Picture({
                source: img.source,
                title: img.title,
                alt: img.alt,
                width: options.itemWidth || '100%',
                height: options.itemHeight || '200px',
                fit: options.fit || 'cover',
                onClick: () => {
                    if (options.onImageClick) {
                        options.onImageClick(img, index);
                    }
                }
            });
            
            // 添加点击事件
            picture.container.classList.add('gallery-item');
            picture.container.style.cursor = 'pointer';
            
            return picture.container;
        });
        
        imageElements.forEach(el => gallery.appendChild(el));
        
        return gallery;
    }
}

// 全局图片管理器
const pictureManager = {
    instances: new Map(),
    
    create(id, options) {
        const picture = new Picture(options);
        this.instances.set(id, picture);
        return picture;
    },
    
    get(id) {
        return this.instances.get(id);
    },
    
    destroy(id) {
        const picture = this.instances.get(id);
        if (picture) {
            picture.destroy();
            this.instances.delete(id);
        }
    },
    
    destroyAll() {
        this.instances.forEach(picture => picture.destroy());
        this.instances.clear();
    }
};
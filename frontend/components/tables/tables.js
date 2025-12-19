// 表格组件
class DataTable {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            columns: [],
            data: [],
            searchable: true,
            paginated: true,
            pageSize: 10,
            selectable: true,
            sortable: true,
            ...options
        };
        
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.selectedRows = new Set();
        this.filteredData = [];
        
        this.init();
    }

    init() {
        this.render();
        this.bindEvents();
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="table-container">
                ${this.renderToolbar()}
                <div class="table-wrapper">
                    <table class="data-table">
                        <thead>${this.renderHeader()}</thead>
                        <tbody>${this.renderBody()}</tbody>
                    </table>
                </div>
                ${this.renderPagination()}
            </div>
        `;
    }

    renderToolbar() {
        if (!this.options.searchable && !this.options.toolbarActions) return '';
        
        return `
            <div class="table-toolbar">
                ${this.options.searchable ? `
                    <input type="text" class="table-search" placeholder="搜索..." 
                           onkeyup="dataTableInstance.handleSearch(this.value)">
                ` : ''}
                ${this.options.toolbarActions || ''}
            </div>
        `;
    }

    renderHeader() {
        const headers = this.options.columns.map(col => `
            <th style="width: ${col.width || 'auto'}" 
                data-column="${col.key}"
                onclick="dataTableInstance.handleSort('${col.key}')">
                ${col.title}
                ${this.options.sortable ? `
                    <span class="sort-indicator ${this.sortColumn === col.key ? this.sortDirection : ''}">
                        ${this.sortColumn === col.key ? (this.sortDirection === 'asc' ? '↑' : '↓') : '↕'}
                    </span>
                ` : ''}
            </th>
        `).join('');
        
        return `<tr>${headers}</tr>`;
    }

    renderBody() {
        const data = this.getPaginatedData();
        
        if (data.length === 0) {
            return `
                <tr>
                    <td colspan="${this.options.columns.length}" class="table-empty">
                        <div class="table-empty-icon">📋</div>
                        <div class="table-empty-text">暂无数据</div>
                        <div class="table-empty-desc">请检查数据源或调整筛选条件</div>
                    </td>
                </tr>
            `;
        }
        
        return data.map((row, index) => `
            <tr data-index="${this.getOriginalIndex(index)}" 
                class="${this.selectedRows.has(this.getOriginalIndex(index)) ? 'selected' : ''}"
                onclick="dataTableInstance.handleRowClick(${this.getOriginalIndex(index)})">
                ${this.options.columns.map(col => `
                    <td>${this.renderCell(row, col)}</td>
                `).join('')}
            </tr>
        `).join('');
    }

    renderCell(row, column) {
        const value = row[column.key];
        
        if (column.render) {
            return column.render(value, row);
        }
        
        if (column.type === 'tag') {
            const tagClass = this.getTagClass(value);
            return `<span class="table-tag ${tagClass}">${value}</span>`;
        }
        
        if (column.type === 'number') {
            return typeof value === 'number' ? value.toLocaleString() : value;
        }
        
        return value || '-';
    }

    getTagClass(value) {
        const tagMap = {
            '正常': 'table-tag-success',
            '异常': 'table-tag-error',
            '警告': 'table-tag-warning',
            '稳定': 'table-tag-success',
            '失稳': 'table-tag-error',
            '越限': 'table-tag-warning'
        };
        return tagMap[value] || 'table-tag-info';
    }

    renderPagination() {
        if (!this.options.paginated) return '';
        
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        const startItem = (this.currentPage - 1) * this.options.pageSize + 1;
        const endItem = Math.min(this.currentPage * this.options.pageSize, this.filteredData.length);
        
        return `
            <div class="table-pagination">
                <div class="pagination-info">
                    显示 ${startItem}-${endItem} 项，共 ${this.filteredData.length} 项
                </div>
                <div class="pagination-controls">
                    <button class="pagination-btn" 
                            onclick="dataTableInstance.goToPage(${this.currentPage - 1})"
                            ${this.currentPage === 1 ? 'disabled' : ''}>
                        上一页
                    </button>
                    ${this.renderPageNumbers(totalPages)}
                    <button class="pagination-btn" 
                            onclick="dataTableInstance.goToPage(${this.currentPage + 1})"
                            ${this.currentPage === totalPages ? 'disabled' : ''}>
                        下一页
                    </button>
                </div>
            </div>
        `;
    }

    renderPageNumbers(totalPages) {
        const pages = [];
        const maxVisible = 5;
        
        let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);
        
        if (end - start < maxVisible - 1) {
            start = Math.max(1, end - maxVisible + 1);
        }
        
        for (let i = start; i <= end; i++) {
            pages.push(`
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}"
                        onclick="dataTableInstance.goToPage(${i})">
                    ${i}
                </button>
            `);
        }
        
        return pages.join('');
    }

    getPaginatedData() {
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        return this.filteredData.slice(start, end);
    }

    getOriginalIndex(paginatedIndex) {
        const start = (this.currentPage - 1) * this.options.pageSize;
        return start + paginatedIndex;
    }

    bindEvents() {
        // 可以在这里添加其他事件绑定
    }

    handleSearch(query) {
        const lowerQuery = query.toLowerCase();
        this.filteredData = this.options.data.filter(row => {
            return this.options.columns.some(col => {
                const value = row[col.key];
                return String(value).toLowerCase().includes(lowerQuery);
            });
        });
        
        this.currentPage = 1;
        this.render();
    }

    handleSort(column) {
        if (!this.options.sortable) return;
        
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }
        
        this.filteredData.sort((a, b) => {
            const aVal = a[column];
            const bVal = b[column];
            
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }
            
            const aStr = String(aVal).toLowerCase();
            const bStr = String(bVal).toLowerCase();
            
            if (this.sortDirection === 'asc') {
                return aStr.localeCompare(bStr);
            } else {
                return bStr.localeCompare(aStr);
            }
        });
        
        this.render();
    }

    handleRowClick(index) {
        if (!this.options.selectable) return;
        
        if (this.selectedRows.has(index)) {
            this.selectedRows.delete(index);
        } else {
            this.selectedRows.clear();
            this.selectedRows.add(index);
        }
        
        this.render();
        
        if (this.options.onRowSelect) {
            const rowData = this.options.data[index];
            this.options.onRowSelect(rowData, index);
        }
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.render();
    }

    setData(data) {
        this.options.data = data;
        this.filteredData = [...data];
        this.currentPage = 1;
        this.selectedRows.clear();
        this.render();
    }

    getSelectedData() {
        return Array.from(this.selectedRows).map(index => this.options.data[index]);
    }

    clearSelection() {
        this.selectedRows.clear();
        this.render();
    }
}

// 全局实例，用于表格事件处理
let dataTableInstance = null;
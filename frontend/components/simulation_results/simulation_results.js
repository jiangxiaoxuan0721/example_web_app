/**
 * 仿真结果展示组件
 * 用于展示N-1仿真结果，包括图表、数据表格和分析
 */

class SimulationResults {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`SimulationResults: Container with id '${containerId}' not found`);
            return;
        }

        this.options = {
            showExport: true,
            showAnalysis: true,
            exportText: '导出结果',
            analyzeText: '分析结果',
            ...options
        };

        this.results = null;
        this.charts = [];
        this.callbacks = {
            onExport: options.onExport || (() => {}),
            onAnalyze: options.onAnalyze || (() => {}),
            ...options.callbacks
        };

        this.init();
    }

    init() {
        this.container.classList.add('simulation-results');
        this.render();
    }

    setResults(results) {
        this.results = results;
        this.render();
    }

    addChart(chartId, chartType, data, options = {}) {
        this.charts.push({
            id: chartId,
            type: chartType,
            data: data,
            options: options
        });
        this.render();
    }

    removeChart(chartId) {
        this.charts = this.charts.filter(chart => chart.id !== chartId);
        this.render();
    }

    clearResults() {
        this.results = null;
        this.charts = [];
        this.render();
    }

    render() {
        this.container.innerHTML = '';

        if (!this.results && this.charts.length === 0) {
            this.renderEmptyState();
            return;
        }

        // 结果概览
        if (this.results && this.results.summary) {
            this.renderSummary();
        }

        // 图表容器
        if (this.charts.length > 0) {
            this.renderCharts();
        }

        // 数据表格
        if (this.results && this.results.data) {
            this.renderDataTable();
        }

        // 分析结果
        if (this.options.showAnalysis && this.results && this.results.analysis) {
            this.renderAnalysis();
        }

        // 操作按钮
        if (this.options.showExport) {
            this.renderActions();
        }
    }

    renderEmptyState() {
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        
        const icon = document.createElement('div');
        icon.className = 'empty-state-icon';
        icon.innerHTML = `
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="9" x2="15" y2="9"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
        `;
        
        const message = document.createElement('div');
        message.className = 'empty-state-message';
        message.textContent = '暂无仿真结果';
        
        emptyState.appendChild(icon);
        emptyState.appendChild(message);
        this.container.appendChild(emptyState);
    }

    renderSummary() {
        const summarySection = document.createElement('div');
        summarySection.className = 'results-summary';
        
        const title = document.createElement('h3');
        title.className = 'section-title';
        title.textContent = '仿真概览';
        summarySection.appendChild(title);
        
        const summaryCards = document.createElement('div');
        summaryCards.className = 'summary-cards';
        
        // 显示关键指标
        const metrics = this.results.summary;
        Object.entries(metrics).forEach(([key, value]) => {
            const card = document.createElement('div');
            card.className = 'summary-card';
            
            const label = document.createElement('div');
            label.className = 'card-label';
            label.textContent = this.formatMetricName(key);
            
            const metricValue = document.createElement('div');
            metricValue.className = 'card-value';
            
            // 根据值判断是否稳定
            if (key.toLowerCase().includes('稳定')) {
                const isStable = value === '稳定' || value === 'stable';
                metricValue.classList.add(isStable ? 'stable' : 'unstable');
                metricValue.textContent = value;
            } else {
                metricValue.textContent = value;
            }
            
            card.appendChild(label);
            card.appendChild(metricValue);
            summaryCards.appendChild(card);
        });
        
        summarySection.appendChild(summaryCards);
        this.container.appendChild(summarySection);
    }

    renderCharts() {
        const chartsSection = document.createElement('div');
        chartsSection.className = 'results-charts';
        
        const title = document.createElement('h3');
        title.className = 'section-title';
        title.textContent = '结果图表';
        chartsSection.appendChild(title);
        
        const chartsGrid = document.createElement('div');
        chartsGrid.className = 'charts-grid';
        
        this.charts.forEach(chart => {
            const chartContainer = document.createElement('div');
            chartContainer.className = 'chart-container';
            chartContainer.id = `chart-${chart.id}`;
            
            const chartTitle = document.createElement('h4');
            chartTitle.className = 'chart-title';
            chartTitle.textContent = chart.options.title || `图表 ${chart.id}`;
            
            const chartElement = document.createElement('div');
            chartElement.className = 'chart-element';
            
            // 根据图表类型创建不同的图表
            if (chart.type === 'line') {
                this.createLineChart(chartElement, chart.data, chart.options);
            } else if (chart.type === 'bar') {
                this.createBarChart(chartElement, chart.data, chart.options);
            } else if (chart.type === 'scatter') {
                this.createScatterChart(chartElement, chart.data, chart.options);
            } else if (chart.type === 'image') {
                this.createImageChart(chartElement, chart.data, chart.options);
            }
            
            chartContainer.appendChild(chartTitle);
            chartContainer.appendChild(chartElement);
            chartsGrid.appendChild(chartContainer);
        });
        
        chartsSection.appendChild(chartsGrid);
        this.container.appendChild(chartsSection);
    }

    renderDataTable() {
        const dataSection = document.createElement('div');
        dataSection.className = 'results-data';
        
        const title = document.createElement('h3');
        title.className = 'section-title';
        title.textContent = '详细数据';
        dataSection.appendChild(title);
        
        const tableContainer = document.createElement('div');
        tableContainer.className = 'table-container';
        tableContainer.style.overflow = 'auto';
        
        const table = document.createElement('table');
        table.className = 'data-table';
        
        // 表头
        if (this.results.data.headers) {
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            this.results.data.headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        
        // 表格数据
        if (this.results.data.rows) {
            const tbody = document.createElement('tbody');
            
            this.results.data.rows.forEach(row => {
                const tr = document.createElement('tr');
                
                row.forEach(cell => {
                    const td = document.createElement('td');
                    td.textContent = cell;
                    tr.appendChild(td);
                });
                
                tbody.appendChild(tr);
            });
            
            table.appendChild(tbody);
        }
        
        tableContainer.appendChild(table);
        dataSection.appendChild(tableContainer);
        this.container.appendChild(dataSection);
    }

    renderAnalysis() {
        const analysisSection = document.createElement('div');
        analysisSection.className = 'results-analysis';
        
        const title = document.createElement('h3');
        title.className = 'section-title';
        title.textContent = '分析结果';
        analysisSection.appendChild(title);
        
        const analysisContent = document.createElement('div');
        analysisContent.className = 'analysis-content';
        analysisContent.innerHTML = this.results.analysis;
        
        analysisSection.appendChild(analysisContent);
        this.container.appendChild(analysisSection);
    }

    renderActions() {
        const actionsSection = document.createElement('div');
        actionsSection.className = 'results-actions';
        
        if (this.options.showExport) {
            const exportButton = document.createElement('button');
            exportButton.className = 'btn btn-secondary export-button';
            exportButton.textContent = this.options.exportText;
            exportButton.addEventListener('click', () => {
                this.callbacks.onExport(this.results);
            });
            actionsSection.appendChild(exportButton);
        }
        
        if (this.options.showAnalysis && !this.results.analysis) {
            const analyzeButton = document.createElement('button');
            analyzeButton.className = 'btn btn-primary analyze-button';
            analyzeButton.textContent = this.options.analyzeText;
            analyzeButton.addEventListener('click', () => {
                this.callbacks.onAnalyze(this.results);
            });
            actionsSection.appendChild(analyzeButton);
        }
        
        if (actionsSection.children.length > 0) {
            this.container.appendChild(actionsSection);
        }
    }

    createLineChart(container, data, options) {
        // 这里可以集成真实的图表库，如Chart.js
        // 为了简化，这里只显示一个占位符
        const chartPlaceholder = document.createElement('div');
        chartPlaceholder.className = 'chart-placeholder';
        chartPlaceholder.innerHTML = `
            <div class="chart-info">
                <p>线形图: ${options.title || '未命名图表'}</p>
                <p>数据点: ${data.length || 0}</p>
            </div>
        `;
        container.appendChild(chartPlaceholder);
    }

    createBarChart(container, data, options) {
        const chartPlaceholder = document.createElement('div');
        chartPlaceholder.className = 'chart-placeholder';
        chartPlaceholder.innerHTML = `
            <div class="chart-info">
                <p>柱状图: ${options.title || '未命名图表'}</p>
                <p>数据点: ${data.length || 0}</p>
            </div>
        `;
        container.appendChild(chartPlaceholder);
    }

    createScatterChart(container, data, options) {
        const chartPlaceholder = document.createElement('div');
        chartPlaceholder.className = 'chart-placeholder';
        chartPlaceholder.innerHTML = `
            <div class="chart-info">
                <p>散点图: ${options.title || '未命名图表'}</p>
                <p>数据点: ${data.length || 0}</p>
            </div>
        `;
        container.appendChild(chartPlaceholder);
    }

    createImageChart(container, data, options) {
        const imageElement = document.createElement('img');
        imageElement.className = 'result-image';
        imageElement.src = data.url;
        imageElement.alt = options.title || '结果图表';
        
        // 如果提供了宽度和高度
        if (options.width) imageElement.width = options.width;
        if (options.height) imageElement.height = options.height;
        
        container.appendChild(imageElement);
    }

    formatMetricName(name) {
        // 将下划线转换为中文字符，或进行其他格式化
        const nameMap = {
            'voltage_stability': '电压稳定性',
            'frequency_stability': '频率稳定性',
            'angle_stability': '功角稳定性',
            'overall_stability': '整体稳定性',
            'max_voltage': '最大电压',
            'min_voltage': '最小电压',
            'simulation_time': '仿真时间',
            'convergence_iterations': '收敛迭代次数'
        };
        
        return nameMap[name] || name;
    }

    exportResults(format = 'json') {
        if (!this.results) {
            console.error('No results to export');
            return;
        }
        
        let content, filename, mimeType;
        
        if (format === 'csv' && this.results.data) {
            // 导出为CSV
            content = this.convertToCSV(this.results.data);
            filename = `simulation_results_${new Date().getTime()}.csv`;
            mimeType = 'text/csv';
        } else {
            // 默认导出为JSON
            content = JSON.stringify(this.results, null, 2);
            filename = `simulation_results_${new Date().getTime()}.json`;
            mimeType = 'application/json';
        }
        
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    convertToCSV(data) {
        if (!data.headers || !data.rows) return '';
        
        const csvRows = [];
        
        // 添加表头
        csvRows.push(data.headers.join(','));
        
        // 添加数据行
        data.rows.forEach(row => {
            csvRows.push(row.join(','));
        });
        
        return csvRows.join('\n');
    }
}

// 导出组件
window.SimulationResults = SimulationResults;
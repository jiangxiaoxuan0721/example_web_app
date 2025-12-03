/**
 * 表格相关功能模块
 */

/**
 * 显示表格数据
 * @param {string} containerId - 容器ID
 * @param {object} data - 表格数据
 */
function displayTable(containerId, data) {
    const container = document.getElementById(containerId);
    
    if (!data || !data.data || !data.data.columns) {
        container.innerHTML = '<p>数据格式错误</p>';
        return;
    }

    let html = '<table>';
    
    // 生成表头
    html += '<tr>';
    data.data.columns.forEach(col => {
        html += `<th>${col.name || 'Column'}</th>`;
    });
    html += '</tr>';
    
    // 生成数据行
    if (data.data.columns.length > 0) {
        const maxRows = Math.max(...data.data.columns.map(col => 
            col.data ? col.data.length : 0));
        
        for (let row = 0; row < maxRows; row++) {
            html += '<tr>';
            data.data.columns.forEach(col => {
                const value = col.data && col.data[row] !== undefined ? col.data[row] : '';
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        }
    }
    
    html += '</table>';
    container.innerHTML = html;
}

/**
 * 显示原始JSON数据
 * @param {object} data - 要显示的数据
 */
function displayRawData(data) {
    const rawDataContainer = document.getElementById('rawData');
    rawDataContainer.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
}
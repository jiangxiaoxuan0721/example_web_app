/**
 * API调用模块
 */

/**
 * 生成IEEE3数据
 * @returns {Promise<string>} 生成结果
 */
async function generateIEEE3Data() {
    try {
        const response = await fetch('/generate_IEEE3_table');
        return await response.text();
    } catch (error) {
        throw new Error('生成数据请求失败: ' + error.message);
    }
}

/**
 * 获取表格数据
 * @returns {Promise<object>} 表格数据
 */
async function fetchTableData() {
    try {
        const response = await fetch('/api/table');
        return await response.json();
    } catch (error) {
        throw new Error('获取表格数据失败: ' + error.message);
    }
}

/**
 * 获取功率流图数据
 * @returns {Promise<object>} 功率流图数据
 */
async function fetchPowerFlowGraphData() {
    try {
        const response = await fetch('/api/power-flow-graph');
        return await response.json();
    } catch (error) {
        throw new Error('获取功率流图数据失败: ' + error.message);
    }
}

/**
 * 获取功率统计信息
 * @returns {Promise<object>} 功率统计信息
 */
async function fetchPowerSummary() {
    try {
        const response = await fetch('/api/power-summary');
        return await response.json();
    } catch (error) {
        throw new Error('获取功率统计信息失败: ' + error.message);
    }
}
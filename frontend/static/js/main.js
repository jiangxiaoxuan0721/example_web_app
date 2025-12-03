/**
 * 主要业务逻辑模块
 */

/**
 * 生成数据的主函数
 */
async function generateData() {
    try {
        showMessage('正在生成数据...', 'success');
        const result = await generateIEEE3Data();
        
        if (result === 'success') {
            showMessage('数据生成成功！', 'success');
            setTimeout(loadData, 1000);
        } else {
            showMessage('生成失败: ' + result, 'error');
        }
    } catch (error) {
        showMessage('请求失败: ' + error.message, 'error');
    }
}

/**
 * 加载所有数据的主函数
 */
async function loadData() {
    try {
        // 并行加载所有数据
        const [tableData, powerFlowData, summaryData] = await Promise.all([
            fetchTableData(),
            fetchPowerFlowGraphData(),
            fetchPowerSummary()
        ]);
        
        // 显示节点数据
        if (tableData.buses) {
            displayTable('busTable', tableData.buses);
        }
        
        // 显示支路数据
        if (tableData.branches) {
            displayTable('branchTable', tableData.branches);
        }
        
        // 显示功率流图
        displayPowerFlowGraph(powerFlowData);
        
        // 显示功率统计信息
        displayPowerSummary(summaryData);
        
        // 显示原始JSON数据
        displayRawData(tableData);
            
        showMessage('数据加载成功', 'success');
    } catch (error) {
        showMessage('加载数据失败: ' + error.message, 'error');
    }
}

/**
 * 页面初始化
 */
function initializePage() {
    // 页面加载时自动加载数据
    loadData();
}

// 当DOM加载完成后初始化页面
document.addEventListener('DOMContentLoaded', initializePage);
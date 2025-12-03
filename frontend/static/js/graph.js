/**
 * 图表相关功能模块
 */

/**
 * 显示功率流图
 * @param {object} data - 功率流图数据
 */
function displayPowerFlowGraph(data) {
    const container = document.getElementById('powerFlowGraph');
    
    if (!data.nodes || !data.edges) {
        container.innerHTML = '<p>功率流数据格式错误</p>';
        return;
    }

    const nodes = new vis.DataSet(data.nodes);
    const edges = new vis.DataSet(data.edges);

    const networkData = {
        nodes: nodes,
        edges: edges
    };

    const options = {
        layout: {
            randomSeed: 2,  // 固定随机种子，保持布局一致
            improvedLayout: false  // 禁用自动布局优化
        },
        nodes: {
            shape: 'box',
            margin: 15,
            font: {
                size: 20,
                color: '#333',
                bold: true
            },
            borderWidth: 2,
            shadow: true,
            physics: false  // 禁用节点物理效果，允许手动拖拽
        },
        edges: {
            smooth: {
                type: 'cubicBezier',
                roundness: 0.5
            },
            font: {
                size: 16,
                align: 'middle',
                background: 'white',
                strokeWidth: 3,
                strokeColor: 'white'
            },
            shadow: true,
            physics: false  // 禁用边物理效果
        },
        physics: {
            enabled: false  // 完全禁用物理引擎
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            dragNodes: true,  // 允许拖拽节点
            dragView: true,   // 允许拖拽视图
            zoomView: true    // 允许缩放视图
        },
        manipulation: {
            enabled: false   // 禁用编辑功能
        }
    };

    new vis.Network(container, networkData, options);
}

/**
 * 显示功率统计信息
 * @param {object} data - 功率统计数据
 */
function displayPowerSummary(data) {
    const container = document.getElementById('powerSummary');
    
    if (!data) {
        container.innerHTML = '<p>暂无功率流统计信息</p>';
        return;
    }

    const html = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
            <div><strong>总支路数:</strong> ${data.total_branches}</div>
            <div><strong>总有功功率:</strong> ${formatNumber(data.total_active_power || 0)} MW</div>
            <div><strong>总无功功率:</strong> ${formatNumber(data.total_reactive_power || 0)} MVar</div>
            <div><strong>有功损耗:</strong> ${formatNumber(data.total_active_loss || 0)} MW</div>
            <div><strong>无功损耗:</strong> ${formatNumber(data.total_reactive_loss || 0)} MVar</div>
            <div><strong>最大功率支路:</strong> ${safeGet(data, 'max_power_branch.id', 'N/A')} (${formatNumber(safeGet(data, 'max_power_branch.power', 0))} MW)</div>
            <div><strong>最小功率支路:</strong> ${safeGet(data, 'min_power_branch.id', 'N/A')} (${formatNumber(safeGet(data, 'min_power_branch.power', 0))} MW)</div>
        </div>
    `;
    
    container.innerHTML = html;
}
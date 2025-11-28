// 全局变量
let topologyNetwork = null;
let voltageChart = null;
let powerChart = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadVisualizationData();
    setupEventListeners();
});

// 初始化图表
function initializeCharts() {
    // 初始化电压分布图
    const voltageCtx = document.getElementById('voltageChart').getContext('2d');
    voltageChart = new Chart(voltageCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '电压幅值 (p.u.)',
                data: [],
                backgroundColor: '#36a2eb',
                borderColor: '#36a2eb',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0.9,
                    max: 1.1
                }
            }
        }
    });

    // 初始化功率分布图
    const powerCtx = document.getElementById('powerChart').getContext('2d');
    powerChart = new Chart(powerCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '有功功率 (MW)',
                data: [],
                borderColor: '#ff6384',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }, {
                label: '无功功率 (MVar)',
                data: [],
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 设置事件监听器
function setupEventListeners() {
    // 生成数据按钮
    document.getElementById('generateData').addEventListener('click', function() {
        generateData();
    });

    // 刷新数据按钮
    document.getElementById('refreshData').addEventListener('click', function() {
        loadVisualizationData();
    });

    // 视图显示/隐藏控制
    ['showTopology', 'showVoltage', 'showPower', 'showTable'].forEach(id => {
        document.getElementById(id).addEventListener('change', function() {
            toggleSection(id.replace('show', '').toLowerCase(), this.checked);
        });
    });
}

// 生成数据
async function generateData() {
    try {
        const response = await fetch('/generate_IEEE3_table');
        const result = await response.text();
        
        if (result === 'success') {
            showAlert('数据生成成功！', 'success');
            setTimeout(loadVisualizationData, 1000); // 延迟加载数据
        } else {
            showAlert('数据生成失败：' + result, 'danger');
        }
    } catch (error) {
        showAlert('请求失败：' + error.message, 'danger');
    }
}

// 加载可视化数据
async function loadVisualizationData() {
    try {
        // 加载拓扑图数据
        const topologyResponse = await fetch('/api/topology');
        const topologyData = await topologyResponse.json();
        updateTopology(topologyData);

        // 加载电压数据
        const voltageResponse = await fetch('/api/voltage');
        const voltageData = await voltageResponse.json();
        updateVoltageChart(voltageData);

        // 加载功率数据
        const powerResponse = await fetch('/api/power');
        const powerData = await powerResponse.json();
        updatePowerChart(powerData);

        // 加载表格数据
        const tableResponse = await fetch('/api/table');
        const tableData = await tableResponse.json();
        updateTables(tableData);

    } catch (error) {
        console.error('加载数据失败:', error);
        showAlert('加载数据失败：' + error.message, 'warning');
    }
}

// 更新拓扑图
function updateTopology(data) {
    const container = document.getElementById('topology');
    
    const nodes = new vis.DataSet(data.nodes || []);
    const edges = new vis.DataSet(data.edges || []);

    const networkData = {
        nodes: nodes,
        edges: edges
    };

    const options = {
        layout: {
            hierarchical: {
                direction: 'UD',
                sortMethod: 'directed'
            }
        },
        nodes: {
            shape: 'box',
            margin: 10,
            font: {
                size: 14
            }
        },
        edges: {
            arrows: 'to',
            smooth: {
                type: 'cubicBezier'
            }
        },
        physics: {
            enabled: false
        }
    };

    if (topologyNetwork) {
        topologyNetwork.destroy();
    }
    
    topologyNetwork = new vis.Network(container, networkData, options);
}

// 更新电压图表
function updateVoltageChart(data) {
    if (voltageChart && data.labels && data.datasets) {
        voltageChart.data.labels = data.labels;
        voltageChart.data.datasets = data.datasets;
        voltageChart.update();
    }
}

// 更新功率图表
function updatePowerChart(data) {
    if (powerChart && data.labels) {
        powerChart.data.labels = data.labels;
        powerChart.data.datasets[0].data = data.active_power || [];
        powerChart.data.datasets[1].data = data.reactive_power || [];
        powerChart.update();
    }
}

// 更新数据表格
function updateTables(data) {
    // 更新节点表格
    const busTableBody = document.querySelector('#busDataTable tbody');
    busTableBody.innerHTML = '';
    
    if (data.buses && data.buses.data && data.buses.data.columns) {
        // 这里需要根据实际数据结构调整
        const sampleData = [
            {id: 'Bus 1', voltage: '1.05', angle: '0.0', active: '50.2', reactive: '10.5'},
            {id: 'Bus 2', voltage: '1.02', angle: '-2.1', active: '30.5', reactive: '8.2'},
            {id: 'Bus 3', voltage: '0.98', angle: '-4.3', active: '20.1', reactive: '5.3'}
        ];
        
        sampleData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.id}</td>
                <td>${row.voltage}</td>
                <td>${row.angle}</td>
                <td>${row.active}</td>
                <td>${row.reactive}</td>
            `;
            busTableBody.appendChild(tr);
        });
    }

    // 更新支路表格
    const branchTableBody = document.querySelector('#branchDataTable tbody');
    branchTableBody.innerHTML = '';
    
    const sampleBranchData = [
        {id: 'Branch 1', from: 'Bus 1', to: 'Bus 2', active: '25.1', reactive: '5.2'},
        {id: 'Branch 2', from: 'Bus 2', to: 'Bus 3', active: '15.3', reactive: '3.1'},
        {id: 'Branch 3', from: 'Bus 1', to: 'Bus 3', active: '10.2', reactive: '2.1'}
    ];
    
    sampleBranchData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.from}</td>
            <td>${row.to}</td>
            <td>${row.active}</td>
            <td>${row.reactive}</td>
        `;
        branchTableBody.appendChild(tr);
    });
}

// 切换显示/隐藏区域
function toggleSection(section, show) {
    const sectionMap = {
        'topology': 'topologySection',
        'voltage': 'voltageSection', 
        'power': 'powerSection',
        'table': 'tableSection'
    };
    
    const element = document.getElementById(sectionMap[section]);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}

// 显示提示信息
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 3秒后自动消失
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 3000);
}
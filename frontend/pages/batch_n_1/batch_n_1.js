// ==========================================
// 1. 数据源注入
// ==========================================
const rawData = [
  {
    "final_result": {
      "transKey": "canvas_0_80",
      "fault_start_time": 3.0,
      "cut_time": 3.15,
      "fault_type": 7,
      "voltage_ok": "True",
      "min_voltage": 2.7080039353050064e-11,
      "frequency_ok": "True",
      "max_freq_deviation": 55.3304598070532,
      "power_angle_ok": "True",
      "max_power_angle_diff": 6.212436219154938,
      "minio_path1": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_15_08_13_05a13b.html",
      "minio_path2": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_59_15de6a.png",
      "minio_path3": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_53_00_699b67.png",
      "minio_path4": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_53_01_0d1ca5.png"
    },
    "saved_results": {
      "save_flow_emt_hdf5": {
        "flow_url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/flow_result/2025/12/17/20251217_135110_46cefd7e_pass.h5",
        "emt_url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/emt_result/2025/12/17/20251217_135110_46cefd7e_pass.h5"
      }
    }
  },
  {
    "final_result": {
      "transKey": "canvas_0_63",
      "fault_start_time": 3.0,
      "cut_time": 3.16,
      "fault_type": 7,
      "voltage_ok": "True",
      "min_voltage": 2.7080039353019988e-11,
      "frequency_ok": "False",
      "max_freq_deviation": 7.134955883519552,
      "power_angle_ok": "True",
      "max_power_angle_diff": 6.212436217030017,
      "minio_path1": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_55_908377.png",
      "minio_path2": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_59_2a8b0d.png",
      "minio_path3": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_53_00_4e5efa.png",
      "minio_path4": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_53_00_20fd38.png"
    },
    "saved_results": {
      "save_flow_emt_hdf5": {
        "flow_url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/flow_result/2025/12/17/20251217_135110_46cefd7e_pass.h5",
        "emt_url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/emt_result/2025/12/17/20251217_135110_46cefd7e_pass.h5"
      }
    }
  },
  {
    "final_result": {
      "transKey": "canvas_0_118",
      "fault_start_time": 3.0,
      "cut_time": 3.17,
      "fault_type": 7,
      "voltage_ok": "True",
      "min_voltage": 2.7080039353019988e-11,
      "frequency_ok": "False",
      "max_freq_deviation": 34.7306556136338,
      "power_angle_ok": "True",
      "max_power_angle_diff": 6.212436217168573,
      "minio_path1": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_45_808ed9.png",
      "minio_path2": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_49_cc82e9.png",
      "minio_path3": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_50_cccb1f.png",
      "minio_path4": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_51_8c6a93.png"
    },
    "saved_results": {
      "save_flow_emt_hdf5": {
        "flow_url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/flow_result/2025/12/17/20251217_135110_46cefd7e_pass.h5",
        "emt_url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/emt_result/2025/12/17/20251217_135110_46cefd7e_pass.h5"
      }
    }
  }
];

// ==========================================
// 1.1 组件实例
// ==========================================
let kpiCards = null;
let dataTable = null;
let drawer = null;

// ==========================================
// 2. 辅助函数
// ==========================================
const faultTypeMap = {
    7: "三相短路 (3PH)",
    8: "单相接地 (1PH-GND)",
    9: "两相短路 (2PH)",
    "default": "未知故障"
};

function getFaultType(code) {
    return faultTypeMap[code] || `${faultTypeMap['default']} (${code})`;
}

function formatNumber(num, unit = '') {
    if (num === null || num === undefined) return '--';
    let val = parseFloat(num);
    if (Math.abs(val) < 0.0001 && val !== 0) {
        return val.toExponential(2) + ' ' + unit; 
    }
    return val.toFixed(4) + ' ' + unit;
}

function isOk(strBool) {
    return strBool === "True";
}

// ==========================================
// 3. 数据处理与渲染
// ==========================================

let processedData = [];

// 筛选状态管理
const activeFilters = {
    unstable: false, // 所有异常
    volt: false,     // 电压越限
    freq: false,     // 频率失稳
    angle: false     // 功角失稳
};

window.onload = function() {
    initComponents();
    processData();
    renderKPI();
    renderTable(processedData);
    
    const now = new Date();
    document.getElementById('report-meta').innerText = `报告生成时间: ${now.toLocaleString()} | 记录数: ${processedData.length}`;
};

function initComponents() {
    // 初始化KPI卡片组件
    kpiCards = new KPICards('kpi-board', {
        layout: 'inline', // 使用一行内布局
        animated: true
    });

    // 初始化表格组件
    dataTable = new DataTable('table-container', {
        columns: [
            { key: 'id', title: 'Case ID (TransKey)', width: '15%' },
            { key: 'faultTypeStr', title: '故障类型', width: '10%' },
            { key: 'volt', title: '最低电压', width: '12%', type: 'number', render: renderVoltageCell },
            { key: 'freq', title: '最大频偏', width: '12%', type: 'number', render: renderFreqCell },
            { key: 'angle', title: '最大功角差', width: '12%', type: 'number', render: renderAngleCell },
            { key: 'status', title: '稳定性结论', width: '25%', render: renderStatusCell },
            { key: 'actions', title: '操作', width: '8%', render: renderActionsCell }
        ],
        data: [],
        searchable: true,
        paginated: true,
        pageSize: 10,
        selectable: true,
        sortable: true,
        toolbarActions: `
            <div class="v-divider"></div>
            <button class="btn btn-filter" id="filter-unstable" onclick="toggleFilter('unstable')">
                所有异常
            </button>
            <button class="btn btn-filter type-error" id="filter-volt" onclick="toggleFilter('volt')">
                电压越限
            </button>
            <button class="btn btn-filter type-warning" id="filter-freq" onclick="toggleFilter('freq')">
                频率失稳
            </button>
            <button class="btn btn-filter type-error" id="filter-angle" onclick="toggleFilter('angle')">
                功角失稳
            </button>
            <div style="margin-left: auto; font-size: 13px; color: #999;">点击行查看详情</div>
        `,
        onRowSelect: (rowData, index) => {
            openDrawer(rowData.index);
        }
    });

    // 设置全局表格实例
    dataTableInstance = dataTable;

    // 初始化抽屉组件
    drawer = drawerManager.create('batch-drawer', {
        title: '详细报告',
        size: 'large'
    });
}

function processData() {
    processedData = rawData.map((item, index) => {
        const res = item.final_result;
        const files = item.saved_results?.save_flow_emt_hdf5 || {};
        
        let failureModes = [];
        if (!isOk(res.voltage_ok)) failureModes.push('电压失稳');
        if (!isOk(res.frequency_ok)) failureModes.push('频率失稳');
        if (!isOk(res.power_angle_ok)) failureModes.push('功角失稳');
        
        return {
            index: index,
            id: res.transKey,
            faultTypeStr: getFaultType(res.fault_type),
            volt: parseFloat(res.min_voltage),
            freq: parseFloat(res.max_freq_deviation),
            angle: parseFloat(res.max_power_angle_diff),
            
            isVoltOk: isOk(res.voltage_ok),
            isFreqOk: isOk(res.frequency_ok),
            isAngleOk: isOk(res.power_angle_ok),
            isStable: failureModes.length === 0,
            failureModes: failureModes,
            
            timing: { start: res.fault_start_time, cut: res.cut_time },
            images: [res.minio_path1, res.minio_path2, res.minio_path3, res.minio_path4],
            files: files
        };
    });
}

function renderKPI() {
    const total = processedData.length;
    const voltFail = processedData.filter(d => !d.isVoltOk).length;
    const freqFail = processedData.filter(d => !d.isFreqOk).length;
    const angleFail = processedData.filter(d => !d.isAngleOk).length;

    const cards = [
        KPICards.createCard('total', '仿真总工况数', total, {
            type: 'primary'
        }),
        KPICards.createCard('voltage', '电压稳定性异常', voltFail, {
            type: 'danger'
        }),
        KPICards.createCard('frequency', '频率稳定性异常', freqFail, {
            type: 'warning'
        }),
        KPICards.createCard('angle', '功角稳定性异常', angleFail, {
            type: 'danger'
        })
    ];

    kpiCards.setCards(cards);
}

function renderTable(data) {
    dataTable.setData(data);
}

// 表格单元格渲染函数
function renderVoltageCell(value, row) {
    const className = !row.isVoltOk ? 'text-error' : '';
    return `<span class="${className}">${formatNumber(value, 'p.u.')}</span>`;
}

function renderFreqCell(value, row) {
    const className = !row.isFreqOk ? 'text-warning' : '';
    return `<span class="${className}">${formatNumber(value, 'Hz')}</span>`;
}

function renderAngleCell(value, row) {
    const className = !row.isAngleOk ? 'text-error' : '';
    return `<span class="${className}">${formatNumber(value, '°')}</span>`;
}

function renderStatusCell(value, row) {
    if (row.isStable) {
        return '<span class="table-tag table-tag-success">系统稳定</span>';
    } else {
        return row.failureModes.map(m => {
            let cls = 'table-tag-warning';
            if(m.includes('功角') || m.includes('电压')) cls = 'table-tag-error';
            return `<span class="table-tag ${cls}">${m}</span>`;
        }).join(' ');
    }
}

function renderActionsCell(value, row) {
    return `<button class="btn btn-primary btn-sm" onclick="openDrawer(${row.index}, event)">查看</button>`;
}

// ==========================================
// 4. 增强筛选逻辑 (OR 逻辑)
// ==========================================

function toggleFilter(type) {
    // 检查当前按钮是否已经是激活状态
    const wasActive = activeFilters[type];
    
    // 清除所有筛选状态
    Object.keys(activeFilters).forEach(key => {
        activeFilters[key] = false;
        const btn = document.getElementById(`filter-${key}`);
        if (btn) {
            btn.setAttribute('data-active', 'false');
        }
    });
    
    // 如果当前按钮之前不是激活状态，则激活它
    if (!wasActive) {
        activeFilters[type] = true;
        const btn = document.getElementById(`filter-${type}`);
        if (btn) {
            btn.setAttribute('data-active', 'true');
        }
    }
    
    applyFilter();
}

function applyFilter() {
    try {
        // 获取搜索框的值 - 尝试多个可能的搜索框
        let query = '';
        const searchInput1 = document.getElementById('search-box');
        const searchInput2 = document.querySelector('.table-search');
        
        if (searchInput1) {
            query = searchInput1.value.toLowerCase();
        } else if (searchInput2) {
            query = searchInput2.value.toLowerCase();
        }
        
        // 检查是否有任何过滤器处于激活状态
        const hasActiveFilters = Object.values(activeFilters).some(v => v);

        const filtered = processedData.filter(item => {
            // 1. 文本搜索过滤
            const matchesSearch = !query || item.id.toLowerCase().includes(query);
            if (!matchesSearch) return false;

            // 2. 按钮状态过滤
            // 如果没有选任何按钮，只看搜索结果
            if (!hasActiveFilters) return true;

            // 单选模式：只检查当前激活的筛选条件
            if (activeFilters.unstable && !item.isStable) return true;
            if (activeFilters.volt && !item.isVoltOk) return true;
            if (activeFilters.freq && !item.isFreqOk) return true;
            if (activeFilters.angle && !item.isAngleOk) return true;

            return false;
        });

        // 安全地渲染表格
        if (dataTable && typeof dataTable.setData === 'function') {
            renderTable(filtered);
        }
    } catch (error) {
        console.error('搜索过滤错误:', error);
    }
}

// ==========================================
// 5. 抽屉逻辑
// ==========================================

function openDrawer(index, event) {
    if(event) event.stopPropagation();
    const data = processedData[index];
    
    if (!drawer) {
        console.error('Drawer not initialized!');
        return;
    }
    
    // 构建抽屉内容
    const content = `
        ${Drawer.createInfoSection('故障场景定义', [
            { label: '设备标识 (TransKey)', value: data.id },
            { label: '故障类型', value: data.faultTypeStr },
            { label: '故障开始时间', value: data.timing.start + ' s' },
            { label: '故障切除时间', value: data.timing.cut + ' s' }
        ])}
        
        ${Drawer.createInfoSection('关键稳定性指标 (KPIs)', [
            { label: '母线最低电压 (Min Voltage)', value: formatNumber(data.volt, 'p.u.') },
            { label: '最大频率偏移 (Max Freq Dev)', value: formatNumber(data.freq, 'Hz') },
            { label: '发电机最大功角差 (Max Angle Diff)', value: formatNumber(data.angle, 'deg') },
            { label: '综合判定', value: data.isStable ? '满足 N-1 准则' : `不满足: ${data.failureModes.join(' & ')}`, highlight: true }
        ], { subtitle: '系统稳定性评估结果' })}
        
        <div id="waveform-section">
            <h4 class="drawer-section-title">仿真波形分析</h4>
            <div class="img-grid" id="waveform-container">
                <!-- 图片将由picture组件动态加载 -->
            </div>
        </div>
        
        <div class="drawer-section">
            <h4 class="drawer-section-title">原始数据文件下载</h4>
            <table class="file-list-table">
                <thead>
                    <tr>
                        <th>文件类型</th>
                        <th>文件名</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.files.flow_url ? `
                        <tr>
                            <td>潮流计算结果 (Flow HDF5)</td>
                            <td style="word-break:break-all; font-family:monospace; color:#666;">${data.files.flow_url.split('/').pop() || 'download.h5'}</td>
                            <td><a href="${data.files.flow_url}" class="download-btn" download target="_blank">下载</a></td>
                        </tr>
                    ` : ''}
                    ${data.files.emt_url ? `
                        <tr>
                            <td>电磁暂态结果 (EMT HDF5)</td>
                            <td style="word-break:break-all; font-family:monospace; color:#666;">${data.files.emt_url.split('/').pop() || 'download.h5'}</td>
                            <td><a href="${data.files.emt_url}" class="download-btn" download target="_blank">下载</a></td>
                        </tr>
                    ` : ''}
                </tbody>
            </table>
        </div>
    `;

    // 更新抽屉内容并打开
    if (drawer) {
        drawer.setTitle(`${data.id} - 详细报告`);
        drawer.setSubtitle(data.isStable ? Drawer.createStatusIndicator('Stable', 'success') : Drawer.createStatusIndicator('Unstable', 'error'));
        drawer.setContent(content);
        drawer.open();
        
        // 等待抽屉打开后添加图片
        setTimeout(() => {
            const waveformContainer = drawer.drawer.querySelector('#waveform-container');
            if (waveformContainer) {
                // 清空容器
                waveformContainer.innerHTML = '';
                
                // 添加波形图片
                if (data.images[0]) {
                    drawer.addPicture({
                        title: '发电机功角 / Rotor Angle',
                        source: data.images[0],
                        height: '250px',
                        fit: 'contain', // 确保图片比例正确显示
                        showFullscreen: true, // 确保显示全屏按钮
                        showDownload: true,
                        appendTo: waveformContainer
                    });
                }
                if (data.images[1]) {
                    drawer.addPicture({
                        title: '母线电压 / Bus Voltage',
                        source: data.images[1],
                        height: '250px',
                        fit: 'contain',
                        showFullscreen: true,
                        showDownload: true,
                        appendTo: waveformContainer
                    });
                }
                if (data.images[2]) {
                    drawer.addPicture({
                        title: '系统频率 / Frequency',
                        source: data.images[2],
                        height: '250px',
                        fit: 'contain',
                        showFullscreen: true,
                        showDownload: true,
                        appendTo: waveformContainer
                    });
                }
                if (data.images[3]) {
                    drawer.addPicture({
                        title: '发电机有功 / Active Power',
                        source: data.images[3],
                        height: '250px',
                        fit: 'contain',
                        showFullscreen: true,
                        showDownload: true,
                        appendTo: waveformContainer
                    });
                }
            }
        }, 100);
    }
}

function closeDrawer() {
    // 使用抽屉组件关闭
    if (drawer) {
        drawer.close();
    }
}

function goHome() {
    // 返回主页，假设主页是 index.html 或根目录
    window.location.href = '/';
}
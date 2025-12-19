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
      "minio_path1": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_13_52_55_9e6860.png",
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
    processData();
    renderKPI();
    renderTable(processedData);
    
    const now = new Date();
    document.getElementById('report-meta').innerText = `报告生成时间: ${now.toLocaleString()} | 记录数: ${processedData.length}`;
};

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

    document.getElementById('kpi-total').innerText = total;
    document.getElementById('kpi-volt').innerText = voltFail;
    document.getElementById('kpi-freq').innerText = freqFail;
    document.getElementById('kpi-angle').innerText = angleFail;
}

function renderTable(data) {
    const tbody = document.getElementById('table-body');
    const emptyState = document.getElementById('empty-state');
    tbody.innerHTML = '';

    if (data.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    emptyState.style.display = 'none';

    data.forEach(row => {
        const tr = document.createElement('tr');
        
        let statusHtml = '';
        if (row.isStable) {
            statusHtml = '<span class="tag tag-success">✅ 系统稳定</span>';
        } else {
            statusHtml = row.failureModes.map(m => {
                let cls = 'tag-warning';
                if(m.includes('功角') || m.includes('电压')) cls = 'tag-error';
                return `<span class="tag ${cls}">${m}</span>`;
            }).join(' ');
        }

        // 阈值高亮
        const voltClass = !row.isVoltOk ? 'text-error' : '';
        const freqClass = !row.isFreqOk ? 'text-warning' : '';
        const angleClass = !row.isAngleOk ? 'text-error' : '';

        tr.innerHTML = `
            <td style="font-family:monospace; font-weight:600;">${row.id}</td>
            <td>${row.faultTypeStr}</td>
            <td class="${voltClass}">${formatNumber(row.volt, 'p.u.')}</td>
            <td class="${freqClass}">${formatNumber(row.freq, 'Hz')}</td>
            <td class="${angleClass}">${formatNumber(row.angle, '°')}</td>
            <td>${statusHtml}</td>
            <td><button class="btn btn-primary" style="padding:4px 10px; font-size:12px;" onclick="openDrawer(${row.index}, event)">详情</button></td>
        `;
        tr.onclick = () => openDrawer(row.index);
        tbody.appendChild(tr);
    });
}

// ==========================================
// 4. 增强筛选逻辑 (OR 逻辑)
// ==========================================

function toggleFilter(type) {
    // 切换状态
    activeFilters[type] = !activeFilters[type];
    
    // 更新按钮外观
    const btn = document.getElementById(`filter-${type}`);
    btn.setAttribute('data-active', activeFilters[type]);
    
    applyFilter();
}

function applyFilter() {
    const query = document.getElementById('search-box').value.toLowerCase();
    
    // 检查是否有任何过滤器处于激活状态
    const hasActiveFilters = Object.values(activeFilters).some(v => v);

    const filtered = processedData.filter(item => {
        // 1. 文本搜索过滤
        const matchesSearch = item.id.toLowerCase().includes(query);
        if (!matchesSearch) return false;

        // 2. 按钮状态过滤
        // 如果没有选任何按钮，只看搜索结果
        if (!hasActiveFilters) return true;

        // 如果选了按钮，采用 OR 逻辑 (满足任一选中条件即可)
        let matchFilter = false;
        
        if (activeFilters.unstable && !item.isStable) matchFilter = true;
        if (activeFilters.volt && !item.isVoltOk) matchFilter = true;
        if (activeFilters.freq && !item.isFreqOk) matchFilter = true;
        if (activeFilters.angle && !item.isAngleOk) matchFilter = true;

        return matchFilter;
    });

    renderTable(filtered);
}

// ==========================================
// 5. 抽屉逻辑
// ==========================================

function openDrawer(index, event) {
    if(event) event.stopPropagation();
    const data = processedData[index];
    
    document.getElementById('d-title').innerText = `${data.id} - 详细报告`;
    document.getElementById('d-key').innerText = data.id;
    document.getElementById('d-type').innerText = data.faultTypeStr;
    document.getElementById('d-start-time').innerText = data.timing.start;
    document.getElementById('d-cut-time').innerText = data.timing.cut;

    document.getElementById('d-volt').innerText = formatNumber(data.volt, 'p.u.');
    document.getElementById('d-freq').innerText = formatNumber(data.freq, 'Hz');
    document.getElementById('d-angle').innerText = formatNumber(data.angle, 'deg');
    
    const conclusionEl = document.getElementById('d-conclusion');
    const tagsEl = document.getElementById('d-status-tags');
    
    if (data.isStable) {
        conclusionEl.innerHTML = '<span class="tag tag-success" style="font-size:14px;">✅ 满足 N-1 准则</span>';
        tagsEl.innerHTML = '<span class="tag tag-success">Stable</span>';
    } else {
        const reasons = data.failureModes.join(' & ');
        conclusionEl.innerHTML = `<span class="tag tag-error" style="font-size:14px;">❌ 不满足: ${reasons}</span>`;
        tagsEl.innerHTML = `<span class="tag tag-error">Unstable</span>`;
    }

    const containers = [
        document.getElementById('img-container-1'),
        document.getElementById('img-container-2'),
        document.getElementById('img-container-3'),
        document.getElementById('img-container-4')
    ];

    data.images.forEach((url, i) => {
        if (i < 4) {
            if (url && url.trim() !== '') {
                containers[i].innerHTML = `<img src="${url}" alt="Waveform ${i+1}" onerror="this.src='https://via.placeholder.com/800x400?text=Image+Load+Error'">`;
            } else {
                containers[i].innerHTML = `<span style="color:#ccc">无图像数据</span>`;
            }
        }
    });

    const fileBody = document.getElementById('d-file-list');
    fileBody.innerHTML = '';
    const fileMap = [
        { label: '潮流计算结果 (Flow HDF5)', url: data.files.flow_url },
        { label: '电磁暂态结果 (EMT HDF5)', url: data.files.emt_url }
    ];

    fileMap.forEach(f => {
        if (f.url) {
            const fileName = f.url.split('/').pop() || 'download.h5';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${f.label}</td>
                <td style="word-break:break-all; font-family:monospace; color:#666;">${fileName}</td>
                <td><a href="${f.url}" class="download-btn" download target="_blank">⬇️ 下载</a></td>
            `;
            fileBody.appendChild(tr);
        }
    });

    document.getElementById('overlay').classList.add('open');
    document.getElementById('drawer').classList.add('open');
}

function closeDrawer() {
    document.getElementById('overlay').classList.remove('open');
    document.getElementById('drawer').classList.remove('open');
}
/**
 * 工具函数模块
 */

/**
 * 显示消息提示
 * @param {string} msg - 消息内容
 * @param {string} type - 消息类型 ('success' 或 'error')
 */
function showMessage(msg, type = 'success') {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `<div class="${type}">${msg}</div>`;
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 3000);
}

/**
 * 格式化数字为指定小数位数
 * @param {number} num - 数字
 * @param {number} decimals - 小数位数
 * @returns {number} 格式化后的数字
 */
function formatNumber(num, decimals = 2) {
    return parseFloat(num.toFixed(decimals));
}

/**
 * 安全地获取嵌套对象的属性
 * @param {object} obj - 对象
 * @param {string} path - 属性路径，如 'a.b.c'
 * @param {*} defaultValue - 默认值
 * @returns {*} 属性值或默认值
 */
function safeGet(obj, path, defaultValue = null) {
    const keys = path.split('.');
    let result = obj;
    
    for (const key of keys) {
        if (result && typeof result === 'object' && key in result) {
            result = result[key];
        } else {
            return defaultValue;
        }
    }
    
    return result;
}
// 医院综合管理系统 - 前端脚本

// 自动隐藏提示消息
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

// 表单验证辅助函数
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.style.borderColor = 'red';
            isValid = false;
        } else {
            field.style.borderColor = '#ddd';
        }
    });
    
    return isValid;
}

// 确认删除
function confirmDelete(message) {
    return confirm(message || '确定要删除吗？此操作不可恢复。');
}

// 数字输入限制
document.addEventListener('DOMContentLoaded', function() {
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
});

// 表格行点击高亮
document.addEventListener('DOMContentLoaded', function() {
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            // 如果点击的是按钮或链接，不执行高亮
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
                return;
            }
            tableRows.forEach(r => r.style.backgroundColor = '');
            this.style.backgroundColor = '#e3f2fd';
        });
    });
});

console.log('医院综合管理系统已加载');


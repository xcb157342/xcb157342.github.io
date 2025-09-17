const fs = require('fs');

// 读取数据文件
const data = fs.readFileSync('./timetable/yangxin.txt', 'utf8');

// 按星期分割数据，使用开始标签作为分割点
const daySections = data.split(/(?=$$\[星期[一二三四五六日]\])/).filter(section => section.trim() !== '');

// 检查每个分割段落
daySections.forEach((section, index) => {
});
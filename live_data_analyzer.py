#!/usr/bin/env python3
# coding=utf-8

import json
import os
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd

def load_live_data(data_dir):
    """加载直播数据"""
    messages = []
    stats_file = os.path.join(data_dir, "live_stats.json")
    
    # 加载统计数据
    if os.path.exists(stats_file):
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {}
    
    # 加载消息数据
    for filename in os.listdir(data_dir):
        if filename.startswith("live_messages_") and filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            message = json.loads(line.strip())
                            messages.append(message)
                        except json.JSONDecodeError:
                            continue
    
    return messages, stats

def analyze_messages(messages):
    """分析消息数据"""
    analysis = {
        'total_messages': len(messages),
        'message_types': Counter(),
        'user_activity': Counter(),
        'gift_analysis': defaultdict(int),
        'time_analysis': defaultdict(int),
        'top_chatters': Counter(),
        'top_gifters': Counter(),
        'gift_timeline': []
    }
    
    for msg in messages:
        msg_type = msg.get('type', 'unknown')
        data = msg.get('data', {})
        timestamp = msg.get('timestamp', '')
        
        # 统计消息类型
        analysis['message_types'][msg_type] += 1
        
        # 统计用户活动
        if 'user_id' in data:
            analysis['user_activity'][data['user_id']] += 1
        
        # 分析礼物
        if msg_type == 'gift':
            gift_name = data.get('gift_name', '')
            giver_id = data.get('giver_id', '')
            combo_count = data.get('combo_count', 0)
            
            if gift_name:
                analysis['gift_analysis'][gift_name] += combo_count
            if giver_id:
                analysis['top_gifters'][giver_id] += combo_count
                
            analysis['gift_timeline'].append({
                'timestamp': timestamp,
                'gift_name': gift_name,
                'giver_id': giver_id,
                'combo_count': combo_count
            })
        
        # 分析聊天
        if msg_type == 'message':
            user_id = data.get('user_id', '')
            if user_id:
                analysis['top_chatters'][user_id] += 1
        
        # 时间分析（按小时）
        if timestamp:
            try:
                hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
                analysis['time_analysis'][hour] += 1
            except:
                pass
    
    return analysis

def generate_report(analysis, stats, output_file=None):
    """生成分析报告"""
    report = []
    
    report.append("=" * 60)
    report.append("📊 抖音直播数据分析报告")
    report.append("=" * 60)
    
    # 基本信息
    if stats:
        report.append(f"⏰ 开始时间: {stats.get('start_time', 'N/A')}")
        report.append(f"⏰ 结束时间: {stats.get('end_time', 'N/A')}")
        report.append(f"👥 独立用户数: {len(stats.get('unique_users', []))}")
    
    report.append(f"💬 总消息数: {analysis['total_messages']}")
    report.append("")
    
    # 消息类型统计
    report.append("📈 消息类型统计:")
    for msg_type, count in analysis['message_types'].most_common():
        percentage = (count / analysis['total_messages']) * 100
        report.append(f"  {msg_type}: {count} ({percentage:.1f}%)")
    report.append("")
    
    # 最活跃用户
    if analysis['top_chatters']:
        report.append("💬 最活跃聊天用户 (前10名):")
        for user_id, count in analysis['top_chatters'].most_common(10):
            report.append(f"  {user_id}: {count}条消息")
        report.append("")
    
    # 礼物分析
    if analysis['gift_analysis']:
        report.append("🎁 礼物统计:")
        for gift_name, count in analysis['gift_analysis'].most_common(10):
            report.append(f"  {gift_name}: {count}个")
        report.append("")
        
        if analysis['top_gifters']:
            report.append("🎁 最大礼物贡献者 (前10名):")
            for user_id, count in analysis['top_gifters'].most_common(10):
                report.append(f"  {user_id}: {count}个礼物")
            report.append("")
    
    # 时间分布
    if analysis['time_analysis']:
        report.append("⏰ 消息时间分布 (按小时):")
        for hour in sorted(analysis['time_analysis'].keys()):
            count = analysis['time_analysis'][hour]
            bar = "█" * (count // max(analysis['time_analysis'].values()) * 20)
            report.append(f"  {hour:02d}:00 {bar} {count}")
        report.append("")
    
    # 用户活跃度分析
    if analysis['user_activity']:
        active_users = len([u for u, c in analysis['user_activity'].items() if c > 1])
        total_users = len(analysis['user_activity'])
        report.append(f"👥 用户活跃度: {active_users}/{total_users} 用户发送了多条消息")
        report.append("")
    
    report.append("=" * 60)
    
    # 输出报告
    report_text = "\n".join(report)
    print(report_text)
    
    # 保存到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"📄 报告已保存到: {output_file}")
    
    return report_text

def export_to_excel(analysis, stats, output_file):
    """导出数据到Excel"""
    try:
        # 创建Excel写入器
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # 消息类型统计
            msg_types_df = pd.DataFrame(list(analysis['message_types'].items()), 
                                      columns=['消息类型', '数量'])
            msg_types_df.to_excel(writer, sheet_name='消息类型统计', index=False)
            
            # 最活跃聊天用户
            if analysis['top_chatters']:
                chatters_df = pd.DataFrame(list(analysis['top_chatters'].most_common(20)), 
                                         columns=['用户ID', '消息数量'])
                chatters_df.to_excel(writer, sheet_name='最活跃用户', index=False)
            
            # 礼物统计
            if analysis['gift_analysis']:
                gifts_df = pd.DataFrame(list(analysis['gift_analysis'].most_common(20)), 
                                      columns=['礼物名称', '数量'])
                gifts_df.to_excel(writer, sheet_name='礼物统计', index=False)
            
            # 礼物贡献者
            if analysis['top_gifters']:
                gifters_df = pd.DataFrame(list(analysis['top_gifters'].most_common(20)), 
                                        columns=['用户ID', '礼物数量'])
                gifters_df.to_excel(writer, sheet_name='礼物贡献者', index=False)
            
            # 时间分布
            if analysis['time_analysis']:
                time_df = pd.DataFrame(list(analysis['time_analysis'].items()), 
                                     columns=['小时', '消息数量'])
                time_df = time_df.sort_values('小时')
                time_df.to_excel(writer, sheet_name='时间分布', index=False)
            
            # 礼物时间线
            if analysis['gift_timeline']:
                timeline_df = pd.DataFrame(analysis['gift_timeline'])
                timeline_df.to_excel(writer, sheet_name='礼物时间线', index=False)
        
        print(f"📊 Excel文件已保存到: {output_file}")
        
    except ImportError:
        print("❌ 需要安装pandas和openpyxl: pip install pandas openpyxl")
    except Exception as e:
        print(f"❌ 导出Excel失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='抖音直播数据分析工具')
    parser.add_argument('data_dir', help='直播数据目录')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    parser.add_argument('--excel', help='导出Excel文件路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"❌ 数据目录不存在: {args.data_dir}")
        return
    
    print(f"📂 加载数据目录: {args.data_dir}")
    
    # 加载数据
    messages, stats = load_live_data(args.data_dir)
    
    if not messages:
        print("❌ 没有找到消息数据")
        return
    
    print(f"✅ 加载了 {len(messages)} 条消息")
    
    # 分析数据
    print("🔍 分析数据中...")
    analysis = analyze_messages(messages)
    
    # 生成报告
    report_file = args.output or os.path.join(args.data_dir, "analysis_report.txt")
    generate_report(analysis, stats, report_file)
    
    # 导出Excel
    if args.excel:
        export_to_excel(analysis, stats, args.excel)
    elif not args.excel and len(messages) > 0:
        excel_file = os.path.join(args.data_dir, "live_analysis.xlsx")
        export_to_excel(analysis, stats, excel_file)

if __name__ == '__main__':
    main()


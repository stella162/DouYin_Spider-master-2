#!/usr/bin/env python3
# coding=utf-8
# python live_monitor_with_save.py 900013148868 --save-path "my_live_data" --format csv

import sys
import os
import argparse
import json
import time
import csv
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dy_live.server import DouyinLive
import utils.common_util as common_util

class LiveMonitorWithSave(DouyinLive):
    def __init__(self, live_id, auth_, save_path=None, output_format='json'):
        super().__init__(live_id, auth_)
        self.save_path = save_path or f"live_data_{live_id}"
        self.output_format = output_format.lower()
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 根据格式设置文件扩展名
        if self.output_format == 'csv':
            self.data_file = os.path.join(self.save_path, f"live_messages_{self.timestamp}.csv")
            self.stats_file = os.path.join(self.save_path, "live_stats.csv")
        elif self.output_format == 'xlsx':
            self.data_file = os.path.join(self.save_path, f"live_messages_{self.timestamp}.xlsx")
            self.stats_file = os.path.join(self.save_path, "live_stats.xlsx")
        else:  # json (default)
            self.data_file = os.path.join(self.save_path, f"live_messages_{self.timestamp}.json")
            self.stats_file = os.path.join(self.save_path, "live_stats.json")
        
        # 创建保存目录
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        # 统计数据
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'total_messages': 0,
            'total_gifts': 0,
            'total_likes': 0,
            'total_enters': 0,
            'total_follows': 0,
            'unique_users': set(),
            'gift_list': [],
            'top_gifters': {},
            'top_chatters': {}
        }
        
        # 存储所有消息用于批量保存
        self.messages = []
        
        # 定期保存计数器
        self.save_counter = 0
        self.save_interval = 10  # 每10条消息保存一次
        
        print(f"📁 数据保存路径: {self.save_path}")
        print(f"📄 消息文件: {self.data_file}")

    def save_message(self, message_type, data):
        """保存消息到文件"""
        message = {
            'timestamp': datetime.now().isoformat(),
            'type': message_type,
            'data': data
        }
        
        # 添加到消息列表
        self.messages.append(message)
        self.save_counter += 1
        
        # 如果是JSON格式，立即保存
        if self.output_format == 'json':
            with open(self.data_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message, ensure_ascii=False) + '\n')
        
        # 如果是CSV/XLSX格式，定期保存
        elif self.output_format in ['csv', 'xlsx'] and self.save_counter >= self.save_interval:
            self.save_messages_to_file()
            self.save_counter = 0
        
        # 更新统计
        self.update_stats(message_type, data)

    def update_stats(self, message_type, data):
        """更新统计数据"""
        self.stats['total_messages'] += 1
        
        if message_type == 'message':
            user_id = data.get('user_id', '')
            if user_id:
                self.stats['unique_users'].add(user_id)
                self.stats['top_chatters'][user_id] = self.stats['top_chatters'].get(user_id, 0) + 1
                
        elif message_type == 'gift':
            self.stats['total_gifts'] += 1
            gift_name = data.get('gift_name', '')
            giver_id = data.get('giver_id', '')
            combo_count = data.get('combo_count', 0)
            
            if gift_name:
                self.stats['gift_list'].append({
                    'gift_name': gift_name,
                    'giver_id': giver_id,
                    'combo_count': combo_count,
                    'timestamp': datetime.now().isoformat()
                })
            
            if giver_id:
                self.stats['top_gifters'][giver_id] = self.stats['top_gifters'].get(giver_id, 0) + combo_count
                
        elif message_type == 'like':
            self.stats['total_likes'] += 1
        elif message_type == 'enter':
            self.stats['total_enters'] += 1
        elif message_type == 'follow':
            self.stats['total_follows'] += 1

    def save_messages_to_file(self):
        """保存消息到文件（CSV/XLSX格式）"""
        if not self.messages:
            return
            
        if self.output_format == 'csv':
            self._save_messages_csv()
        elif self.output_format == 'xlsx':
            self._save_messages_xlsx()
    
    def _save_messages_csv(self):
        """保存消息为CSV格式"""
        if not self.messages:
            return
            
        # 准备CSV数据
        csv_data = []
        for msg in self.messages:
            # 基础字段
            row = {
                'timestamp': msg['timestamp'],
                'message_type': msg['type']
            }
            
            # 根据消息类型添加特定字段
            data = msg['data']
            if msg['type'] == 'message':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'content': data.get('content', ''),
                    'user_level': data.get('user_level', ''),
                    # 其他字段设为空
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'gift':
                row.update({
                    'giver_id': data.get('giver_id', ''),
                    'giver_nickname': data.get('giver_nickname', ''),
                    'gift_name': data.get('gift_name', ''),
                    'combo_count': data.get('combo_count', ''),
                    'receiver_id': data.get('receiver_id', ''),
                    'receiver_nickname': data.get('receiver_nickname', ''),
                    # 其他字段设为空
                    'user_id': '',
                    'nickname': '',
                    'content': '',
                    'user_level': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'like':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'like_count': data.get('count', ''),
                    'like_total': data.get('total', ''),
                    # 其他字段设为空
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'member_count': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'enter':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'member_count': data.get('member_count', ''),
                    # 其他字段设为空
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'follow':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'follow_count': data.get('follow_count', ''),
                    # 其他字段设为空
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'room_stats':
                row.update({
                    'display_short': data.get('display_short', ''),
                    'display_middle': data.get('display_middle', ''),
                    'display_long': data.get('display_long', ''),
                    'room_total': data.get('total', ''),
                    # 其他字段设为空
                    'user_id': '',
                    'nickname': '',
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'follow_count': ''
                })
            
            csv_data.append(row)
        
        # 写入CSV文件
        if csv_data:
            # 定义固定的字段顺序
            fieldnames = [
                'timestamp', 'message_type', 'user_id', 'nickname', 'content', 'user_level',
                'giver_id', 'giver_nickname', 'gift_name', 'combo_count', 'receiver_id', 'receiver_nickname',
                'like_count', 'like_total', 'member_count', 'follow_count',
                'display_short', 'display_middle', 'display_long', 'room_total'
            ]
            
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
    
    def _save_messages_xlsx(self):
        """保存消息为XLSX格式"""
        if not self.messages:
            return
            
        # 准备数据（与CSV相同）
        csv_data = []
        for msg in self.messages:
            # 基础字段
            row = {
                'timestamp': msg['timestamp'],
                'message_type': msg['type']
            }
            
            # 根据消息类型添加特定字段
            data = msg['data']
            if msg['type'] == 'message':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'content': data.get('content', ''),
                    'user_level': data.get('user_level', ''),
                    # 其他字段设为空
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'gift':
                row.update({
                    'giver_id': data.get('giver_id', ''),
                    'giver_nickname': data.get('giver_nickname', ''),
                    'gift_name': data.get('gift_name', ''),
                    'combo_count': data.get('combo_count', ''),
                    'receiver_id': data.get('receiver_id', ''),
                    'receiver_nickname': data.get('receiver_nickname', ''),
                    # 其他字段设为空
                    'user_id': '',
                    'nickname': '',
                    'content': '',
                    'user_level': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'like':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'like_count': data.get('count', ''),
                    'like_total': data.get('total', ''),
                    # 其他字段设为空
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'member_count': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'enter':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'member_count': data.get('member_count', ''),
                    # 其他字段设为空
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'follow_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'follow':
                row.update({
                    'user_id': data.get('user_id', ''),
                    'nickname': data.get('nickname', ''),
                    'follow_count': data.get('follow_count', ''),
                    # 其他字段设为空
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'display_short': '',
                    'display_middle': '',
                    'display_long': '',
                    'room_total': ''
                })
            elif msg['type'] == 'room_stats':
                row.update({
                    'display_short': data.get('display_short', ''),
                    'display_middle': data.get('display_middle', ''),
                    'display_long': data.get('display_long', ''),
                    'room_total': data.get('total', ''),
                    # 其他字段设为空
                    'user_id': '',
                    'nickname': '',
                    'content': '',
                    'user_level': '',
                    'giver_id': '',
                    'giver_nickname': '',
                    'gift_name': '',
                    'combo_count': '',
                    'receiver_id': '',
                    'receiver_nickname': '',
                    'like_count': '',
                    'like_total': '',
                    'member_count': '',
                    'follow_count': ''
                })
            
            csv_data.append(row)
        
        # 写入XLSX文件
        if csv_data:
            # 定义固定的字段顺序
            fieldnames = [
                'timestamp', 'message_type', 'user_id', 'nickname', 'content', 'user_level',
                'giver_id', 'giver_nickname', 'gift_name', 'combo_count', 'receiver_id', 'receiver_nickname',
                'like_count', 'like_total', 'member_count', 'follow_count',
                'display_short', 'display_middle', 'display_long', 'room_total'
            ]
            
            # 确保所有行都有相同的字段
            for row in csv_data:
                for field in fieldnames:
                    if field not in row:
                        row[field] = ''
            
            df = pd.DataFrame(csv_data, columns=fieldnames)
            df.to_excel(self.data_file, index=False, engine='openpyxl')

    def save_stats(self):
        """保存统计数据"""
        # 转换set为list以便JSON序列化
        stats_to_save = self.stats.copy()
        stats_to_save['unique_users'] = list(self.stats['unique_users'])
        stats_to_save['end_time'] = datetime.now().isoformat()
        
        if self.output_format == 'json':
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_to_save, f, ensure_ascii=False, indent=2)
        elif self.output_format == 'csv':
            self._save_stats_csv(stats_to_save)
        elif self.output_format == 'xlsx':
            self._save_stats_xlsx(stats_to_save)
    
    def _save_stats_csv(self, stats_data):
        """保存统计为CSV格式"""
        # 基础统计
        basic_stats = [
            {'metric': 'start_time', 'value': stats_data['start_time']},
            {'metric': 'end_time', 'value': stats_data['end_time']},
            {'metric': 'total_messages', 'value': stats_data['total_messages']},
            {'metric': 'total_gifts', 'value': stats_data['total_gifts']},
            {'metric': 'total_likes', 'value': stats_data['total_likes']},
            {'metric': 'total_enters', 'value': stats_data['total_enters']},
            {'metric': 'total_follows', 'value': stats_data['total_follows']},
            {'metric': 'unique_users_count', 'value': len(stats_data['unique_users'])}
        ]
        
        with open(self.stats_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
            writer.writeheader()
            writer.writerows(basic_stats)
    
    def _save_stats_xlsx(self, stats_data):
        """保存统计为XLSX格式"""
        # 基础统计
        basic_stats = [
            {'metric': 'start_time', 'value': stats_data['start_time']},
            {'metric': 'end_time', 'value': stats_data['end_time']},
            {'metric': 'total_messages', 'value': stats_data['total_messages']},
            {'metric': 'total_gifts', 'value': stats_data['total_gifts']},
            {'metric': 'total_likes', 'value': stats_data['total_likes']},
            {'metric': 'total_enters', 'value': stats_data['total_enters']},
            {'metric': 'total_follows', 'value': stats_data['total_follows']},
            {'metric': 'unique_users_count', 'value': len(stats_data['unique_users'])}
        ]
        
        df = pd.DataFrame(basic_stats)
        df.to_excel(self.stats_file, index=False, engine='openpyxl')

    def on_message(self, ws, message):
        """重写消息处理函数，添加保存功能"""
        try:
            import gzip
            import static.Live_pb2 as Live_pb2
            
            frame = Live_pb2.PushFrame()
            frame.ParseFromString(message)
            origin_bytes = gzip.decompress(frame.payload)
            response = Live_pb2.LiveResponse()
            response.ParseFromString(origin_bytes)
            
            if response.needAck:
                s = Live_pb2.PushFrame()
                s.payloadType = "ack"
                s.payload = response.internalExt.encode('utf-8')
                s.logId = frame.logId
                ws.send(s.SerializeToString(), opcode=0x02)
                
            for item in response.messagesList:
                if item.method == 'WebcastGiftMessage':
                    message_obj = Live_pb2.GiftMessage()
                    message_obj.ParseFromString(item.payload)
                    
                    # 显示消息
                    print(f'\033[1;37;40m[礼物]SEC_UID = {message_obj.user.sec_uid} - {message_obj.user.nickname}\033[m 送给 \033[1;37;40m{message_obj.toUser.sec_uid} - {message_obj.toUser.nickname}\033[m \033[4;30;44m{message_obj.gift.name}\033[m x {message_obj.comboCount}')
                    
                    # 保存数据
                    self.save_message('gift', {
                        'giver_id': message_obj.user.sec_uid,
                        'giver_nickname': message_obj.user.nickname,
                        'receiver_id': message_obj.toUser.sec_uid,
                        'receiver_nickname': message_obj.toUser.nickname,
                        'gift_name': message_obj.gift.name,
                        'combo_count': message_obj.comboCount
                    })
                    
                elif item.method == "WebcastChatMessage":
                    message_obj = Live_pb2.ChatMessage()
                    message_obj.ParseFromString(item.payload)
                    
                    # 显示消息
                    print(f'\033[1;37;40m[消息]SEC_UID = {message_obj.user.sec_uid} - {message_obj.user.nickname}\033[m : \033[4;30;44m{message_obj.content}\033[m')
                    
                    # 保存数据
                    self.save_message('message', {
                        'user_id': message_obj.user.sec_uid,
                        'nickname': message_obj.user.nickname,
                        'content': message_obj.content
                    })
                    
                elif item.method == "WebcastMemberMessage":
                    message_obj = Live_pb2.MemberMessage()
                    message_obj.ParseFromString(item.payload)
                    
                    # 显示消息
                    print(f'\033[1;37;40m[进入]SEC_UID = {message_obj.user.sec_uid} - {message_obj.user.nickname}\033[m 进入直播间')
                    
                    # 保存数据
                    self.save_message('enter', {
                        'user_id': message_obj.user.sec_uid,
                        'nickname': message_obj.user.nickname,
                        'member_count': message_obj.memberCount
                    })
                    
                elif item.method == "WebcastLikeMessage":
                    message_obj = Live_pb2.LikeMessage()
                    message_obj.ParseFromString(item.payload)
                    
                    # 显示消息
                    print(f'\033[1;37;40m[点赞]SEC_UID = {message_obj.user.sec_uid} - {message_obj.user.nickname}\033[m 点赞了 {message_obj.count} 次')
                    print(f'\033[1;37;40m[点赞]点赞总数 = {message_obj.total}\033[m')
                    
                    # 保存数据
                    self.save_message('like', {
                        'user_id': message_obj.user.sec_uid,
                        'nickname': message_obj.user.nickname,
                        'count': message_obj.count,
                        'total': message_obj.total
                    })
                    
                elif item.method == "WebcastSocialMessage":
                    message_obj = Live_pb2.SocialMessage()
                    message_obj.ParseFromString(item.payload)
                    
                    if message_obj.action == 1:
                        # 显示消息
                        print(f'\033[1;37;40m[关注]SEC_UID = {message_obj.user.sec_uid} - {message_obj.user.nickname}\033[m 关注主播')
                        
                        # 保存数据
                        self.save_message('follow', {
                            'user_id': message_obj.user.sec_uid,
                            'nickname': message_obj.user.nickname,
                            'follow_count': message_obj.followCount
                        })
                        
                elif item.method == "WebcastRoomStatsMessage":
                    message_obj = Live_pb2.RoomStatsMessage()
                    message_obj.ParseFromString(item.payload)
                    
                    # 显示消息
                    print(f'\033[1;37;40m[房间信息] {message_obj.displayLong}')
                    
                    # 保存数据
                    self.save_message('room_stats', {
                        'display_short': message_obj.displayShort,
                        'display_middle': message_obj.displayMiddle,
                        'display_long': message_obj.displayLong,
                        'total': message_obj.total
                    })
                    
        except Exception as e:
            print('error')
            print(str(e))

    def on_close(self, ws, close_status_code, close_msg):
        """重写关闭函数，保存统计数据"""
        print("\033[31m### closed ###")
        print(f"status_code: {close_status_code}, msg: {close_msg}")
        print("### ===closed=== ###\033[m")
        
        # 保存消息数据（CSV/XLSX格式）
        if self.output_format in ['csv', 'xlsx']:
            self.save_messages_to_file()
            print(f"📄 消息数据已保存到: {self.data_file}")
        
        # 保存统计数据
        self.save_stats()
        print(f"📊 统计数据已保存到: {self.stats_file}")
        
        # 显示统计摘要
        self.show_summary()

    def show_summary(self):
        """显示统计摘要"""
        print("\n" + "="*50)
        print("📊 直播监听统计摘要")
        print("="*50)
        print(f"⏰ 开始时间: {self.stats['start_time']}")
        print(f"⏰ 结束时间: {datetime.now().isoformat()}")
        print(f"💬 总消息数: {self.stats['total_messages']}")
        print(f"🎁 总礼物数: {self.stats['total_gifts']}")
        print(f"👍 总点赞数: {self.stats['total_likes']}")
        print(f"🚪 总进入数: {self.stats['total_enters']}")
        print(f"❤️ 总关注数: {self.stats['total_follows']}")
        print(f"👥 独立用户数: {len(self.stats['unique_users'])}")
        
        if self.stats['top_chatters']:
            top_chatter = max(self.stats['top_chatters'].items(), key=lambda x: x[1])
            print(f"💬 最活跃用户: {top_chatter[0]} ({top_chatter[1]}条消息)")
        
        if self.stats['top_gifters']:
            top_gifter = max(self.stats['top_gifters'].items(), key=lambda x: x[1])
            print(f"🎁 最大礼物贡献者: {top_gifter[0]} ({top_gifter[1]}个礼物)")
        
        print("="*50)

def extract_live_id(url_or_id):
    """从抖音直播URL或直接ID中提取直播间ID"""
    if url_or_id.isdigit():
        return url_or_id
    
    if 'live.douyin.com' in url_or_id:
        parsed = urlparse(url_or_id)
        path = parsed.path.strip('/')
        if path:
            return path.split('?')[0]
    
    return url_or_id

def main():
    parser = argparse.ArgumentParser(description='抖音直播监听程序（带数据保存）')
    parser.add_argument('live_id', help='直播间ID或URL')
    parser.add_argument('--save-path', help='数据保存路径（可选）', default=None)
    parser.add_argument('--format', help='输出格式：json, csv, xlsx（默认：json）', 
                       choices=['json', 'csv', 'xlsx'], default='json')
    
    args = parser.parse_args()
    
    # 提取直播间ID
    live_id = extract_live_id(args.live_id)
    print(f"🎯 监听直播间ID: {live_id}")
    
    # 加载认证信息
    try:
        common_util.load_env()
        auth = common_util.dy_live_auth
        
        if not auth or not auth.cookie:
            print("❌ 直播认证配置错误！")
            print("\n📋 请确保 .env 文件中配置了 DY_LIVE_COOKIES")
            return
        
        print("✅ 认证配置成功！")
        
        # 创建带保存功能的直播监听对象
        live = LiveMonitorWithSave(live_id, auth, args.save_path, args.format)
        
        print(f"🚀 开始监听直播间 {live_id}...")
        print(f"📄 输出格式: {args.format.upper()}")
        print("📱 监听内容：")
        print("  - [进入] 用户进入直播间")
        print("  - [消息] 用户发送弹幕")
        print("  - [礼物] 用户送出礼物")
        print("  - [点赞] 用户点赞")
        print("  - [关注] 用户关注主播")
        print("  - [房间信息] 直播间统计信息")
        print(f"\n💾 所有数据将自动保存为 {args.format.upper()} 格式")
        print("按 Ctrl+C 停止监听\n")
        
        # 开始监听
        live.start_ws()
        
    except KeyboardInterrupt:
        print("\n\n👋 监听已停止")
        if 'live' in locals():
            # 保存消息数据（CSV/XLSX格式）
            if live.output_format in ['csv', 'xlsx']:
                live.save_messages_to_file()
                print(f"📄 消息数据已保存到: {live.data_file}")
            
            live.save_stats()
            live.show_summary()
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    main()


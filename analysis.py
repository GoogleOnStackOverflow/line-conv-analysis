#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import operator
import os
import argparse
import datetime
import re

def is_conv(text):
    parts = len(text.split('\t'))
    return parts == 1 or parts == 3

def is_invite(text):
    return '邀請' in text and '加入' in text

def is_cancel_invite(text):
    return '的邀請' in text and '已取消' in text

def is_kicked(text):
    return '已讓' in text and '退出群組' in text

def is_leave(text):
    return '已退出群組' in text

def is_join(text):
    return '加入聊天' in text

class ConversationData:
    def __init__(self, path):
        self.context = {}
        self.users = {}
        self.join = []
        self.leave = []

        with open(path, 'r') as f:
            text = f.read()
            text = text.split('\n')
        
        date_re = re.compile('^[0-9]+/[0-9]+/[0-9]+....')
        conv_start = re.compile('^[0-9]+:[0-9]+\t.')
        
        today = ''
        last_usr = ''
        last_time = ''
        
        for line in text:
            if date_re.match(line):
                today = datetime.datetime.strptime(line[:10], '%Y/%m/%d').strftime('%Y%m%d')
                if today not in self.context.keys():
                    self.context[today] = {}
            elif conv_start.match(line) and is_conv(line):
                last_time = now = line.split('\t')[0]
                last_usr = usr = line.split('\t')[1]
                content = line.split('\t')[2]

                if usr not in self.context[today].keys():
                    self.context[today][usr] = []
                self.context[today][usr].append((now, content))
            elif today != '' and last_usr != '' and last_time != '' and is_conv(line):
                self.context[today][last_usr].append((last_time, line))
            elif is_join(line):
                now = line.split('\t')[0]
                content = line.split('\t')[1]
                self.join.append(('{} {}'.format(today, now), content[:-len('加入聊天')-1]))
            elif is_leave(line):
                now = line.split('\t')[0]
                content = line.split('\t')[1]
                self.leave.append(('{} {}'.format(today, now), content[:-len('已退出群組')-1]))
        
    def get_conv_leaderboard(self, start, end):
        start_date = datetime.datetime.strptime(start, '%Y%m%d')
        end_date = datetime.datetime.strptime(end, '%Y%m%d')

        for day in self.context.keys():
            today = datetime.datetime.strptime(day, '%Y%m%d')
            if today >= start_date and today <= end_date:
                for usr in self.context[day].keys():
                    if usr not in self.users.keys():
                        self.users[usr] = 0
                    self.users[usr] = self.users[usr] + len(self.context[day][usr])

        return sorted(self.users.items(), key=operator.itemgetter(1), reverse = True)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Generate warrant/option scanning settings')
    parser.add_argument('-i', '--InfoPath', dest='info_path',
                        help='The path to the info file', default=None, required=True)

    parser.add_argument('-s', '--StartDate', dest='start_date',
                        help='First date to be analysis', default=None, required=True)
    parser.add_argument('-e', '--EndDate', dest='end_date',
                        help='Last date to be analysis', default=None, required=True)

    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    info_path = os.path.abspath(args.info_path)

    conv_data = ConversationData(info_path)
    board = conv_data.get_conv_leaderboard(args.start_date, args.end_date)

    print('對話次數')
    for usr_data in board:
        print('{}\t| {}'.format(usr_data[1], usr_data[0]))
    
    print('\n加入名單')
    for join in conv_data.join:
        print('{}\t| {}'.format(join[0], join[1]))

    print('\n退出名單')
    for leave in conv_data.leave:
        print('{}\t| {}'.format(leave[0], leave[1]))

if __name__ == "__main__":
    main(sys.argv[1:])
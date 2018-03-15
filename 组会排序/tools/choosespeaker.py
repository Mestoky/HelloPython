'''每周运行一次，选出本周speaker，一轮之中不出现重复speaker；对于两轮之间，同一个speaker两次之间至少隔两周'''

import random
import time
import configparser


def initial_write(config):
    config.add_section('all')
    config.set('all', 'candidates', 'A,B,C,D,E,F,G,H,I,J,K,L,M,N')
    config.add_section('left')
    config.set('left', 'candidates', '')
    config.add_section('record')
    config.set('record', 'candidates', '')
    with open('members.ini', 'w', encoding='UTF-8') as configfile:
        config.write(configfile)


def write_data(name, info, config):
    config.set(name, 'candidates', ','.join(info))
    with open('members.ini', 'w', encoding='UTF-8') as configfile:
        config.write(configfile)


def read_data(name, config):
    content = config.get(name, 'candidates')
    if content:
        return content.split(',')
    else:
        return []


def choose_speaker(li, rec):
    speaker = random.choice(li)
    while speaker in rec:
        speaker = random.choice(li)
    return speaker


def make_decisions():
    random.seed(time.time())
    config = configparser.ConfigParser()
    if not config.read('members.ini', encoding='UTF-8'):
        initial_write(config)
    all_can = read_data('all', config)
    if not read_data('left', config):
        left_can = all_can
    else:
        left_can = read_data('left', config)
    rec_can = read_data('record', config)
    speaker = choose_speaker(left_can, rec_can)
    print('下周组会轮到你：%s' % speaker)
    rec_can.append(speaker)
    if len(rec_can) > 2:
        rec_can.pop(0)
    write_data('record', rec_can, config)
    left_can.remove(speaker)
    if not left_can:
        left_can = all_can
    write_data('left', left_can, config)
    return '下周组会轮到你：%s@%s' % (speaker, speaker)


def initial():
    write_data('record', '')
    write_data('left', '')


if __name__ == '__main__':
    make_decisions()

import configparser
import random
import time


class Data:
    """公用数据"""
    config = configparser.ConfigParser()
    filename = ''
    all = []
    left = []
    rec = []


def read_config(filename, default=None):
    """生成config并读取/初始化ini文件"""
    Data.filename = filename
    if not default:
        default = ['A', 'B', 'C', 'D', 'E', 'F']
    if Data.config.read(Data.filename, encoding='UTF-8'):
        Data.all = Data.config.get('all', 'candidates').split(',')
        Data.left = Data.config.get('left', 'candidates').split(',')
        Data.rec = Data.config.get('record', 'candidates').split(',')
    else:
        Data.all = default[:]
        Data.left = default[:]
        Data.config.add_section('all')
        Data.config.add_section('left')
        Data.config.add_section('record')
        Data.config.set('all', 'candidates', ','.join(Data.all))


def choose_speaker(protect=2):
    """从演讲候选人中选出演讲人"""
    assert Data.left and Data.all, '未进行初始化！'
    random.seed(time.time())
    speaker = random.choice(list(set(Data.left) - set(Data.rec)))
    Data.left.remove(speaker)
    Data.rec.append(speaker)
    if len(Data.left) == 0:
        Data.left.extend(Data.all)
    if len(Data.rec) > protect:
        Data.rec.pop(0)
    return speaker


def save_data():
    """将候选人列表写入文件"""
    assert Data.filename, '未设置文件名！'
    Data.config.set('left', 'candidates', ','.join(Data.left))
    Data.config.set('record', 'candidates', ','.join(Data.rec))
    with open(Data.filename, 'w', encoding='UTF-8') as file:
        Data.config.write(file)


if __name__ == '__main__':
    read_config('members.ini')
    print(choose_speaker())
    save_data()

import configparser

config = configparser.ConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
config.add_section('all')
config.set('all', 'candidates', '胡康,贺克伦,苟星,马欢,张孟起,辛永琳')
config.add_section('left')
config.set('left', 'candidates', '')
config.add_section('record')
config.set('record', 'candidates', '')

# Writing our configuration file to 'example.cfg'
with open('members.ini', 'w', encoding='UTF-8') as configfile:
    config.write(configfile)

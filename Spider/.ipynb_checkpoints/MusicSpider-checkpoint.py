import requests
from lxml import etree
from selenium import webdriver
import re
import langid
import jieba
import MeCab
import os


def getSongList(id):
    song_name_list = []
    song_link_list = []
    song_num_list = []
    song_singer_list = []

    url = "https://music.163.com/#/user/songs/rank?id=" + str(id)

    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    driver = webdriver.Chrome(chrome_options=options, executable_path='../chromedriver.exe')
    driver.get(url=url)
    driver.switch_to.frame('contentFrame')
    page = driver.page_source
    page_html = etree.HTML(page)
    song_label_list = page_html.xpath('/html/body/div[3]/div/div[2]/div/div[1]/ul/li')

    for i, li in enumerate(song_label_list):
        song_name = li.xpath('./div[2]/div[1]/div/span/a/b/text()')[0]
        song_name_list.append(song_name)

        song_link = li.xpath('./div[2]/div[1]/div/span/a/@href')
        song_link_list.append(song_link[0][9:])

        song_num = li.xpath('./div[3]/span/@style')
        song_num_list.append(song_num[0][6:-1])

        song_singer = li.xpath('./div[2]/div[1]/div/span/span/span/@title')
        song_singer_list.append(song_singer[0])
        print(song_singer_list)

    return song_link_list, song_name_list, song_num_list, song_singer_list

def getLyricsByID(song_link_list):
    """
    将歌词写入一个txt文件
    :param song_link_list: getSongList的第一个返回值
    :return: None
    """
    with open('lyrics.txt', 'a') as f:
        for link in song_link_list:
            url = 'https://api.imjad.cn/cloudmusic/?type=lyric&id=' + str(link)
            r = requests.get(url)
            result = r.json()
            lyric = result['lrc']['lyric']
            lyrics = re.split('[\n]', lyric)
            for i in lyrics:
                try:
                    index = i.index(']')
                    if len(i[index + 1:]) != 0:
                        f.write(i[index + 1] + '\n')
                except:
                    print('没有找到反括号')

def cutIntoWords(line):
    mecab_tagger = MeCab.Tagger("-Owakati")
    lang = langid.classify(line)[0]
    words = []
    if lang == 'ja':
        words = mecab_tagger.parse(line).split()
    if lang == 'zh':
        words = list(jieba.cut(line))
    if lang == 'en':
        words = line.split()

    return words


def saveWordsFre():
    word_count = {}
    stopwords = []
    path = 'D:/project/JapaneseMusicVisualization/spider/raw'
    for label_dir in os.listdir(path):
        file_path = os.path.join(path, label_dir)
        print(file_path)
        with open(file_path, 'r', encoding='UTF-8') as f:
            for word in f.readlines():
                stopwords.append(word.strip())
    print(stopwords)

    with open('lyrics.txt', 'r') as f:
        for line in f.readlines():
            words = cutIntoWords(line)
            print('words',words)
            for word in words:
                if word in stopwords:
                    continue
                if word in word_count:

                    word_count[word] += 1
                else:
                    word_count[word] = 1

    with open('wordsFre.csv', 'w') as f:
        for key, value in word_count.items():
            f.write(str(key) + ',' + str(value) + '\n')

a, b, numlist, singer = getSongList(514969298)
print(singer)
print(numlist)


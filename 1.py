# -*- coding:utf-8 -*-
import os
import sys
import requests
import datetime
from Crypto.Cipher import AES

reload(sys)
sys.setdefaultencoding('utf-8')


def download(url):
    if 'nsd' not in url:
        print '文件名有误，请检查'
    else:
        headers = {
            'Referer': "http://tts.tmooc.cn/video/showVideo?menuId=672814&version=NSDTN201904",
            "Origin": "http://tts.tmooc.cn",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}

        all_content = requests.get(url, headers=headers).text  # 获取第一层M3U8文件内容
        filename = url.split('/')[3]
        # print all_content
        if "#EXTM3U" not in all_content:
            raise BaseException("非M3U8的链接")

        # if "EXT-X-STREAM-INF" in all_content:  # 第一层
        #     file_line = all_content.split("\n")
        #     for line in file_line:
        #         if '.m3u8' in line:
        #             url = url.rsplit("/", 1)[0] + "/" + line  # 拼出第二层m3u8的URL
        #             all_content = requests.get(url).text

        file_line = all_content.split("\n")

        unknow = True
        key = ""
        for index, line in enumerate(file_line):  # 第二层
            if "#EXT-X-KEY" in line:  # 找解密Key
                method_pos = line.find("METHOD")
                comma_pos = line.find(",")
                method = line[method_pos:comma_pos].split('=')[1]
                print "Decode Method：", method

                uri_pos = line.find("URI")
                quotation_mark_pos = line.rfind('"')
                key_path = line[uri_pos:quotation_mark_pos].split('"')[1]

                key_url = key_path  # 拼出key解密密钥URL
                print key_url
                res = requests.get(key_url, headers=headers)
                key = res.content
                print "key：", key

            if "EXTINF" in line:  # 找ts地址并下载
                unknow = False
                pd_url = file_line[index + 1]  # 拼出ts片段的URL
                print pd_url

                res = requests.get(pd_url, headers=headers)
                c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]

                if len(key):  # AES 解密
                    cryptor = AES.new(key, AES.MODE_CBC, key)
                    with open(os.path.join(download_path, c_fule_name + ".mp4"), 'ab') as f:
                        f.write(cryptor.decrypt(res.content))
                else:
                    with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                        f.write(res.content)
                        f.flush()
        if unknow:
            raise BaseException("未找到对应的下载链接")
        else:
            print "下载完成"
        merge_file(download_path, filename)


def merge_file(path, filename):
    os.chdir(path)
    # cmd = "copy /b * new.tmp"
    cmd = "cat * > new.tmp"
    os.system(cmd)
    os.system('rm *.ts')
    os.system('rm *.mp4')
    os.rename("new.tmp", filename + ".mp4")

    os.system('mv ' + filename + ".mp4" + ' 下载完成/')
    print '当前文件已经完成下载，在download/下载完成中，请注意查收。'


if __name__ == '__main__':
    try:
        download_path = os.getcwd() + "//download"
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        download_path_success = os.getcwd() + "//download//下载完成"
        if not os.path.exists(download_path_success):
            os.mkdir(download_path_success)
        print '请输入要下载的日期文件名：\neg：nsd19060628pm\n'
        filename = raw_input('请输入：')
        print filename
        if filename:
            url = "http://c.it211.com.cn/{}/{}.m3u8".format(filename, filename)
            download(url)
        else:
            print '请输入要下载日期的文件名'
    except:
        print '你TM输入的文件名有问题啊！'

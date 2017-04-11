import http.cookiejar
import re
import urllib.parse
import os
import numpy as np
import scipy.io as sio
import scipy.signal
from PIL import Image
import numpy as ny
import urllib.request
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import time


def get_gpa_message(score):
    sum_credit = 0
    sum_score = 0
    message = ''
    for subject in score:
        message = message + subject['subject'] + '的成绩为：' + subject['score'] + '\n'
        try:
            score_of_subject = float(subject['score'])
        except:
            if subject['score'] == '优秀':
                score_of_subject = 95
            elif subject['score'] == '良好':
                score_of_subject = 85
            elif subject['score'] == '中等':
                score_of_subject = 75
            elif subject['score'] == '及格':
                score_of_subject = 65
            else:
                score_of_subject = 55

        sum_credit += float(subject['credit'])
        sum_score += score_of_subject * float(subject['credit'])
    message += '当前绩点为:' + str((sum_score / sum_credit) / 10 - 5)
    return message


def page_to_list(ScoPage):
    index = re.search(r'课程代码(.*?)</table>', ScoPage, re.I | re.M | re.S).span()
    return re.findall(r'<tr(.*?)</tr>', ScoPage[index[0]:index[1]], re.I | re.M | re.S)


def simply_list(page_list):
    simple_list = []
    subject_list = []
    for x in page_list:
        result = re.findall(r'<td>(.*?)</td>', x, re.I | re.M)
        simple_list.append({'subject': result[1], 'attribute': result[2], 'score': result[3], 'credit': result[7]})
        subject_list.append(result[1])
    return simple_list, subject_list


def get_diff(old_list, new_list, all_score_list):
    new_subject = list(set(new_list).difference(set(old_list)))
    new_score_of_subject = []
    for each_new_subject in new_subject:
        for each_subject_dict in all_score_list:
            if each_new_subject == each_subject_dict['subject']:
                new_score_of_subject.append(each_subject_dict['score'])
    return new_subject, new_score_of_subject


def get_title_message(old_all_list, new_all_list):
    new_info_list, new_subject_list = simply_list(new_all_list)
    old_info_list, old_subject_list = simply_list(old_all_list)
    diff_subject, diff_score = get_diff(old_subject_list, new_subject_list, new_info_list)
    title = '好好学习!  '
    for index in range(len(diff_subject)):
        title += diff_subject[index] + '的成绩为:' + diff_score[index]
    message = get_gpa_message(new_info_list)
    return title, message


def iserror(page):  # 若验证码正确，返回False
    if (re.search(r'验证码不正确！！', page, re.I | re.M)) is None:
        return False
    else:
        return True


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_message(mes, from_addr, password, to_addr, student_name, title):
    smtp_server = "smtp.163.com"
    msg = MIMEText(mes, 'plain', 'utf-8')
    msg['From'] = _format_addr('成绩自动查询 <%s>' % from_addr)
    msg['To'] = _format_addr(student_name + '同学 <%s>' % to_addr)
    msg['Subject'] = Header(title, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


def getVIEW(Page):
    view = r'name="__VIEWSTATE" value="(.+)" '
    view = re.compile(view)
    return view.findall(Page)[0]


def photo_split(im):
    im = im[0:20, :]
    im = scipy.signal.wiener(im)
    im = im > (255 * 0.4)
    s1 = im[:, 4:17]
    s2 = im[:, 17:30]
    s3 = im[:, 30:43]
    s4 = im[:, 43:56]
    s1 = np.transpose(s1).reshape((1, 260))
    s2 = np.transpose(s2).reshape((1, 260))
    s3 = np.transpose(s3).reshape((1, 260))
    s4 = np.transpose(s4).reshape((1, 260))
    s = np.concatenate((s1, s2, s3, s4), axis=0)
    return s


def sigmoid(z):
    z = np.matrix(z)
    g = 1 / (1 + np.exp(-z))
    return g


def predict(Theta1, Theta2, Theta3, X):
    X = np.matrix(X)
    Theta1 = np.matrix(Theta1)
    Theta2 = np.matrix(Theta2)
    Theta3 = np.matrix(Theta3)
    m = X.shape[0]
    h1 = sigmoid(((np.concatenate((np.ones((m, 1)), X), axis=1)) * (np.transpose(Theta1))))
    h2 = sigmoid(((np.concatenate((np.ones((m, 1)), h1), axis=1)) * (np.transpose(Theta2))))
    h3 = sigmoid(((np.concatenate((np.ones((m, 1)), h2), axis=1)) * (np.transpose(Theta3))))
    p1 = np.ndarray.argmax(h3[0, :])
    p2 = np.ndarray.argmax(h3[1, :])
    p3 = np.ndarray.argmax(h3[2, :])
    p4 = np.ndarray.argmax(h3[3, :])
    return p1, p2, p3, p4


def openimage(fullpath):
    im = ny.array(Image.open(fullpath).convert('L'), 'f')
    return im


def loadTheta():
    matname = u'THETA.mat'
    data = sio.loadmat(matname)
    Theta1 = data['Theta1']
    Theta2 = data['Theta2']
    Theta3 = data['Theta3']
    return Theta1, Theta2, Theta3


def verfication(fullpath):
    word = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
            'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    Theta1, Theta2, Theta3 = loadTheta()

    im = openimage(fullpath)
    X = photo_split(im)
    p1, p2, p3, p4 = predict(Theta1, Theta2, Theta3, X)
    verification = (word[p1[0, 0]]) + (word[p2[0, 0]]) + (word[p3[0, 0]]) + (word[p4[0, 0]])
    return verification


def getStuNam(page):
    return re.findall(r'<span id="xhxm">(.*?)同学</span></em>', page, re.I | re.M)[0]


def StuNamEncode(StuNam):
    codelist = re.findall(r'x(.*?)\\', str(StuNam.encode('GBK')), re.I | re.M)
    namecode = ''
    for i in codelist:
        namecode = namecode + '%' + i.upper()

    return namecode


def UrlToMes(ScoPage):
    index = re.search(r'课程代码(.*?)</table>', ScoPage, re.I | re.M | re.S).span()
    ScoPage = ScoPage[index[0]:index[1]]
    r = re.findall(r'<tr(.*?)</tr>', ScoPage, re.I | re.M | re.S)
    messageStr = ''
    for x in r:
        result = re.findall(r'<td>(.*?)</td>', x, re.I | re.M)
        messageStr = messageStr + result[1] + '的分数为' + result[3] + '\n'

    return messageStr


update_info = '本次升级内容：\n1、增加学分\n2、当有新成绩时，新出的科目成绩会放在邮件标题\n3、缩短查询间隔\n4、感谢你的支持!\n'

info = [
    {
        'account': '1111',
        'password': '1111',
        'email': '1111@qq.com',
        'from_email': '1111@163.com',
        'smtp_password': '11111',
        'old_score': None
    },
    {
        'account': 'id',
        'password': '1111',
        'email': '1111@qq.com',
        'from_email': '111@163.com',
        'smtp_password': '1111',
        'old_score': None
    }
]

error_time = 0
all_times = 0
os.chdir("source_new")
while True:
    try:
        for x in info:
            studentID = x['account']
            password = x['password']
            cookie = http.cookiejar.CookieJar()
            handler = urllib.request.HTTPCookieProcessor(cookie)
            opener = urllib.request.build_opener(handler)

            loginURL = 'http://jwgldx.gdut.edu.cn/default2.aspx'
            page = opener.open(loginURL).read()
            page = (page.decode("gb2312"))

            picurl = 'http://jwgldx.gdut.edu.cn/CheckCode.aspx'
            while True:
                picture = opener.open(picurl).read()
                with open('checkcode.jpg', 'wb') as f:
                    f.write(picture)

                SecretCode = verfication('checkcode.jpg')
                postdata = {
                    '__VIEWSTATE': getVIEW(page),
                    'txtUserName': studentID,
                    'TextBox2': password,
                    'RadioButtonList1': '%D1%A7%C9%FA',
                    'txtSecretCode': SecretCode,
                    'Button1': '',
                    'lbLanguage': '',
                    'hidPdrs': '',
                    'hidsc': ''
                }

                headers = {
                    'Connection': 'keep-alive',
                    'Referer': 'http://jwgldx.gdut.edu.cn/default2.aspx',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                }

                data = urllib.parse.urlencode(postdata).encode(encoding='utf-8')
                request = urllib.request.Request(url=loginURL, data=data, headers=headers)  # (loginURL, data, headers)

                respond = opener.open(request)
                result = respond.read().decode('gb2312')
                if iserror(result):
                    error_time += 1
                else:
                    break

            student_name = getStuNam(result)
            studentNameCode = StuNamEncode(student_name)
            headers = {
                'Connection': 'keep-alive',
                'Referer': 'http://jwgldx.gdut.edu.cn/xs_main.aspx?xh=' + studentID,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
            }
            ScorceUrl = 'http://jwgldx.gdut.edu.cn/xscj.aspx?xh=' + studentID + '&xm=' + studentNameCode + '&gnmkdm=N121605'
            request = urllib.request.Request(url=ScorceUrl, data=None, headers=headers)
            ScorcePage = opener.open(request).read()
            ScorcePage = (ScorcePage.decode("gb2312"))
            postdata = {
                '__VIEWSTATE': getVIEW(ScorcePage),
                'ddlXN': '2016-2017',
                'ddlXQ': '1',
                'txtQSCJ': '0',
                'txtZZCJ': '100',
                'Button5': '%B0%B4%D1%A7%C4%EA%B2%E9%D1%AF'
            }
            headers = {
                'Connection': 'keep-alive',
                'Referer': ScorceUrl,
                'Origin': 'http://jwgldx.gdut.edu.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
            }

            data = urllib.parse.urlencode(postdata).encode(encoding='utf-8')
            request = urllib.request.Request(url=ScorceUrl, data=data, headers=headers)

            respond = opener.open(request)
            result = respond.read().decode('gb2312')
            new_score = page_to_list(result)
            if new_score != x['old_score']:
                if x['old_score'] is None:
                    x['old_score'] = new_score
                else:
                    the_title, the_message = get_title_message(x['old_score'], new_score)
                    send_message(the_message, x['from_email'], x['smtp_password'], x['email'], student_name, the_title)
                    x['old_score'] = new_score

        time.sleep(300)
        all_times += 1
        print(all_times)

    except:
        time.sleep(30)
        continue

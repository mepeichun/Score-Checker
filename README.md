# check_score_system
期末成绩自动查询

仅实用于广东工业大学教务系统

注意：禁止用于商业用途，欢迎个人学习交流。禁止攻击教务系统，做有损天良之事。未经同意，禁止转载。

本代码作为大学生创新项目的一小部分，请别人的尊重劳动成果

## 使用方法
```python
info = [
    {
        'account': '11',
        'password': '11',
        'email': '11@qq.com',
        'from_email': '11@163.com',
        'smtp_password': '111',
        'old_score': None
    },
    {
        'account': '22',
        'password': '22',
        'email': '22@qq.com',
        'from_email': '22@163.com',
        'smtp_password': '22',
        'old_score': None
    }
]
```
修改`account`,`password`,`email`,`from_email`,`smtp_password`为：`学号`,`教务管理系统密码`,`接收邮箱`,`发送邮箱`,`发送邮箱smtp密码`
注意，推荐发送邮箱为@163.com网易邮箱，便于开启stmp功能(请自行搜索)
该代码效率不高，请勿疯狂使用，以免占用学校服务器资源
相信在不久的将来，这个系统就会出现在你们面前，供全校学生使用

## 使用效果

每次新出成绩，会在成绩出来5分钟内收到邮件，并将新出的科目及成绩放到标题

![截图1](https://github.com/mepeichun/check_score_system/raw/master/screenshot1.PNG)

邮件内部有详细的学科成绩，学期绩点

![截图2](https://github.com/mepeichun/check_score_system/raw/master/screenshot2.PNG)

## 原理
深度神经网络加爬虫

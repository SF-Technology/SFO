# SFO #

SFO 是为对象存储Swift开发的可视化监控管理工具。主要由对象存储Swift集群个节点代理服务SfoAgents、集中管理服务SfoServer和WEB可视化应用SfoBrowser组成

>**提示**：</br>
>如果对构建不清楚如何使用Flask构建Restful请参考如下文档：</br>
>1）http://www.pythondoc.com/Flask-RESTful/intermediate-usage.html#id2</br>
>2）http://flask.pocoo.org/docs/0.12/</br>


 Linux主机需要安装 lshw 模块
 操作kafka需要安装kafka-python模块和six库
 keystone需要安装python-keystoneclient
 操作mysql需要安装mysql-python包 yum install mysql-python
 还需要安装flask的数据库操作模块 pip install flask-sqlalchemy
 安装pymysql包 pip install pymysql

 报错解决：
 ImportError: cannot import name _rd_kafka
 需要安装kafka依赖库：yum install librdkafka-devel
 安装完成后重装pykafka包
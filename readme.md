#### 使用

将setting的DATEBASES的HOST改成cvat数据库的IP

#### 定时任务**

运行 python manage.py migrate 后

再将 workload/views.py 的 # from apscheduler.schedulers.background import BackgroundScheduler

至 # my_job()处的注释解除



 

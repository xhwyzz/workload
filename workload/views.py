from django.shortcuts import render
from workload.models import Workload
from django.db.models import Count


# from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# import psycopg2
# import datetime
# from django.conf import settings
#
# #开启定时工作
# try:
#     # 实例化调度器
#     scheduler = BackgroundScheduler()
#     # 调度器使用DjangoJobStore()
#     scheduler.add_jobstore(DjangoJobStore(), "default")
#     # 设置定时任务，选择方式为interval，时间间隔为1小时
#     @register_job(scheduler,"interval", hours=1)
#     def my_job():
#         # 这里写你要执行的任务
#         conn = psycopg2.connect(database=settings.DATABASES['default']['NAME'], user=settings.DATABASES['default']['USER'],
#                                 password=settings.DATABASES['default']['PASSWORD'], host=settings.DATABASES['default']['HOST'],
#                                 port=settings.DATABASES['default']['PORT'])
#         cursor = conn.cursor()
#         # 查询新增标签数量
#         job_id = {}
#         cursor.execute('select MAX(lastid) from workload')
#         row = cursor.fetchone()
#         if row[0]:
#             lastid = row[0]
#         else:
#             lastid = 0
#         cursor.execute("select job_id, count(job_id) from engine_labeledshape where id > %d group by job_id" % lastid)
#         rows = cursor.fetchall()
#         for row in rows:
#             job_id[row[0]] = row[1]
#         cursor.execute('select MAX(id) from engine_labeledshape')
#         row = cursor.fetchone()
#         lastid = row[0]
#         # 查询任务id的负责人
#         as_id = {}
#         for j_id in job_id:
#             cursor.execute("select task_id from engine_segment where id = %s" % j_id)
#             row = cursor.fetchone()
#             cursor.execute("select assignee_id from engine_task where id = %s" % row[0])
#             row = cursor.fetchone()
#             a_id = row[0]
#             if a_id not in as_id:
#                 as_id[a_id] = job_id[j_id]
#             else:
#                 as_id[a_id] = as_id[a_id] + job_id[j_id]
#
#         # 查询负责人id对应的用户名
#         cursor.execute("select id,username from auth_user")
#         rows = cursor.fetchall()
#         user_id = {}
#         for row in rows:
#             user_id[row[0]] = row[1]
#         for ele in as_id:
#             dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             if ele is not None:
#                 cursor.execute(
#                     "INSERT INTO workload (assignee, updated_date, workcount, lastid) VALUES ('%s', '%s', %d, %d)" % (
#                     user_id[ele], dt, as_id[ele], lastid))
#                 print('添加成功')
#             else:
#                 cursor.execute(
#                     "INSERT INTO workload (assignee, updated_date, workcount, lastid) VALUES ('%s', '%s', %d, %d)" % (
#                     'None', dt, as_id[ele], lastid))
#                 print('添加成功')
#             conn.commit()
#
#         cursor.close()
#         conn.close()
#     register_events(scheduler)
#     scheduler.start()
# except Exception as e:
#     print(e)
#     # 有错误就停止定时器
#     scheduler.shutdown()
# my_job()

def workload_list(request):
    workloads = Workload.objects.filter().annotate(dcount=Count('updated_date'))
    pdict = {}
    wdict = {}
    for ele in workloads:
        if str(ele.updated_date)[:10] not in wdict:
            wdict[str(ele.updated_date)[:10]] = {
                'hours': {str(ele.updated_date)[10:]: [{'type': ele.assignee, 'value': ele.workcount}]},
                'days': [{'type': ele.assignee, 'value': ele.workcount}],
            }
        else:
            # 天总工作量
            flag = True
            for i in wdict[str(ele.updated_date)[:10]]['days']:
                if ele.assignee in i.values():
                    i['value'] = i['value'] + ele.workcount
                    flag = False
            if flag:
                wdict[str(ele.updated_date)[:10]]['days'].append({'type': ele.assignee, 'value': ele.workcount})
            # 小时总工作量
            if str(ele.updated_date)[10:] not in wdict[str(ele.updated_date)[:10]]['hours']:
                wdict[str(ele.updated_date)[:10]]['hours'][str(ele.updated_date)[10:]] = [{'type': ele.assignee, 'value': ele.workcount}]
            else:
                wdict[str(ele.updated_date)[:10]]['hours'][str(ele.updated_date)[10:]].append({'type': ele.assignee, 'value': ele.workcount})

    for eledate in wdict:
        pdict[eledate] = {}
        for elehours in wdict[eledate]['hours']:
            for eleperson in wdict[eledate]['hours'][elehours]:
                if eleperson['type'] not in  pdict[eledate]:
                    pdict[eledate][eleperson['type']] = [{'type': elehours, 'value': eleperson['value']}]
                else:
                    flag = True
                    for i in   pdict[eledate][eleperson['type']]:
                        if elehours in i.values():
                            i['value'] =  i['value'] + eleperson['value']
                            flag = False
                    if flag:
                        pdict[eledate][eleperson['type']].append({'type': elehours, 'value': eleperson['value']})

    context = {
        'wdict': wdict,
        'pdict': pdict,
    }

    return render(request, 'index.html', context=context)
from django.http import JsonResponse
from django.core.exceptions import ValidationError,ObjectDoesNotExist
import time

from sign.models import Event, Guest
# 添加发布会接口
def add_event(request):
    #通过POST请求接收发布会参数
    #发布会id
    eid = request.POST.get('eid', '')
    #发布会标题
    name = request.POST.get('name', '')
    #限制人数
    limit = request.POST.get('limit', '')
    #状态
    status = request.POST.get('status', '')
    #地址
    address = request.POST.get('address', '')
    #发布会时间
    start_time = request.POST.get('start_time', '')

    #判断字段为空，则JsonResponse（）返回相应的状态码和提示
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        #JsonResponse()是一个非常有用的类，它可以将字典转化成JSON格式返回给客户端
        return JsonResponse({'status':10021, 'message':'parameter error'})

    #分别判断发布会id和名称是否存在，如果存在则返回相应的状态码和提示
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status':10022, 'message':'event id already exists'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status':10023, 'message':'event name already exists'})

    #因为发布会状态不是必传字段，所以判断如果为空，则将状态设为1,即True
    if status == '':
        status = 1

    #将数据插入Event表
    try:
        Event.objects.create(id=eid, name=name, limit=limit, address=address, status=int(status), start_time=start_time)
    #如果插入过程中日期格式错误，则抛出ValidationError异常
    except ValidationError as e:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        #异常处理接收该异常并返回相应的状态码和提示
        return JsonResponse({'status':10024, 'message':error})
    #插入成功，则返回状态码200和提示
    return JsonResponse({'status':200, 'message':'add event success'})

# 查询发布会接口
def get_event_list(request):
    #通过GET请求接收发布会id（eid）和发布会名称(name)。两个参数都为可选项，但不能同时为空
    eid = request.GET.get('eid', '')
    name = request.GET.get('name', '')

    #两个参数同时为空，则返回状态码和提示
    if eid == '' and name == '':
        return JsonResponse({'status':10021, 'message':'parameter error'})

    #如果eid不为空，则优先使用发布会id查询。由于id具有唯一性，所以查询结果只会有一条
    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'query result is empty'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            #将查询结果以字典的形式存放在定义的event中，并将event作为接口返回字典中的data对应的值
            return JsonResponse({'status':200, 'message':'success', 'data':event})

    #如果name不为空，则使用发布会标题查询。由于name为模糊查询，查询数据可能会有多条
    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            #首先将查询结果的每一条数据放到一个event字典中
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                #再把每个event字典放到datas数组中
                datas.append(event)
            #最后将整个datas数组作为接口返回字典中data对应的值
            return JsonResponse({'status':200, 'message':'success', 'data':datas})
        else:
            return JsonResponse({'status':10022, 'message':'query result is empty'})




# 添加嘉宾接口
def add_guest(request):
    #通过POST请求接收嘉宾参数
    #关联发布会id
    eid = request.POST.get('eid', '')
    #姓名
    realname = request.POST.get('realname', '')
    #手机
    phone = request.POST.get('phone', '')
    #邮箱
    email = request.POST.get('email', '')

    #判断eid，realname,phone不为空，否则返回状态码和提示
    if eid == '' or realname == '' or phone == '':
        return JsonResponse({'status':10021, 'message':'parameter error'})

    #判断关联的发布会eid是否存在，以及发布会状态是否为True
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022, 'message':'event id null'})

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023, 'message':'event status is not available'})

    #判断嘉宾人数不应该大于发布会人数限制,否则返回状态码和提示
    event_limit = Event.objects.get(id=eid).limit
    guest_limit = Guest.objects.filter(event_id=eid)

    if len(guest_limit) >= event_limit:
        return JsonResponse({'status':10024, 'message':'event number is full'})

    #判断当前时间是否大于发布会时间
    event_time = Event.objects.get(id=eid).start_time
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime, "%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))
    now_time = str(time.time())
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    #如果大于，则说明发布会已开始，或已结束。就不能添加嘉宾了
    if n_time >= e_time:
        return JsonResponse({'status':10025, 'message':'event has started'})

    #插入嘉宾数据
    try:
        Guest.objects.create(realname=realname, phone=phone, email=email, sign=0, event_id=int(eid))
    except ValidationError as e:
        return JsonResponse({'status':10026, 'message':'the event guest phone number repeat'})
    #插入成功，则返回状态码200和提示
    return JsonResponse({'stauts':200, 'message':'add guest success'})



# 查询嘉宾接口
def get_guest_list(request):
    #通过GET请求接收嘉宾参数
    #关联发布会id
    eid = request.GET.get('eid', '')
    #手机
    phone = request.GET.get('phone', '')

    #如果发布会id为空，返回状态码和提示
    if eid == '':
        return JsonResponse({'status':10021, 'message':'eid cannot be empty'})

    #如果发布会id不为空，但手机号为空，则优先使用发布会id查询。由于id具有唯一性，所以查询结果只会有一条
    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            #首先将查询结果的每一条数据放到一个guest字典中
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                #再把每个guest字典放到datas数组中
                datas.append(guest)
            #最后将整个datas数组作为接口返回字典中data对应的值
            return JsonResponse({'status':200, 'message':'success', 'data':datas})
        else:
            return JsonResponse({'status':10022, 'message':'query  result is empty'})

    #如果发布会id不为空，手机号也不为空，通过手机号和发布会id查询。
    if eid != '' and phone != '':
            guest = {}
            try:
                result = Guest.objects.get(phone=phone, event_id=eid)
            #如果有异常，则抛出ObjectDoesNotExist
            except ObjectDoesNotExist:
                return JsonResponse({'status':10022, 'message':'query result is empty'})
            #没有异常，则执行else语句，返回接口字典
            else:
                guest['realname'] = result.realname
                guest['phone'] = result.phone
                guest['email'] = result.email
                guest['sign'] = result.sign
                #将查询结果以字典的形式存放在定义的guest中，并将event作为接口返回字典中的data对应的值
                return JsonResponse({'status':200, 'message':'success', 'data':guest})


# 嘉宾签到接口
def user_sign(request):
    #通过POST请求接收嘉宾参数
    #关联发布会id
    eid = request.POST.get('eid', '')
    #手机
    phone = request.POST.get('phone', '')

    #判断eid,phone均不能为空，否则返回状态码和提示
    if eid == '' or phone == '':
        return JsonResponse({'stauts':10021, 'message':'parameter error'})

    #查询发布会id是否存在，不存在返回状态码和提示
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'stauts':10022, 'message':'event id null'})

    #查询发布会的状态，状态不为True，即当前未开启发布会，返回状态码和提示
    result = Event.objects.get(id=eid).stauts
    if not result:
        return JsonResponse({'stauts':10023, 'message':'event status is not available'})

    #判断当前时间是否大于发布会时间
    #发布会时间
    event_time = Event.objects.get(id=eid).start_time
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime, "%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))
    #当前时间
    now_time = str(time.time())
    ntime = now_time.split(".")[0]
    n_time = int(ntime)
    #如果大于，则说明发布会已开始，或已结束。就不能添加嘉宾了
    if n_time >= e_time:
        return JsonResponse({'status':10024, 'message':'event has started'})

    #再判断嘉宾手机号是否存在，不存在返回状态码和提示
    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status':10025, 'message':'user phone null'})

    #判断手机号和发布会id是否为对应关系。不是对应关系，则返回状态码和提示
    result = Guest.objects.filter(event_id=eid, phone=phone)
    if not result:
        return JsonResponse({'status':10026, 'message':'user did not participate in the conference'})

    #判断结果的状态是否为签到，
    result = Guest.objects.get(event_id=eid, phone=phone).sign
    #如果已签到，则返回状态码和提示
    if result:
        return JsonResponse({'status':10027, 'message':'user has sign in'})
    #如果未签到，则修改状态为已签到，并返回状态码200和提示
    else:
        Guest.objects.filter(event_id=eid, phone=phone).update(sign='1')
        return JsonResponse({'status':200, 'message':'sign success'})
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.core.mail import send_mass_mail
import datetime


@csrf_exempt
def drafting_contract(request):
    if request.method == "GET":
        return render(request, 'DraftingContract.html')
    if request.method == "POST":
        name = request.POST.get('name')
        customer = request.POST.get('customer')
        beginTime = request.POST.get('beginTime')
        endTime = request.POST.get('endTime')
        content = request.POST.get('content')
        userName = request.user.username
        nowTime = datetime.datetime.now()

        file = request.FILES.get('files')
        print(file)
        # print(file.name)

        my_contract = Contract.objects.create(name=name,
                                              customer=customer,
                                              beginTime=beginTime,
                                              endTime=endTime,
                                              content=content,
                                              userName=userName)
        my_state = State.objects.create(conNum=my_contract.num, type=1, time=nowTime)

        if file is not None:
            my_attachment = Attachment.objects.create(conNum=my_contract.num,
                                                      fileName=file.name,
                                                      uploadTime=nowTime,
                                                      file=file)
        print(my_contract)
        print(my_state)
        print(my_contract.beginTime)

        # message1 = ('Subject here', 'Here is the message', '948525147@qq.com', ['719475327@qq.com'])
        # message2 = ('Another Subject', 'Here is another message', '948525147@qq.com', ['719475327@qq.com'])
        #
        # send_mass_mail((message1, message2), fail_silently=False)

        return render(request, 'draftingContract.html')


def list_draft(request):
    contract_list = []
    data_list = Contract.objects.filter(userName=request.user.username)
    for contract in data_list:
        state = State.objects.filter(conNum=contract.num).last()
        if state.type == 1:
            state = '待会签'
        elif state.type == 2:
            state = '待定稿'
        elif state.type == 3:
            state = '待审批'
        elif state.type == 4:
            state = '待签订'
        else:
            state = '已签订'
        temp = State.objects.filter(conNum=contract.num).first()
        contract_list.append({'num': contract.num, 'name': contract.name, 'time': temp.time, 'state': state})
    return render(request, 'listDraft.html', {'contract_list': contract_list})


def list_contract(request):
    # right = Right.objects.filter(userName=request.user.username).first()
    # role = Role.objects.filter(name=right.userName).first()
    # flag = [False, False, False]
    # if '会签合同' in role.functions:
    #     flag[0] = True

    contract_list = []
    process_list = Process.objects.filter(state=0, userName=request.user.username)
    for process in process_list:
        if process.type == 1:
            p_type = '会签'
        elif process.type == 2:
            p_type = '审批'
        else:
            p_type = '签订'
        contract = Contract.objects.filter(num=process.conNum).first()
        temp = State.objects.filter(conNum=contract.num).first()
        contract_list.append({'conNum': process.conNum, 'name': contract.name, 'time': temp.time, 'p_type': p_type})
    return render(request, 'listContract.html', {'contract_list': contract_list})


def contract_info(request):
    if request.method == "POST":
        num = request.POST.get('num')
        p_type = request.POST.get('type')
        contract = Contract.objects.filter(num=num).first()
        if p_type == '会签':
            return render(request, 'signingContract.html', {'contract': contract})
        elif p_type == '定稿':
            return render(request, 'finalContract.html', {'contract': contract})
        elif p_type == '审批':
            return render(request, 'approvalContract.html', {'contract': contract})
        else:
            return render(request, 'signContract.html', {'contract': contract})


def signing_contract(request):
    if request.method == "POST":
        if 'table' in request.POST:
            num = request.POST.get('num')
            contract = Contract.objects.filter(num=num).first()
            return render(request, 'signingContract.html', {'contract': contract})
        else:
            num = request.POST.get('num')
            content = request.POST.get('content')
            Process.objects.filter(conNum=num, type=1, userName=request.user.username).update(state=1,
                                                                                              content=content,
                                                                                              time=datetime.datetime.now())
            filter_result = Process.objects.filter(conNum=num, type=1, state=0)
            if not filter_result:
                State.objects.create(conNum=num, type=2, time=datetime.datetime.now())
            return redirect('/listContract')
    return render(request, 'signingContract.html')


def final_contract(request):
    if request.method == "POST":
        if 'table' in request.POST:
            num = request.POST.get('num')
            contract = Contract.objects.filter(num=num).first()
            process = Process.objects.filter(conNum=num, type=1).first()
            return render(request, 'signingContract.html', {'contract': contract, 'content': process.content})
        else:
            num = request.POST.get('num')
            content = request.POST.get('content')
            Contract.objects.filter(num=num).update(content=content)
            State.objects.create(conNum=num, type=3, time=datetime.datetime.now())
            return redirect('/listDraft')
    return render(request, 'finalContract.html')


def approval_contract(request):
    if request.method == "POST":
        if 'table' in request.POST:
            num = request.POST.get('num')
            contract = Contract.objects.filter(num=num).first()
            return render(request, 'signingContract.html', {'contract': contract})
        else:
            num = request.POST.get('num')
            state = request.POST.get('state')
            opinion = request.POST.get('opinion')
            Process.objects.filter(conNum=num, type=2, userName=request.user.username).update(state=state,
                                                                                              content=opinion,
                                                                                              time=datetime.datetime.now())
            filter_result = Process.objects.filter(Q(state=0) | Q(state=2), conNum=num, type=2)
            if not filter_result:
                State.objects.create(conNum=num, type=4, time=datetime.datetime.now())
            return redirect('/listContract')
    return render(request, 'approvalContract.html')


def sign_contract(request):
    if request.method == "POST":
        if 'table' in request.POST:
            num = request.POST.get('num')
            contract = Contract.objects.filter(num=num).first()
            return render(request, 'signingContract.html', {'contract': contract})
        else:
            num = request.POST.get('num')
            content = request.POST.get('content')
            Process.objects.filter(conNum=num, type=3, userName=request.user.username).update(state=1,
                                                                                              content=content,
                                                                                              time=datetime.datetime.now())
            filter_result = Process.objects.filter(conNum=num, type=3, state=0)
            if not filter_result:
                State.objects.create(conNum=num, type=5, time=datetime.datetime.now())
            return redirect('/listContract')
    return render(request, 'signContract.html')


def C_Select(request, pagenum='1'):
    print(request.method)
    if request.method == "GET":
        contract_list = Contract.objects.all()

        # 分页构建
        paginator = Paginator(contract_list, 2)
        # 获取某页对象
        try:
            page = paginator.page(pagenum)
        except PageNotAnInteger:
            page = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        except EmptyPage:
            page = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        print(page.object_list[0].name)
        return render(request, 'Contract_select.html',
                      {'page': page, "paginator": paginator, 'pagerange': paginator.page_range,
                       'currentpage': page.number})
    if request.method == "POST":
        s_name = request.POST['name']
        contract_list = Contract.objects.filter(Q(name__icontains=s_name)).order_by('num')
        paginator = Paginator(contract_list, 2)

        try:
            page = paginator.page(pagenum)
        except PageNotAnInteger:
            page = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        except EmptyPage:
            page = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容

        return render(request, 'Contract_select.html',
                      {'page': page, "paginator": paginator, 'pagerange': paginator.page_range,
                       'currentpage': page.number})


def C_Process(request, type=0, pagenum='1'):
    print(request.method)
    if request.method == "GET":
        process_list = Process.objects.all()
        # 分页构建
        paginator = Paginator(process_list, 2)
        # 获取某页对象
        try:
            page = paginator.page(pagenum)
        except PageNotAnInteger:
            page = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        except EmptyPage:
            page = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        # print(page.object_list[0].name)
        return render(request, 'Contract_process.html',
                      {'page': page, "paginator": paginator, 'pagerange': paginator.page_range,
                       'currentpage': page.number})
    if request.method == "POST":
        s_name = request.POST['name']
        contract_list = Process.objects.filter(Q(name__icontains=s_name)).order_by('num')
        paginator = Paginator(contract_list, 2)

        try:
            page = paginator.page(pagenum)
        except PageNotAnInteger:
            page = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        except EmptyPage:
            page = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容

        return render(request, 'Contract_select.html',
                      {'page': page, "paginator": paginator, 'pagerange': paginator.page_range,
                       'currentpage': page.number})

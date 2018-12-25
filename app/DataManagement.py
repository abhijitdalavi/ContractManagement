import os

from django.http import HttpResponseRedirect,StreamingHttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *


class customer_add(TemplateView):
    template_name = "customer_add.html"

    def get(self, request, *args, **kwargs):
        return render(request, 'customer_add.html')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        address = request.POST.get('address')
        fax = request.POST.get('fax')
        tel = request.POST.get('tel')
        email = request.POST.get('email')
        bank = request.POST.get('bank')
        account = request.POST.get('account')
        remark = request.POST.get('remark')

        customer_list = Customer.objects.all()
        for user in customer_list:
            if user.name == name:
                return render(request, 'customer_add.html', {'is_exist': '该客户已存在，请重新输入'})

        Customer.objects.create(name=name, address=address, fax=fax, tel=tel, email=email, bank=bank,
                                account=account, remark=remark)

        return HttpResponseRedirect('/customer_select')


class customer_modify(TemplateView):
    template_name = "customer_modify.html"

    def get(self, request, *args, **kwargs):
        return render(request, 'customer_modify.html')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        tel = request.POST.get('tel')
        if tel is None:
            customer_list = Customer.objects.all()
            user_exist = False
            for user in customer_list:
                if user.name == name:
                    user_exist = True
                    return render(request, 'customer_modify.html', {'user': user})
                else:
                    continue

            return render(request, 'customer_modify.html', {'not_found': "User not found"})
        else:
            address = request.POST.get('address')
            fax = request.POST.get('fax')
            tel = request.POST.get('tel')
            email = request.POST.get('email')
            bank = request.POST.get('bank')
            account = request.POST.get('account')
            remark = request.POST.get('remark')
            Customer.objects.filter(name=name).update(tel=tel, fax=fax, email=email, address=address, bank=bank,
                                                      account=account, remark=remark)

            return render(request, 'customer_modify.html', {'complish': "User modify complish"})


class customer_select(TemplateView):
    template_name = "customer_select.html"

    def get(self, request, *args, **kwargs):
        customer_list = Customer.objects.all()

        file = open('media/新建文本文档.txt', 'rb')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="models.txt"'
        # return response
        return render(request, 'customer_select.html',{'customer_list': customer_list})

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        download =request.POST.get('download')
        if download is None:
            customer_list = Customer.objects.all()
            attach_list = Attachment.objects.all()
            user_exist = False
            for user in customer_list:
                if user.name == name:
                    user_exist = True
                    for attach in attach_list:
                        if attach.cusName == user.name:
                            return render(request, 'customer_select.html', {'user': user, 'query': "query"})
                    return render(request, 'customer_select.html', {'user': user})
                else:
                    continue

            return render(request, 'customer_select.html', {'not_found': "User not found"})
        else:
            attach_list = Attachment.objects.all()
            file = ''
            path = ''
            for attach in attach_list:
                print(attach.cusName)
                print(attach.path)
                if attach.cusName == download:
                    path = attach.path
                    file = open(attach.path, 'rb')
            response = StreamingHttpResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=' + os.path.basename(path)
            return response
            # return render(request, 'customer_select.html', {'not_found': "User not found"})


class customer_delete(TemplateView):
    template_name = "customer_delete.html"

    def get(self, request, *args, **kwargs):
        return render(request, 'customer_delete.html')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        tel = request.POST.get('tel')
        address = request.POST.get('address')
        print(name, tel, address)
        if tel is None:
            customer_list = Customer.objects.all()
            user_exist = False
            for user in customer_list:
                if user.name == name:
                    user_exist = True
                    return render(request, 'customer_delete.html', {'user': user})
                else:
                    continue

            return render(request, 'customer_delete.html', {'not_found': "User not found"})
        else:

            Customer.objects.filter(name=name).delete()

            return render(request, 'customer_delete.html', {'complish': "User delete complish"})

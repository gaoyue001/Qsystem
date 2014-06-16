# coding=utf-8
from django.shortcuts import render_to_response, redirect, render,get_object_or_404,RequestContext
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import RequestContext
import json
from django.db import connection
import MySQLdb
from django.contrib.sessions.models import Session
import datetime
from django.core.urlresolvers import reverse
from django.db.models import Q
from forms import changedesignForm, delayprojectForm, ProjectForm, ProjectSearchForm
from project.models import *
import math
import forms
import models

from django.views.decorators.csrf import csrf_exempt

from models import project,user,project_user,project_delay,public_message,project_user_message
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

#login
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from forms import RegisterForm,LoginForm

def register(request):
    template_var={}
    form = RegisterForm()    
    if request.method=="POST":
        form=RegisterForm(request.POST.copy())
        if form.is_valid():
            new_user = form.save()
            template_var["error"] = _(u"注册成功！")
    template_var["form"]=form
    return render_to_response("register.html",template_var,context_instance=RequestContext(request))
    
def login(request):
    template_var={}
    
    if "username" in request.COOKIES and "password" in request.COOKIES:
        username = request.COOKIES["username"]
        password = request.COOKIES["password"]
        _userset=user.objects.filter(username__exact = username,password__exact = password)
        if _userset.count() >= 1:
            _user = _userset[0]
            request.session['username'] = _user.username
            request.session['realname'] = _user.realname
            return HttpResponseRedirect("/personal_homepage")
    
    form = LoginForm()
    if request.method == 'POST':
        form=LoginForm(request.POST.copy())
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            isautologin = form.cleaned_data["isautologin"]
            _userset=user.objects.filter(username__exact = username,password__exact = password)
            if _userset.count() >= 1:
                _user = _userset[0]
                if _user.isactived:
                    request.session['username'] = _user.username
                    request.session['realname'] = _user.realname
                    request.session['id'] = _user.id
                    
                    response = HttpResponseRedirect("/personal_homepage")
                    if isautologin:
                        response.set_cookie("username", username, 3600)
                        response.set_cookie("password", password, 3600)
                    return response
                else:
                    template_var["error"] = _(u'用户未激活，请联系管理员')
            else:
                template_var["error"] = _(u'用户不存在，请先注册')
    template_var["form"]=form
    return render_to_response("login.html",template_var,context_instance=RequestContext(request))
#login


# Create your views here.
def new_project(request,pid = ''):
    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            priority = form.cleaned_data['priority']
            pname = form.cleaned_data['pname']
            status = form.cleaned_data['status']
            leader = form.cleaned_data['leader']
            leader = models.user.objects.get(id=leader)
            designer = form.cleaned_data['designer']
            if designer:
                designer  = models.user.objects.get(id=designer )
            tester = form.cleaned_data['tester']
            if tester:
                tester  = models.user.objects.get(id=tester )
            sdate = form.cleaned_data['startdate']
            pdate = form.cleaned_data['plandate']
            psdate = form.cleaned_data['psdate']
            pedate = form.cleaned_data['pedate']
            dsdate = form.cleaned_data['dsdate']
            dedate = form.cleaned_data['dedate']
            tsdate = form.cleaned_data['tsdate']
            tedate = form.cleaned_data['tedate']
            ppath = form.cleaned_data['ppath']
            dppath = form.cleaned_data['dppath']
            tppath = form.cleaned_data['tppath']
            tcpath = form.cleaned_data['tcpath']
            trpath = form.cleaned_data['trpath']
            relateduser = form.cleaned_data['relateduser']
            if (pid==''):
                pro = models.project(priority=priority, project=pname, status_p=status, leader_p =leader, designer_p=designer,tester_p=tester, start_date=sdate, expect_launch_date=pdate, real_launch_date=tsdate, estimated_product_start_date=psdate, estimated_product_end_date=pedate, estimated_develop_start_date=dsdate, estimated_develop_end_date=dedate, estimated_test_start_date=tsdate, estimated_test_end_date=tedate, blueprint_p=ppath, develop_plan_p=dppath, test_plan_p=tppath, test_case_p=tcpath, test_report_p=trpath, isactived=1)
            else:
                pro = models.project(id=pid,priority=priority, project=pname, status_p=status, leader_p =leader, designer_p=designer,tester_p=tester, start_date=sdate, expect_launch_date=pdate, real_launch_date=tsdate, estimated_product_start_date=psdate, estimated_product_end_date=pedate, estimated_develop_start_date=dsdate, estimated_develop_end_date=dedate, estimated_test_start_date=tsdate, estimated_test_end_date=tedate, blueprint_p=ppath, develop_plan_p=dppath, test_plan_p=tppath, test_case_p=tcpath, test_report_p=trpath, isactived=1)
            pro.save()
            
            #存完项目，存相关产品测试开发人员信息
            relateduser = relateduser.replace(" ","").split(",")
            print relateduser
            if len(relateduser):
                if (pid==''):
                    pid = models.project.objects.filter(project=pname).order_by("-id")[0].id
                print pid
                for uid in relateduser:
                    if uid:
                        project_user = models.project_user(username_id=uid, project_id=pid,isactived=1)
                        project_user.save()
            return redirect('/projectlist/')

    return render(request, 'newproject.html', {'form':form})
    

def project_list(request):
	
    noticess=public_message.objects.filter(isactived='1',type_p='notice').order_by('-id')
    count=len(noticess)
    notices=noticess[:5]
    a = 0
    if count == 0:
        a = 0
    elif count == 1:
        a = 0
    elif count == 2:
        a = 0
    elif count == 3:
        a = 0
    elif count == 4:
        a = 0
    elif count == 5:
        a = 0
    else:
        a = len(noticess)-5    	
	

    projectlist = None
    puser=None
    project_name=""
    start_date_s=""
    end_date_s=""
    status_p=""
    leader_p=""
    project_user_list=None
    print request.method
    puser=project_user.objects.all()
    #projectlist = project.objects.all()
    if request.method == 'POST':
        search_form = ProjectSearchForm(request.POST)
        if search_form.is_valid():
            project_name = search_form.cleaned_data['project']
            start_date_s = search_form.cleaned_data['start_date_s']
            end_date_s = search_form.cleaned_data['end_date_s']
            status_p = search_form.cleaned_data['status_p']
            leader_p = search_form.cleaned_data['leader_p']
           
            print project_name,start_date_s,end_date_s,status_p,leader_p
            projectlist = project.objects.filter()
            
            
            print projectlist
            if not isNone(project_name):
                projectlist = projectlist.filter(project__contains=project_name.strip())
            if not isNone(start_date_s):
                projectlist = projectlist.filter(start_date__gte=start_date_s)
            if not isNone(end_date_s):
                projectlist = projectlist.filter(start_date__lte=end_date_s)
            if not isNone(status_p):
                projectlist = projectlist.filter(status_p=status_p.strip())
            if not isNone(leader_p):
                #projectlist = projectlist.filter(leader_p__username__contains=leader_p.strip())
                project_user_list = project_user.objects.filter(username__realname__contains=leader_p.strip())
                projectids = []
                for p in project_user_list:
                    projectids.append(p.project.id)
                print projectids
                projectlist = projectlist.filter(pk__in=projectids)

    else:
        projectlist = project.objects.all()
        
    paginator = Paginator(projectlist, 25)
    page = request.GET.get('page')
    try:
        projectobj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        projectobj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        projectobj = paginator.page(paginator.num_pages)

    return render_to_response('projectlist.html',RequestContext(request, {'projectobj': projectobj,'puser':puser,'project_name':project_name,'start_date_s':start_date_s,'end_date_s':end_date_s,"status_p":status_p,"leader_p":leader_p,'notices': notices,'count':count,'a':a}))

def isNone(s):
    if s is None or len(s.strip()) == 0:
        return True
    else:
        return False
    
def detail(request, pid):
    pro = models.project.objects.get(id=int(pid))
    user = models.user.objects.get(id = pro.leader_p_id)
    qas = models.user.objects.filter(project_user__project_id=pid, department_id=1)
    qa = {'rel': qas}
    devs = models.user.objects.filter(project_user__project_id=pid, department_id=2)
    dev= {'rel': devs}
    pds = models.user.objects.filter(project_user__project_id=pid, department_id=3)
    pd = {'rel': pds}
    related_user = {'qa':qa, 'dev': dev, 'pd': pd}
    dt_temp ={}
    dt = {}
    #处理时间为空,无法计算时间差   
    if ((pro.estimated_product_end_date!=None) & (pro.estimated_product_start_date!=None)):
        dt_temp['p']= pro.estimated_product_end_date - pro.estimated_product_start_date
        dt['ptime']= int(dt_temp['p'].days+1)
    else:
        dt['ptime']= 0
    if ((pro.estimated_develop_end_date!=None) & (pro.estimated_develop_start_date!=None)):
        dt_temp['d']= pro.estimated_develop_end_date - pro.estimated_develop_start_date
        dt['dtime']= int(dt_temp['d'].days+1)
    else:
        dt['dtime']= 0
    if ((pro.estimated_test_end_date!=None) & (pro.estimated_test_start_date!=None)):
        dt_temp['t']= pro.estimated_test_end_date - pro.estimated_test_start_date
        dt['ttime']= int(dt_temp['t'].days+1)
    else:
        dt['ttime']= 0    
    
    if ('/detail/' in request.path) :
        res = {'pro':pro, 'user':user, 'dt': dt, 'reuser': related_user}
        return render_to_response('detail.html',{'res': res})
    elif ('/editproject' in request.path):
        res = {'pro':pro, 'user':user, 'dt': dt, 'reuser': related_user, 'request': 1}
        return render_to_response('newproject.html',{'res': res})

def show_person(request):
    roles = request.GET['role']
    key = 0
    if roles == "tes":
        key = 1
    elif roles == "dev":
        key = 2
    elif roles == "pro":
        key = 3
    else:
        key = 0
    person = models.user.objects.filter(department_id = key)
    rs=[]
    num = len(person) 
    if num == 0:
        rrs = {"person":rs}
        rs = json.dumps(rrs)
        return HttpResponse(rs)
    for item in person:
        uid = item.id
        realname = item.realname
        dic = {'id':int(uid), 'realname':realname}
        rs.append(dic)
    rrs = {"person":rs}
    rs = json.dumps(rrs)
    return HttpResponse(rs)
    
def psearch(request):
    key = request.GET['key']
    prs = models.user.objects.filter(realname__contains=key)
    rs = []
    if len(prs) > 0:
        for item in prs:
            dic = {'id':item.id, 'realname':item.realname}
            rs.append(dic)
        rrs = {"person":rs}
        rs = json.dumps(rrs)
    return HttpResponse(rs)

#homepage部分views
def personal_homepage(request):
    result=project.objects.exclude(Q(status_p=u'已上线')| Q(status_p=u'暂停'))
    result1=project.objects.exclude(~Q(status_p=u'已上线')& ~Q(status_p=u'暂停'))
    puser=project_user.objects.all()
    
    
    #userid = request.session['id']
    userid='1'
    messagess=public_message.objects.raw('select a.id,a.content,a.isactived,a.project_id,a.publication_date,a.publisher_id,a.type_p from project_public_message as a,project_project_user as  b WHERE  a.project_id=b.project_id and a.isactived=1 and b.username_id=%s ORDER BY a.id desc',[userid])
    i=0
    for item in messagess:
      i=i+1 
    count=i
    messages=messagess[:4]
   
    return render_to_response('personal_homepage.html',
        {'result':result,'result1':result1,'puser':puser,'messages': messages,'count':count})

def deleteproject(request,id):
    delpro=get_object_or_404(project,pk=int(id))    
    delpro.delete()
    return HttpResponseRedirect(reverse("homepage"))


def pauseproject(request,id):
    pausepro=get_object_or_404(project,pk=int(id))
    pausepro.status_p='暂停'
    pausepro.save()
    return HttpResponseRedirect(reverse("homepage"))

def delayproject(request):
    if request.method=='POST':
        form = delayprojectForm(request.POST)
        if form.is_valid():
            delayid=form.cleaned_data['delayid']
            delay_date = form.cleaned_data['delay_date']
            delay_reason = form.cleaned_data['delay_reason']
            delpro=project.objects.get(id=delayid)
            uid=delpro.leader_p
            protitle=delpro.project
            delay_p=project_delay(application=uid,project_id=delayid,delay_to_date=delay_date,apply_date=datetime.datetime.now(),title=protitle,reason=delay_reason,result="jieshou",review_date=datetime.datetime.now(),isactived="1")
            delay_p.save()                   
    return HttpResponseRedirect(reverse("homepage"))


def changedesign(request):    
          
    if request.method=='POST':
        form = changedesignForm(request.POST)
        if form.is_valid():
            changeid=form.cleaned_data['changeid']
            content = form.cleaned_data['content']
            dpath = form.cleaned_data['dpath']
            chd=project.objects.get(id=changeid)
            uid=chd.leader_p
            chd.blueprint_p=dpath
            chd.save()
            pub_message=public_message(project_id=changeid,publisher=uid,content=content,type_p="message",publication_date=datetime.datetime.now(),isactived="1")
            pub_message.save()           
    return HttpResponseRedirect(reverse("homepage"))


def nopermit(request):
    department_list = models.department.objects.all()
    level_1_list=models.user.objects.filter(department_id='1',Position_level="1")
    print level_1_list
    level_2_list=models.user.objects.filter(department_id='1',Position_level="2")
    print level_2_list
    level_3_list=models.user.objects.filter(department_id='1',Position_level="3")
    department=" sfsd"
    return render_to_response('nopermit.html',locals())

@csrf_exempt
def show_user2(request):
    department=request.POST['department']
    department_id=1
    key=0
    if department=='产品设计部':
        department_id=1
    elif department=='测试部':
        department_id=2
    elif department=='客户端开发':
        department_id=3
    elif department=='网站开发':
        department_id=4
    elif department=='客服部':
        department_id=5
    else:
        department_id=1
    level_1_list=models.user.objects.filter(department_id=department_id,Position_level="1")
    level_2_list=models.user.objects.filter(department_id=department_id,Position_level="2")
    level_3_list=models.user.objects.filter(department_id=department_id,Position_level="3")
    department_list = models.department.objects.all()
    return render_to_response('nopermit.html',locals())

@csrf_exempt
def show_user(request):
    if request.method == 'POST':
        department=request.POST['department']
        if department=='产品设计部':
           department_id=1
        elif department=='测试部':
             department_id=2
        elif department=='客户端开发':
             department_id=3
        elif department=='网站开发':
             department_id=4
        elif department=='客服部':
             department_id=5
        else:
             department_id=0
    else:
        department_id=2
    level_list=models.user.objects.filter(department_id=department_id)
    level_1_list=models.user.objects.filter(department_id=department_id,Position_level="1")
    level_2_list=models.user.objects.filter(department_id=department_id,Position_level="2")
    level_3_list=models.user.objects.filter(department_id=department_id,Position_level="3")
    department_list = models.department.objects.all()
    return render_to_response('sourcemanage.html',locals())

@csrf_exempt
def Insert_user1(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_1']
    user=models.user.objects.filter(department_id=department_id,realname=realname).update(Position_level='1')
    return redirect('/show_user/')

@csrf_exempt
def Insert_user2(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_2a']
    user=models.user.objects.filter(department_id=department_id,realname=realname).update(Position_level='2')
    return redirect('/show_user/')

@csrf_exempt
def Insert_user3(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_3a']
    print realname
    user=models.user.objects.filter(department_id=department_id,realname=realname).update(Position_level='3')
    return redirect('/show_user/')

#逻辑删除
@csrf_exempt
def delet_userlogic(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_1']
    user=models.user.objects.filter(department_id=department_id,realname=realname).update(Position_level='0')
    return redirect('/show_user/')

@csrf_exempt
def delet_userlogic2(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_2']
    print realname
    user=models.user.objects.filter(department_id=department_id,realname=realname).update(Position_level='0')
    return redirect('/show_user/')

@csrf_exempt
def delet_userlogic3(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_3']
    user=models.user.objects.filter(department_id=department_id,realname=realname).update(Position_level='0')
    return redirect('/show_user/')

@csrf_exempt
def delete_user1(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_1']
    user=models.user.objects.get(department_id=department_id,realname=realname)
    user.delete()
    return redirect('/show_user/')
@csrf_exempt
def delete_user2(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_2']
    user=models.user.objects.get(department_id=department_id,realname=realname)
    user.delete()
    return redirect('/show_user/')

@csrf_exempt
def delete_user3(request):
    department=request.POST['department']
    if department=='产品设计部':
       department_id=1
    elif department=='测试部':
         department_id=2
    elif department=='客户端开发':
         department_id=3
    elif department=='网站开发':
         department_id=4
    elif department=='客服部':
         department_id=5
    else:
         department_id=0
    realname=request.POST['level_3']
    user=models.user.objects.get(department_id=department_id,realname=realname)
    user.delete()
    return redirect('/show_user/')

def delay(request):
    useid = 1
    #raw_sql = 'select * from project_project_delay where isactived is null and application_id=useid'
    delays = project_delay.objects.filter(application_id=useid).filter(isactived__isnull=True)
    return render_to_response('delay.html',{'delays':delays})

def notice(request):
    if request.method == 'POST':  # 如果是post请求
        wds = request.POST
        try:
            wd = wds['wd']
            notices = public_message.objects.filter(content__icontains=wd).filter(type_p ="notice").order_by('publication_date')
        except Exception as e:
            notices = public_message.objects.filter(type_p ="notice").order_by('publication_date')
    else:  # Get请求
        notices = public_message.objects.filter(type_p ="notice").order_by('publication_date')
    
    return render_to_response('notice.html', locals())

@csrf_exempt

def historymessage(request):
    # 查询与用户相关的消息
    #sessionID = request.session['id']
    #usid = user.objects.get(id=sessionID)
    useid = 1
    #request.session['id']
    tests= project_user_message.objects.filter(userid_id=useid)
    lists=[]
    for test in tests:
        lists.append(test.messageid_id)
    if request.method == 'POST':  # 如果是post请求
        wds = request.POST
        try:
            wd = wds['wd']
            messages = public_message.objects.filter(pk__in=lists).filter(content__icontains=wd).filter(type_p = "message").order_by('publication_date')
        except Exception as e:
            messages = public_message.objects.filter(pk__in=lists).filter(type_p = "message").order_by('publication_date')
    else:  # Get请求
        messages = public_message.objects.filter(pk__in=lists).filter(type_p = "message").order_by('publication_date')
        

    return render_to_response('historymessage.html', locals())


def refuse(request):
    if request.method == 'POST':
        form = forms.TestForm(request.POST)
        if form.is_valid():
            delayid = form.cleaned_data['delayid']
            reason = form.cleaned_data['reason']
            delay = project_delay.objects.get(id=delayid)
            delay.reason = reason
            delay.isactived = False
            delay.save();
    delays = project_delay.objects.filter(isactived=True)
    return render_to_response('delay.html', {'delays':delays})


def approve(request):
    if request.method == 'POST':
        form = forms.Approveform(request.POST)
        if form.is_valid():
            delayid1 = form.cleaned_data['delayid1']
            delay = project_delay.objects.get(id=delayid1)
            delay.isactived = True
            delay.save();
    raw_sql = 'select * from project_project_delay where isactived is null'
    delays = project_delay.objects.raw(raw_sql)
    return render_to_response('delay.html', {'delays':delays})


def deletehistory(request):  
    useid = 1
    if request.method == 'POST':
        form = forms.MessageForm(request.POST)  
        if form.is_valid():
            messageid = form.cleaned_data['messageid'] 
            usermessage= project_user_message.objects.get(userid_id=useid,messageid_id=messageid)
            usermessage.delete();
    tests= project_user_message.objects.filter(userid_id=useid)
    lists=[]
    for test in tests:
        lists.append(test.messageid_id)
    messages  = public_message.objects.filter(pk__in=lists).filter(type_p = "message").order_by('publication_date')
    return render_to_response('historymessage.html', locals())
        
         
  
def deletenotice(request):  
    useid = 1
    if request.method == 'POST':
        form = forms.NoticeForm(request.POST) 
        if form.is_valid():
            noticeid = form.cleaned_data['noticeid'] 
            usernotice= project_user_message.objects.get(userid_id=useid,messageid_id=noticeid)
            print usernotice.messageid_id
            usernotice.delete();
    tests= project_user_message.objects.filter(userid_id=useid)
    lists=[]
    for test in tests:
        lists.append(test.messageid_id)
    notices = public_message.objects.filter(pk__in=lists).filter(type_p = "notice").order_by('publication_date')
    return render_to_response('notice.html', locals())
    
from django.conf.urls import patterns, include, url
from project.views import detail, new_project
from django.contrib import admin
admin.autodiscover()
import project

#login
from django.views.generic import TemplateView
#login


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Qsystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #login
    url('^$', 'project.views.login',name="index"),
    url('^login', 'project.views.login',name="login"),
    url('^register', 'project.views.register',name="register"),
    url('^register/login', 'project.views.login',name="login"),
    url('^register/register', 'project.views.register',name="register"),
    url('^logout','project.views.logout'),
    url('^nologin','project.views.no_login'),
    url('^noperm/', 'project.views.no_perm'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^newproject/$',new_project),
    url(r'^newproject/(\d+)$',new_project),
   # url(r'^create/(\d*)', project.views.create, name='create'),
    url(r'^showperson', project.views.show_person),
    url(r'^projectlist', project.views.project_list),
    url(r'^psearch', project.views.psearch),
    url(r'^detail/(\d+)/$', detail,name="prodetail"),
    url(r'^showuser', project.views.show_headname),
    #homepage
    url(r'^personal_homepage/$', project.views.personal_homepage,name="homepage"),
    url(r'^changedesign/', project.views.changedesign,name="design_change"),
    url(r'^delayproject/$', project.views.delayproject,name="project_delay"),
    url(r'^pauseproject-(?P<id>\d+)/$', project.views.pauseproject,name="project_pause"),
    url(r'^deleteproject-(?P<id>\d+)/$', project.views.deleteproject,name="project_delete"),
    
   #sourcemanage
    url(r'^judge/$',project.views.judge),
    url(r'^sourcemanage/$',project.views.show_user),
    url(r'^show_user/$',project.views.show_user),
    url(r'^nopermit/$',project.views.nopermit),
    url(r'^show_user2/$',project.views.show_user2),
    url(r'^Insert_user1/$',project.views.Insert_user1),
    url(r'^Insert_user2/$',project.views.Insert_user2),
    url(r'^Insert_user3/$',project.views.Insert_user3),
    url(r'^delete_user1/$',project.views.delete_user1),
    url(r'^delete_user2/$',project.views.delete_user2),
    url(r'^delete_user3/$',project.views.delete_user3),
    url(r'^delet_userlogic/$',project.views.delet_userlogic),
    url(r'^delet_userlogic2/$',project.views.delet_userlogic2),
    url(r'^delet_userlogic3/$',project.views.delet_userlogic3),
    ('^detail/(\d+)/$',detail),
    url('^editproject/(\d+)/$', detail,name="editproject"),

    url(r'^delay',project.views.delay),
    url(r'^notice',project.views.notice),
    url(r'^historymessage',project.views.historymessage),
    url(r'^refuse',project.views.refuse),
    url(r'^deletehistory',project.views.deletehistory),
    url(r'^deletenotice',project.views.deletenotice),
    url(r'^approve',project.views.approve),
)

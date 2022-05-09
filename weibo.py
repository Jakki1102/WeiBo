import requests
from lxml import etree
import pymysql
import json
import re
import time
import nlp
from config_spider import *
import datetime

def get_dates(begin_date,end_date):  #获取日期范围列表
    dates = []
    dt = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    date = begin_date[:]
    while date <= end_date:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates


def get_time(date):  #整理时间信息
    localtime = time.localtime(time.time())#获取当前日期
    if '今天' in date:
        date=date.replace('今天',str(localtime[0])+'-'+str(localtime[1])+'-'+str(localtime[2])+'-')
    elif '刚刚' in date:
        date=date.replace('刚刚',str(localtime[0])+'-'+str(localtime[1])+'-'+str(localtime[2])+'-'+str(localtime[3])+':'+str(localtime[4]))
    elif '小时前' in date:
        date=str(localtime[0])+'-'+str(localtime[1])+'-'+str(localtime[2])+'-'+str(localtime[3])+':'+str(localtime[4])
    elif '分钟前' in date:
        date=str(localtime[0])+'-'+str(localtime[1])+'-'+str(localtime[2])+'-'+str(localtime[3])+':'+str(localtime[4])
    elif '秒前' in date:
        date=str(localtime[0])+'-'+str(localtime[1])+'-'+str(localtime[2])+'-'+str(localtime[3])+':'+str(localtime[4])
    elif '年' not in date and '月' in date:
        date=str(localtime[0])+'-'+date
    else:
        return date
    date=date.replace(' ','').replace('年','-').replace('月','-').replace('日','-')
    return date

def get_url(mode,data):
    if mode==1:    #用户主页地址
        url='https://weibo.com/p/'+data
        return url
    if mode==2:    #蓝V用户信息地址
        url='https:'+data
        return url
    if mode==3:    #个人用户信息地址
        url='https://weibo.com'+data
        return url
    if mode==4:     #评论地址
        url='https://weibo.com/aj/v6/comment/big?ajwvr=6&id='+data+'&filter=hot&from=singleWeiBo'
        return url
    if mode==5:    #微博信息页
        url='https:'+data
        return url
    if mode==6:    #微博搜索页地址
        url='https://s.weibo.com'+data
        return url
    
def get_string(mode,string):   #字符串处理
    if mode==1:
        string = re.sub(r'''\\u200d|\\u200b|\\xa0|\\ue627|\\u3000|\\n|[,'" 【】\[\]：]''','',string)    #处理正文及评论等
        return string
    if mode==2:
        string = re.sub(r"\\r|\\n|\\t|<script>|\\",'',string)   #处理网页
        return string        
        
    
def get_html(url,mode):
    headers={'User-Agent': config_user_agent,
             'Cookie':config_cookie}
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False
    if mode==0:  #解析普通网页
        r=requests.get(url,headers=headers)
        html=get_string(2,r.text)
        return html
    elif mode==1:   #解析个人微博json
        r=requests.get(url,headers=headers).json()
        html=get_string(2,r['data'])
        return html
    elif mode==2:   #解析评论json
        r=requests.get(url,headers=headers).json()
        html=get_string(2,r['data']['html'])
        return html
    
#打印信息
def display_user_info(user_info):
    print('用户ID：'+user_info[0])
    print('主页地址：'+user_info[1])
    print('昵称：'+user_info[2])
    print('所在地：'+user_info[3])
    print('性别：'+user_info[4])
    print('生日：'+user_info[5])
    print('简介：'+user_info[6])
    print('注册时间：'+user_info[7])
    print('关注数：'+str(user_info[8]))
    print('粉丝数：'+str(user_info[9]))
    print('微博数：'+str(user_info[10]))
    print('')
def display_weibo_info(weibo_info):
    print('微博ID：'+weibo_info[0])
    print('用户ID：'+weibo_info[1])
    print('微博地址：'+weibo_info[2])
    print('发布时间：'+weibo_info[3])
    print('微博内容：'+weibo_info[4])
    print('情感指数：'+str(weibo_info[5]))
    print('图片地址：'+weibo_info[6])
    print('视频地址：'+weibo_info[7])
    print('转发数：'+str(weibo_info[8]))
    print('评论数：'+str(weibo_info[9]))
    print('点赞数：'+str(weibo_info[10]))
    print('')
def display_comment_info(comment_info):
    print('评论ID：'+comment_info[0])
    print('微博ID：'+comment_info[1])
    print('评论时间：'+comment_info[2])
    print('评论内容：'+comment_info[3])
    print('情感指数：'+str(comment_info[4]))
    print('点赞数：'+str(comment_info[5]))
    print('')
    
def get_user_info(user_home_url):
    try:
        #初始化属性值
        user_info=[]    #将用户的全部信息加入到此列表中
        user_id=nick_name=location=gender=birthday=introduction=register_time='无'
        followers_num=fans_num=weibo_num=0
        html=get_html(user_home_url,0)  
        tree=etree.HTML(html)
        user_id=re.search( r"\['page_id'\]='(.*)'",html).group(1)   #获取用户id
        nick_name=tree.xpath('//h1[@class="username"]/text()')[0]   #获取用户昵称
        followers_num=tree.xpath('//td[1][@class="S_line1"]//strong/text()')[0] #获取用户关注数
        fans_num=tree.xpath('//td[2][@class="S_line1"]//strong/text()')[0]  #获取用户粉丝数
        weibo_num=tree.xpath('//td[3][@class="S_line1"]//strong/text()')[0] #获取用户微博数
        user_info_url=tree.xpath('//div[@class="PCD_person_info"]/a/@href')[0]  #获取用户更多信息链接
        
        #蓝V用户和个人用户的详细信息页地址不同
        if 'about' in user_info_url:
            user_info_url=get_url(2,user_info_url)
        else:
            user_info_url=get_url(3,user_info_url)
            
        html=get_html(user_info_url,0)  
        tree=etree.HTML(html)

        if 'about' in user_info_url:    #蓝V用户只有简介
            introduction=tree.xpath('//div[@class="pf_intro"]/@title')[0]
        else:   #个人用户更多信息
            info_list=tree.xpath('//span[@class="pt_title S_txt2"]/text()')
            if '所在地：'in info_list:
                location_index=info_list.index('所在地：')+1
                location=tree.xpath('//li['+str(location_index)+'][@class="li_1 clearfix"]/span[@class="pt_detail"]/text()')[0]
            if '性别：'in info_list:
                gender_index=info_list.index('性别：')+1
                gender=tree.xpath('//li['+str(gender_index)+'][@class="li_1 clearfix"]/span[@class="pt_detail"]/text()')[0]
            if '生日：'in info_list:
                birthday_index=info_list.index('生日：')+1
                birthday=tree.xpath('//li['+str(birthday_index)+'][@class="li_1 clearfix"]/span[@class="pt_detail"]/text()')[0]
            if '简介：'in info_list:
                introduction_index=info_list.index('简介：')+1
                introduction=get_string(1,tree.xpath('//li['+str(introduction_index)+'][@class="li_1 clearfix"]/span[@class="pt_detail"]/text()')[0])
            if '注册时间：'in info_list:
                register_time_index=info_list.index('注册时间：')+1
                register_time=tree.xpath('//li['+str(register_time_index)+'][@class="li_1 clearfix"]/span[@class="pt_detail"]/text()')[0].replace(' ','')

        user_info.append(user_id)
        user_info.append(user_home_url)
        user_info.append(nick_name)
        user_info.append(location)
        user_info.append(gender)
        user_info.append(birthday)
        user_info.append(introduction)
        user_info.append(register_time)
        user_info.append(followers_num)
        user_info.append(fans_num)
        user_info.append(weibo_num)
        return user_info
    except:
        print('用户信息获取失败\n')
        pass


def get_weibo(weibo_url):
    try:
        html=get_html(weibo_url,0)  
        tree=etree.HTML(html)
        weibo_info=[]
        weibo_id=user_id=time=content=image=video='无'
        sentiment=repost_num=comment_num=like_num=0
        weibo_id=tree.xpath('//div[@node-type="root_child_comment_build"]/@mid')[0]
        user_id=re.search( r"\['page_id'\]='(.*)'",html).group(1)
        time=tree.xpath('//a[@node-type="feed_list_item_date"]/text()')[0]
        time=get_time(time)
        content=get_string(1,str(tree.xpath('//div[@node-type="feed_list_content"]//text()')))
        sentiment=nlp.get_sentiment(content[:190])   #若接口返回错误信息 默认为0
        image=get_string(1,str(tree.xpath('//ul/li[@action-type="feed_list_media_img" or @action-type="fl_pics"]/img/@src')))
        if image=='':
            image='无'
        if '微博视频' in str(tree.xpath('//div[@node-type="feed_list_content"]/a[last()][@action-type="feed_list_url"]/@title')):  #可能是视频/投票/位置/@
            video=tree.xpath('//div[@node-type="feed_list_content"]/a[last()][@action-type="feed_list_url"]/@href')[0]
        repost_num=tree.xpath('//span[@node-type="forward_btn_text"]/span/em[2]/text()')[0]
        comment_num=tree.xpath('//span[@node-type="comment_btn_text"]/span/em[2]/text()')[0]
        like_num=tree.xpath('//span[@node-type="like_status"]/em[2]/text()')[0]
        if comment_num=='评论':
            comment_num=0
        if repost_num=='转发':
            repost_num=0
        if like_num=='赞':
            like_num=0

        weibo_info.append(weibo_id)
        weibo_info.append(user_id)
        weibo_info.append(weibo_url)
        weibo_info.append(time)
        weibo_info.append(content)
        weibo_info.append(sentiment)
        weibo_info.append(image)
        weibo_info.append(video)
        weibo_info.append(int(repost_num))
        weibo_info.append(int(comment_num))
        weibo_info.append(int(like_num))
        return weibo_info
    except:
        print('微博信息获取失败\n')
        pass

    
def get_comment(comment_url,weibo_id):
    try:
        comment_all_info=[0,0]   #评论总分 评论数
        html=get_html(comment_url,2)
        tree=etree.HTML(html)
        comment_id_list=tree.xpath('//div[@node-type="root_comment"]/@comment_id')
        time_list=tree.xpath('//div[@node-type="root_comment"]//div[@class="WB_func clearfix"]/div[@class="WB_from S_txt2"]/text()')
        like_num_list=tree.xpath('//div[@node-type="root_comment"]//span[@node-type="like_status"]/em[2]/text()')
        for i in range(0,5):
            comment_info=[]
            comment_id=comment_id_list[i]
            time=get_time(time_list[i])
            content=get_string(1,str(tree.xpath('//div['+str(i+1)+'][@node-type="root_comment"]/div[@node-type="replywrap"]/div[@class="WB_text"]/text()')))
            like_num=like_num_list[i]
            sentiment=nlp.get_sentiment(content[:190])   #若接口返回错误信息 默认为0
            if like_num=='赞':
                like_num=0
            comment_info.append(comment_id)
            comment_info.append(weibo_id)
            comment_info.append(time)
            comment_info.append(content)
            comment_info.append(sentiment)
            comment_info.append(int(like_num))
            display_comment_info(comment_info)
            tb_comment_save(comment_info,db)
            comment_all_info[1]=comment_all_info[1]+1
            comment_all_info[0]=comment_all_info[0]+comment_info[4]
        return comment_all_info
    except:
        print('评论暂时无法查看或已全部获取\n')
        return comment_all_info
        pass
            
#数据库操作
def tb_user_save(user_info,db):
    cursor = db.cursor()
    sql = "INSERT INTO tb_user(user_id,user_home_url,nick_name,location,\
    gender,birthday,introduction,register_time,followers_num,fans_num,weibo_num)\
    VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
    (user_info[0],user_info[1],user_info[2],user_info[3],user_info[4],user_info[5],user_info[6],user_info[7],user_info[8],user_info[9],user_info[10])
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print('用户信息存储失败\n')
def tb_weibo_save(weibo_info,db):
    cursor = db.cursor()
    sql = "INSERT INTO tb_weibo(weibo_id,user_id,weibo_url,time,\
    content,sentiment,image,video,repost_num,comment_num,like_num)\
    VALUES ('%s','%s','%s','%s','%s',%s,'%s','%s',%s,%s,%s)" % \
    (weibo_info[0],weibo_info[1],weibo_info[2],weibo_info[3],weibo_info[4],weibo_info[5],weibo_info[6],weibo_info[7],weibo_info[8],weibo_info[9],weibo_info[10])
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print('微博信息存储失败\n')
def tb_comment_save(comment_info,db):
    cursor = db.cursor()
    sql = "INSERT INTO tb_comment(comment_id,weibo_id,time,content,sentiment,like_num)\
    VALUES ('%s','%s','%s','%s',%s,%s)" % \
    (comment_info[0],comment_info[1],comment_info[2],comment_info[3],comment_info[4],comment_info[5])
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print('评论信息存储失败\n')
def tb_avg_sentiment_save(weibo_id,sentiment,time,db):
    cursor = db.cursor()
    sql = "INSERT INTO tb_avg_sentiment(weibo_id,sentiment,time)\
    VALUES ('%s',%s,'%s')" % \
    (weibo_id,sentiment,time)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print('平均情感指数存储失败')



#检查微博用户id是否已存在 返回1存在
def tb_weibo_check(weibo_id):
    cursor = db.cursor()
    sql = "select count(*) from tb_weibo where weibo_id='"+weibo_id+"'"
    cursor.execute(sql)
    results = cursor.fetchall()
    return results[0][0]
def tb_user_check(user_id):
    cursor = db.cursor()
    sql = "select count(*) from tb_user where user_id='"+user_id+"'"
    cursor.execute(sql)
    results = cursor.fetchall()
    return results[0][0]
    

def get_hot_weibo():   #热门微博
    weibo_count=0
    while(1):
        try:
            html=get_html('https://d.weibo.com',0)#热门微博的地址#######################################
            tree=etree.HTML(html)
            weibo_id_list=tree.xpath('//div[@action-type="feed_list_item"]/@mid')     
            weibo_url_list=tree.xpath('//div[@action-type="feed_list_item"]//a[@node-type="feed_list_item_date"]/@href')   
            for i in range(0,7):#一页7条                         #先判断微博id是否存在
                if tb_weibo_check(weibo_id_list[i])==1:           #如果微博id存在，则用户信息也存在
                    print('微博已存在,ID：'+weibo_id_list[i]+'\n')
                    print('###############################################################')
                    continue
                weibo_info=get_weibo(weibo_url_list[i])         #微博id不存在再获取微博信息
                if tb_user_check(weibo_info[1])==1:           #如果微博id不存在，再判断用户id是否存在，若存在则不再请求用户信息，只保存微博信息，
                    print('用户已存在,ID：'+weibo_info[1]+'\n')
                else:         #如果用户不存在，则
                    user_home_url=get_url(1,weibo_info[1])
                    user_info=get_user_info(user_home_url)
                    display_user_info(user_info)
                    tb_user_save(user_info,db)
                display_weibo_info(weibo_info)
                tb_weibo_save(weibo_info,db)
                comment_url=get_url(4,weibo_info[0])
                comment_all_info=get_comment(comment_url,weibo_info[0])
                weibo_avg_sentiment=int((comment_all_info[0]+weibo_info[5])/(comment_all_info[1]+1))
                tb_avg_sentiment_save(weibo_info[0],weibo_avg_sentiment,weibo_info[3],db)
                weibo_count=weibo_count+1
                print('已采集'+str(weibo_count)+'条')
                print('###############################################################')
                time.sleep(1)
        except:
            print('###############################################################')
            continue
            
def weibo_sou(keyword,date):#搜微博
    html=get_html('https://s.weibo.com/weibo?q='+keyword+'&xsort=hot&suball=1&timescope=custom:'+date+':'+date+'&Refer=g',0)#热门微博的地址#######################################
    tree=etree.HTML(html)
    page_url=tree.xpath('//div[@class="m-page"]//li/a/@href')
    page_num=len(page_url)
    if page_num==0:         #搜索结果只有一页
        page_num=1
    for i in range(0,page_num):                #按页码数循环
        if page_num!=1:                        #若只有一页，则不再重新解析html
            page_url[i]=get_url(6,page_url[i])
            html=get_html(page_url[i],0)########################################
            tree=etree.HTML(html)
        weibo_num=html.count('feed_list_item')  #微博条数
        weibo_url_list=tree.xpath('//div[@action-type="feed_list_item"]//p[@class="from"]/a[1]/@href')
        weibo_id_list=tree.xpath('//div[@action-type="feed_list_item"]/@mid')
        for j in range(0,weibo_num):
            try:                                              #先判断微博id是否存在
                if tb_weibo_check(weibo_id_list[j])==1:           #如果微博id存在，则用户信息也存在
                    print('微博已存在,ID：'+weibo_id_list[j]+'\n')
                    print(date+'   第'+str(i+1)+'/'+str(page_num)+'页/第'+str(j+1)+'/'+str(weibo_num)+'条')
                    print('####################################################################')
                    continue   #微博id不存在再获取微博信息
                weibo_url=get_url(5,weibo_url_list[j])
                weibo_info=get_weibo(weibo_url)
                if tb_user_check(weibo_info[1])==1:           #如果微博id不存在，再判断用户id是否存在，若存在则不再请求用户信息，只保存微博信息，
                    print('用户已存在,ID：'+weibo_info[1]+'\n')
                else:         #如果用户不存在，则
                    user_home_url=get_url(1,weibo_info[1])
                    user_info=get_user_info(user_home_url)
                    display_user_info(user_info)
                    tb_user_save(user_info,db)
                display_weibo_info(weibo_info)
                tb_weibo_save(weibo_info,db)
                comment_url=get_url(4,weibo_info[0])
                comment_all_info=get_comment(comment_url,weibo_info[0])
                weibo_avg_sentiment=int((comment_all_info[0]+weibo_info[5])/(comment_all_info[1]+1))
                tb_avg_sentiment_save(weibo_info[0],weibo_avg_sentiment,weibo_info[3],db)
                print(date+'   第'+str(i+1)+'/'+str(page_num)+'页/第'+str(j+1)+'/'+str(weibo_num)+'条')
                print('####################################################################')
                time.sleep(1)
            except:
                print(date+'   第'+str(i+1)+'/'+str(page_num)+'页/第'+str(j+1)+'/'+str(weibo_num)+'条')
                print('####################################################################')
                pass
            
def get_person_weibo(user_id):
    try:
        if tb_user_check(user_id)==1:
            print('用户已存在')
        else:
            user_home_url=get_url(1,user_id)
            user_info=get_user_info(user_home_url)
            display_user_info(user_info)
            tb_user_save(user_info,db)
        for i in range(1,9999):
            weibo_count=0    #用于每页微博的计数
            weibo_ori_url=['','','']
            weibo_ori_url[0]='https://weibo.com/p/'+user_id+'?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page='+str(i)+'#feedtop'
            weibo_ori_url[1]='https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&profile_ftype=1&is_ori=1&pagebar=0&pl_name=Pl_Official_MyProfileFeed__21&id='+user_id+'&script_uri=/p/'+user_id+'&feed_type=0&page='+str(i)+'&pre_page='+str(i)+'&domain_op=100505&__rnd=1588661155111'
            weibo_ori_url[2]='https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&profile_ftype=1&is_ori=1&pagebar=1&pl_name=Pl_Official_MyProfileFeed__21&id='+user_id+'&script_uri=/p/'+user_id+'&feed_type=0&page='+str(i)+'&pre_page='+str(i)+'&domain_op=100505&__rnd=1588661155111'
            for j in range(0,3):
                if j==0:
                    html=get_html(weibo_ori_url[0],0)   #第一部分与二三部分解析方式不同
                else:
                    html=get_html(weibo_ori_url[j],1)
                tree=etree.HTML(html)
                weibo_num=html.count('feed_list_item')
                weibo_url_list=tree.xpath('//div[@action-type="feed_list_item"]//a[@node-type="feed_list_item_date"]/@href')
                weibo_id_list=tree.xpath('//div[@action-type="feed_list_item"]/@mid')
                for k in range(0,weibo_num):
                    try:
                        if tb_weibo_check(weibo_id_list[k])==1:
                            weibo_count=weibo_count+1
                            print('微博已存在,ID：'+weibo_id_list[k]+'\n')
                            print('第'+str(i)+'页第'+str(weibo_count)+'条')
                            print('####################################################################')
                            continue
                        weibo_url=get_url(3,weibo_url_list[k])
                        weibo_info=get_weibo(weibo_url)
                        display_weibo_info(weibo_info)
                        tb_weibo_save(weibo_info,db)
                        comment_url=get_url(4,weibo_info[0])
                        comment_all_info=get_comment(comment_url,weibo_info[0])
                        weibo_avg_sentiment=int((comment_all_info[0]+weibo_info[5])/(comment_all_info[1]+1))
                        tb_avg_sentiment_save(weibo_info[0],weibo_avg_sentiment,weibo_info[3],db)
                        weibo_count=weibo_count+1
                        print('第'+str(i)+'页第'+str(weibo_count)+'条')
                        print('####################################################################')
                        time.sleep(1)
                    except:
                        pass
    except:
        print('所有微博已爬取完毕！')
        pass
    
        
if __name__ == '__main__':
    begin_time=time.time()
    try:
        db=pymysql.connect(config_mysql_hostname,config_mysql_username,config_mysql_password,config_mysql_dbname)
        
        if config_mode==1:
            get_hot_weibo()
        if config_mode==2:
            dates=get_dates(config_begin_date,config_end_date)    #获取日期范围列表
            for date in dates:
                weibo_sou(config_keyword,date)
        if config_mode==3:
            get_person_weibo(config_user_id)
    except:
        end_time=time.time()   #记录时间信息
        run_time=end_time-begin_time
        start_time=time.localtime(begin_time)
        err_time=time.localtime(end_time)
        print('系统开始时间：'+str(start_time[0])+'年'+str(start_time[1])+'月'+str(start_time[2])+'日'+str(start_time[3])+':'+str(start_time[4]))
        print('系统结束时间：'+str(err_time[0])+'年'+str(err_time[1])+'月'+str(err_time[2])+'日'+str(err_time[3])+':'+str(err_time[4]))
        print('共运行'+str(round(run_time/60,2))+'分钟')



import pymysql
import time
from config_chart import *
import pyecharts.options as opts
from pyecharts.charts import Line
import os
import jieba

db=pymysql.connect(config_mysql_hostname,config_mysql_username,config_mysql_password,config_mysql_dbname)

def get_date_sentiment_by_keyword(db):
    cursor = db.cursor()
    sql ='''SELECT DATE_FORMAT( time, '%Y-%m-%d' ) AS '时间',round(AVG( sentiment ) ,0) AS '情感指数'
            FROM tb_avg_sentiment 
            WHERE weibo_id IN (SELECT weibo_id FROM tb_weibo 
                               WHERE content LIKE '%'''+config_keyword+'''%'
                               AND time >= "'''+config_begin_date+'''" AND time <= "'''+config_end_date+'''" )
            GROUP BY DATE_FORMAT( time, '%Y-%m-%d' )'''

    cursor.execute(sql)
    date_sentiment = cursor.fetchall()
    return date_sentiment
def get_weibo_num_by_keyword(db):
    cursor = db.cursor()
    sql ='''SELECT count(*) FROM tb_weibo 
            WHERE content LIKE '%'''+config_keyword+'''%'
            AND time > "'''+config_begin_date+'''" AND time < "'''+config_end_date+'''"
        '''
    
    cursor.execute(sql)
    weibo_comment_num = cursor.fetchall()[0][0]
    return weibo_comment_num

def get_date_sentiment_by_uid(db):
    cursor = db.cursor()
    sql ='''SELECT DATE_FORMAT( time, '%Y-%m-%d' ) as '时间',round(AVG( sentiment ) ,0) as '情感指数'
            FROM(
                SELECT weibo_id,MIN(DATE_FORMAT( time, '%Y-%m-%d' )) AS time,round( AVG( sentiment ), 0 ) AS sentiment
                FROM(
                    (SELECT weibo_id,time,content,sentiment FROM tb_weibo 
                     WHERE user_id="'''+config_user_id+'''"
		    )
                    UNION ALL
                    (SELECT weibo_id,time,content,sentiment
                     FROM tb_comment 
                     WHERE weibo_id IN
                        (SELECT weibo_id FROM tb_weibo 
                         WHERE user_id="'''+config_user_id+'''"
                        )
		    )
                ) AS a 
                GROUP BY weibo_id ) AS b 
            GROUP BY DATE_FORMAT( time, '%Y-%m-%d' )'''
    cursor.execute(sql)
    date_sentiment = cursor.fetchall()
    return date_sentiment
def get_weibo_num_by_uid(db):
    cursor = db.cursor()
    sql ='''SELECT count(*) 
            FROM tb_weibo 
            WHERE user_id="'''+config_user_id+'''"
        '''
    cursor.execute(sql)
    weibo_comment_num = cursor.fetchall()[0][0]
    return weibo_comment_num

def get_nick_name(db):   #获取用户昵称
    cursor = db.cursor()
    sql ="SELECT nick_name from tb_user where user_id='"+config_user_id+"'"
    cursor.execute(sql)
    nick_name = cursor.fetchall()[0][0]
    return nick_name


def get_weibo_by_keyword(db):
    cursor = db.cursor()
    sql ='''SELECT content FROM tb_weibo 
            WHERE content LIKE '%'''+config_keyword+'''%'
            AND time >= "'''+config_begin_date+'''" AND time <= "'''+config_end_date+'''" '''
    cursor.execute(sql)
    weibo = cursor.fetchall()
    return weibo

def get_weibo_by_uid(db):
    cursor = db.cursor()
    sql ="SELECT content FROM tb_weibo WHERE user_id='"+config_user_id+"'"
    cursor.execute(sql)
    weibo = cursor.fetchall()
    return weibo

def get_txtfile(weibo,mode,nick_name):
    if mode==1:
        if os.path.isfile(config_keyword+'.txt')==False:
            with open(config_keyword+'.txt', 'a',encoding='utf-8') as file:
                for row in weibo:
                    file.write(row[0])
                    file.write('\n')
                file.close()
        else:
            pass
    if mode==2:
        if os.path.isfile(nick_name+'.txt')==False:
            with open(nick_name+'.txt', 'a',encoding='utf-8') as file:
                for row in weibo:
                    file.write(row[0])
                    file.write('\n')
                file.close()
        else:
            pass

def jiebaba(mode,nick_name):
    if mode==1:
        txt = open(config_keyword+'.txt', "r", encoding='utf-8').read()
    if mode==2:
        txt = open(nick_name+'.txt', "r", encoding='utf-8').read()
    words  = jieba.lcut(txt)
    counts = {}
    excludes = {}
    for word in words:
        if len(word) == 1:
            continue
        else:
            rword = word
        counts[rword] = counts.get(rword,0) + 1
    for word in excludes:
        del counts[word]
    items = list(counts.items())
    items.sort(key=lambda x:x[1], reverse=True) 
    for i in range(50):
        word, count = items[i]
        print ("{0:<10}{1:>5}".format(word, count))


def get_date(date_sentiment):   #获取横坐标数据
    date=[]
    for i in range(0,len(date_sentiment)):
        date.append(date_sentiment[i][0])
    return date
def get_sentiment(date_sentiment):   #获取纵坐标数据
    sentiment=[]
    for i in range(0,len(date_sentiment)):
        sentiment.append(date_sentiment[i][1])
    return sentiment


#生成图表
def get_chart(title):
    c = (
        Line(init_opts=opts.InitOpts(width="1300px",
                                     height="600px",
                                     page_title = "Result",
                                     renderer = "svg",
                                     bg_color="#FFFFFF"))
        .add_xaxis(date)    #传入时间值
        .add_yaxis('情感指数',
                   sentiment,     #传入情感值
                   is_smooth=True,
                   linestyle_opts=opts.LineStyleOpts(width=4),       #线条样式
                   label_opts=opts.LabelOpts(is_show= False,font_weight= 'bolder',position="inside"),)  
        .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=1),      #区域填充颜色透明度
            markline_opts=opts.MarkLineOpts(       #辅助线
                data=[
                    opts.MarkLineItem(type_="min", name="最小值"),
                    opts.MarkLineItem(type_="max", name="最大值"),
                    opts.MarkLineItem(type_="average", name="平均值"),
                ],
                precision= 1,   #辅助线精度
                label_opts=opts.LabelOpts(is_show= False),
            ),
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show= False),        #图例
            tooltip_opts=opts.TooltipOpts(trigger="axis",axis_pointer_type="cross"),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                max_=100,min_=-100,range_color=["#000000","#000000","#000000","#FF0000", "#FFBF00"],
                is_piecewise=False,
                ),
            datazoom_opts=opts.DataZoomOpts(range_start=0,range_end=100),       #范围调节器
            title_opts=opts.TitleOpts(title,
                                      pos_top="1%",
                                      pos_left="center",
                                      title_textstyle_opts=opts.TextStyleOpts(font_size=20,       #标题字体
                                                                              font_family="Arial")),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(font_weight= 'bold'),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(width=2),symbol=['none', 'arrow']),   #调整轴线
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                boundary_gap=True   #左右留白
            ),
            yaxis_opts=opts.AxisOpts(
                min_=-100,         #刻度范围
                max_=100,
                axislabel_opts=opts.LabelOpts(font_weight= 'bold'),     #刻度标签字体
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(width=2),symbol="arrow")
            ),
        )
        .render("Result.html")
    )

if config_mode==1:     #关键词分析
    print('关键词：'+config_keyword)
    print('时间范围：'+config_begin_date+'至'+config_end_date)
    print('正在查询数据库...')
    weibo_num=get_weibo_num_by_keyword(db)
    print('共'+str(weibo_num)+'条相关微博')
    print('正在生成图表...')
    date_sentiment=get_date_sentiment_by_keyword(db)
    date=get_date(date_sentiment)
    sentiment=get_sentiment(date_sentiment)
    title='关键词"'+config_keyword+'"'+'微博情感指数趋势'
    get_chart(title)
    print('图表已生成！')
    #os.system('result.html')
    print('正在统计词频...')
    time.sleep(3)
    weibo=get_weibo_by_keyword(db)
    get_txtfile(weibo,1,'')
    jiebaba(1,'')

if config_mode==2:   #用户分析
    nick_name=get_nick_name(db)
    print('用户ID：'+config_user_id)
    print('用户昵称：'+nick_name)
    print('正在查询数据库...')
    weibo_num=get_weibo_num_by_uid(db)
    print('共'+str(weibo_num)+'条原创微博')
    print('正在生成图表...')
    date_sentiment=get_date_sentiment_by_uid(db)
    date=get_date(date_sentiment)
    sentiment=get_sentiment(date_sentiment)
    title='用户"'+nick_name+'"微博情感指数趋势',
    get_chart(title)
    print('图表已生成！')
    print('正在统计词频...')
    time.sleep(3)
    weibo=get_weibo_by_uid(db)
    get_txtfile(weibo,2,nick_name)
    jiebaba(2,nick_name)
    



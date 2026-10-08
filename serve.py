import socket#导入socket模块，提供了网络通信的功能
import threading#导入threading模块，提供了多线程的功能
import time#导入time模块，提供了时间相关的功能
import jieba#导入jieba模块，提供了中文分词的功能
from wordcloud import WordCloud#从wordcloud模块导入WordCloud类，提供了生成词云的功能
from collections import Counter#从collections模块导入Counter类，提供了计数器的功能
import re#导入re模块，提供了正则表达式的功能
import requests#导入requests模块，提供了发送HTTP请求的功能
from bs4 import BeautifulSoup#从bs4模块导入BeautifulSoup类，提供了解析HTML的功能

clients = []#定义一个空列表来存储所有连接到服务器的客户端socket对象
clients_lock = threading.Lock()#定义一个锁对象来保护对clients列表的访问，避免多线程同时修改列表导致数据不一致的问题

#爬虫功能的代码，使用requests库来发送HTTP请求，获取网页内容，并使用BeautifulSoup库来解析HTML，提取需要的信息.
def crawl_web(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        wangye=requests.get(url,headers=headers,timeout=5)#发送HTTP GET请求，参数是URL地址、请求头和超时时间
        
        wangye.encoding = 'utf-8'
        html = wangye.text#获取网页内容的文本表示
    except requests.RequestException as e:  #捕获请求异常，参数是异常对象
        print(f"爬取网页时发生错误：{e}")#打印错误信息
        return "爬取网页时发生错误！"
    soup = BeautifulSoup(html, 'html.parser')#使创建一个BeautifulSoup对象来解析HTML，参数是HTML内容和解析器类型
    text = soup.get_text()#使用get_text()方法提取网页中的文本内容，存储在text变量中
    text = re.sub(r'\s+', ' ', text).strip()#使用正则表达式去掉文本中的多余空白字符，存储在text变量中
    preview = text[:200]#获取文本的前200个字符作为预览，存储在preview变量中
    return preview#返回预览文本，方便在服务器中调用这个函数


#定义一个函数来广播消息给所有连接到服务器的客户端，参数是要广播的消息
def broadcast(message):
    with clients_lock:
        for sock, _ in clients:
            try:
                sock.send(message.encode('utf-8'))
            except:
                pass

STOPWORDS = set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '也', '都', '这', '那', '你', '他', '她', '它', '我们', '他们', '你们', '一个', '没有', '自己', '这个', '那个', '什么', '怎么', '可以', '因为', '所以', '但是', '如果', '虽然', '然后', '而且', '或者', '对于', '关于', '以及', '等等'])



#定义一个函数来统计聊天记录中每个词出现的次数，参数是聊天记录的文本内容，返回一个字典，键是词，值是出现的次数
#就是词频统计的函数，先用正则表达式去掉文本中的标点符号和特殊字符，然后用jieba分词对文本进行分词，最后用Counter统计每个词出现的次数，并过滤掉停用词。
def stats_liaotianjilu():
    try:
        with open("liaotianjilu.txt", "r", encoding="utf-8") as f:
            content = f.read()#阅读完liaotianjilu.txt文件的内容，存储在content变量中
    except FileNotFoundError:
        return "聊天记录文件不存在！"#如果文件不存在，就返回一个提示消息

    pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] .+?：(.+?)\n' #定义一个正则表达式模式，匹配聊天记录中的时间戳和用户名部分
    messages = re.findall(pattern, content)#使用re.findall()函数根据正则表达式模式从content中提取出所有的消息文本，存储在messages列表中
    if not messages:
        return "聊天记录中没有消息！"#如果没有提取到任何消息，就返回一个提示消息
    
    wenben_str = ''.join(messages)#将所y有消息文本连接成一个字符串，存储在wenben_str变量中
    #' '.join(messages) 是字符串的 join 方法，意思是：用空格 ' ' 作为连接符，把列表 messages 中的所有字符串拼接成一个大的字符串。
    words = jieba.lcut(wenben_str)#使用jieba.lcut()函数对wenben_str进行分词，返回一个列表，存储在words变量中
    #现在words是一个包含了聊天记录中所有词语的列表，其中可能包含一些停用词，我们需要过滤掉这些停用词。

    wenben_str_guolv = [word for word in words if word not in STOPWORDS and len(word) > 1]
    #使用列表推导式过滤掉停用词和长度小于等于1的词，存储在filtered_words变量中
    #列表推导式的语法是：[expression for item in iterable if condition]，意思是：对于iterable中的每个item，如果满足condition条件，就把expression的结果添加到新的列表中。
    cipin = Counter(wenben_str_guolv)#使用Counter类统计filtered_words中每个词出现的次数，返回一个字典，存储在cipin变量中
    top5 = cipin.most_common(5)#使用Counter的most_common()方法获取出现次数最多的前5个词，返回一个列表，存储在top5变量中

    ciyun = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',#指定字体路径，解决中文乱码问题
        width=800,
        height=400,
        background_color='white'
    )
    ciyun.generate_from_frequencies(cipin)#根据词频生成词云
    ciyun.to_file("liaotianciyun.png")#将生成的词云保存为图片文件

    top5_str = '\n'.join([f"{word}: {count}" for word, count in top5])#将top5列表中的词和对应的次数格式化成字符串，存储在top5_str变量中
    return top5_str#返回top5_str字符串，方便在服务器中调用这个函数




##这是双方开始交流的部分，服务器接收客户端发送的数据，并回复一个消息给客户端。最后关闭连接。
##先定义一个函数来处理客户端连接，参数是客户端的socket对象，在这个函数里进行数据的接收和发送。
def handle_client(client_socket):
#必须新增三个功能：接收客户端发送的昵称，
# 打印连接成功的消息；接收客户端发送的数据，打印帅哥说了什么；
#  维护一个列表来存储所有连接到服务器的客户端socket对象，这样就可以实现群聊了。
#1.接收客户端发送的昵称，打印连接成功的消息
    try:
        name_bytes = client_socket.recv(1024)#接收客户端发送的昵称，参数是接收的最大字节数
        if not name_bytes:
           client_socket.close()#如果没有收到昵称，就关闭连接
           return
        else:
            name = name_bytes.decode('utf-8')#解码成字符串
    except :
      client_socket.close()#如果接收昵称时发生异常，也关闭连接
      return
#2.接收客户端发送的数据，打印帅哥说了什么；维护一个列表来存储所有连接到服务器的客户端socket对象，这样就可以实现群聊了。
    with clients_lock:#使用锁来保护对clients列表的访问，避免多线程同时修改列表导致数据不一致的问题
              clients.append((client_socket, name))#将客户端socket对象和昵称添加到clients列表中，方便后续发送消息给所有客户端
#3.广播新用户加入的消息
    welcome_msg = f"{name}加入了聊天室！"#构造欢迎消息，告诉其他客户端有新的帅哥加入了聊天室
    broadcast(welcome_msg)#调用broadcast函数广播消息
#4.进入消息接收和发送的循环
    while True:
      data_bytes = client_socket.recv(1024)#recv()方法接收客户端发送的数据，参数是接收的最大字节数
      if not data_bytes:
        client_socket.close()#关闭客户端连接
        break
      else:
        data = data_bytes.decode('utf-8')#解码成字符串
        if data.strip() == '/stats':
            jieguo = stats_liaotianjilu()#调用统计聊天记录的函数，获取词频统计结果
            broadcast(f"聊天记录统计结果：\n{jieguo}")#广播统计结果给所有客户端
            continue#如果收到的消息是/stats，就调用统计函数，并广播结果给所有客户端，然后继续等待下一条消息
        if data.strip().startswith('/crawl'):
            url = data.strip()[6:].strip()#从消息中提取URL地址，假设消息格式是/crawl http://example.com
            jieguo = crawl_web(url)#调用爬虫函数，获取爬取网页的预览文本
            broadcast(f"爬取网页的结果：\n{jieguo}")#广播爬取结果给所有客户端
            continue#如果收到的消息以/crawl开头，就调用爬虫函数，并广播结果给所有客户端，然后继续等待下一条消息
        print(f"{name}说：{data}")#打印帅哥说了什么
        reply = "服务器已经受到帅哥的消息了！"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())#获取当前时间的字符串表示，格式为年月日时分秒
        broadcast(f"[{timestamp}] {name}说：{data}\n")#广播消息给所有客户端，告诉他们这个帅哥说了什么
        #这段代码是用来将每句话都保存在这个叫做liaotianjilu的聊天记录上
        with open("liaotianjilu.txt","a",encoding="utf-8") as f:
            f.write(f"[{timestamp}] {name}说：{data}\n")

##这是创建一个 TCP 服务器的代码，服务器会监听指定的端口，等待客户端连接，并与客户端进行简单的消息交流。
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 7891
server_socket.bind((host, port))#bind() 的作用是告诉操作系统：这个 socket 将使用 HOST:PORT 这个地址。之后客户端连接时，需要连接这个地址
server_socket.listen(5)#listen()让服务端socket变成被动接收连接状态，5是等待连接的最大数量，超过这个数量的连接会被拒绝
print("服务已开启，等待帅哥的连接")



#服务器进入一个无限循环，等待客户端连接，每当有一个客户端连接进来，就创建一个新的线程来处理这个连接，这样就可以同时处理多个客户端连接了。
while True:#服务器进入一个无限循环，等待客户端连接
  client_socket, addr = server_socket.accept()
#accept()会阻塞程序，直到有客户端连接进来，返回一个新的socket对象和客户端的地址
  print("帅哥连接成功，地址是：", addr)
  t = threading.Thread(target=handle_client, args=(client_socket,))#创建一个新的线程来处理这个客户端连接，target是线程要执行的函数，args是传递给函数的参数
  t.start()







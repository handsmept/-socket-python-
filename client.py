import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 7891
client_socket.connect((host, port))#connect()方法连接服务器，参数是服务器的地址 
#connect() 是客户端固定用法，向服务端发起 TCP 三次握手。
# 如果连接成功，就可以用这个 socket 收发数据；如果失败（如服务端没开），会抛出异常。
name = input("请输入你的名字\n")
print(f"你好，{name}！")
client_socket.send(name.encode('utf-8'))# 向服务端发送当前客户端的昵称，方便在聊天室里区分不同的客户端。

##这是客户端与服务器交流的部分，客户端发送一个消息给服务器，并接收服务器的回复。最后关闭连接。
while 1:
  msg = input("请输入您想要说的话（输入'quit'退出，输入'/stats'查看聊天记录统计,输入'/crawl url'爬取网页新闻）：\n")
  if msg == "quit":
    break
  else:
   client_socket.send(msg.encode('utf-8'))#send()方法发送数据，参数是要发送的数据，必须是字节类型，所以需要编码
   reply = client_socket.recv(1024).decode('utf-8')#recv()方法接收服务器发送的数据，参数是接收的最大字节数  print("服务器说：", reply)
   print("服务器说：\n", reply)
client_socket.close()#关闭客户端socket


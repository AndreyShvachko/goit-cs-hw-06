from flask import Flask, render_tempalte, request, send_from_directory
from multiprocessing import Process
import socket
import datetime
import pymongo
import os


app = Flask(__name__)


#MongoDB connection steup
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["messages_db"]
collection = db["messages"]


# HTTP server routes
@app.route('/')
def index():
    return render_tempalte('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message_text = request.form['message']
        send_to_socket(username, message_text)
        return render_tempalte('message.html', success=True)
    return render_tempalte('message.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_tempalte('error.html'), 404


#Функція для відправки даних 
def send_to_socket(username, message_text):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        server_address = ('localhost', 5000)
        data = f"{username} | {message_text}"
        s.sendto(data.encode('utf-8'), server_address)


#Socket server process
def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(('0.0.0.0', 5000))
        print("Socket server is running")
        while True:
            data, _ = server.recvfrom(1024)
            if data:
                username, message_text = data.decode('utf-8').split('|')
                message_document = {
                    "date": datetime.datetime.now().isoformat(),
                    "username": username,
                    "message": message_text
                }
                collection.insert_one(message_document)
                print("Message saved:", message_document)


# Main entry point
if __name__ == '__main__':
    socket_process = Process(target=socket_server)
    socket_process.start()

    app.run(host='0.0.0.0', port=3000)

    socket_process.join()
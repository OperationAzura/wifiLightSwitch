from machine import Pin
import socket

line1 = Pin(13, Pin.OUT)
line2 = Pin(12, Pin.OUT)

def web_page():
  htmlFile = open("index.html", "r")
  html = htmlFile.read()
  htmlFile.close()
  #html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  #<link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  #h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  #border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  #.button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  #<p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  #<p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html

def run():  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        try:
            #response = ''
            request = conn.recv(1024)
            request = str(request)
            #print('Content = %s' % request)
            line1On = request.find('/?line1=on')
            line1Off = request.find('/?line1=off')
            line2On = request.find('/?line2=on')
            line2Off = request.find('/?line2=off')
            if line1On == 6:
                line1.value(1)
                response = 'line 1 on'
            elif line1Off == 6:
                line1.value(0)
                response = 'line 1 off'
            elif line2On == 6:
                line2.value(1)
                response = 'line 2 on'
            elif line2Off == 6:
                line2.value(0)
                response = 'line 2 off'
            else:
                response = web_page()
                
            #response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Access-Control-Allow-Origin: 192.*\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        except Exception as e:
            print('EXCEPTION!!!')
            s = str(e)
            
    conn.close()

# python
import requests
import re
import json
import commands
import base64

#proxies = {"http": "127.0.0.1:8080"} 
proxies = {}
headers = {'Host': 'loli-h.com',
	 'Origin': 'http://loli-h.com',
	 'Referer': 'http://loli-h.com/auth/login.php',
	 'User-Agent': 'Mozilla/5.0 (Intel Linux  AppleWebKit/537.36 (KHTML, like Gecko)',
	 'X-Requested-With': 'XMLHttpRequest'}

def getSession():
	return requests.Session()

def getpasskeyuaid(s):
	logincontent = s.get("http://loli-h.com/auth/login.php", headers=headers, proxies=proxies).content
	passkey = re.findall('Aes.Ctr.encry.*?"(.*?)".*?"(.*?)"', logincontent)[0][1]
	uaid = re.findall('uaid\=base64_encode\("(.*?)"', logincontent)[0]
	return passkey, uaid, s

def getpenu(userpass, passkey, uaid):
	passencrypted, newuaid = commands.getoutput('phantomjs /Users/chen/Downloads/LoginDemo/all.js %s %s %s'%(userpass, passkey, uaid)).split("\n")
	return passencrypted, newuaid

def loginstatus(s, newuaid, username, passencrypted):
	sc = s.post("http://loli-h.com/auth/_assp.php", headers=headers, data={"uaid": newuaid}, proxies=proxies).content
	postlogin = s.post("http://loli-h.com/user/_login.php", headers=headers, data={"email": username, "passwd": passencrypted, "remember_me": "no"}, timeout=10, proxies=proxies)
	code, msg = json.loads(postlogin.content)['code'], json.loads(postlogin.content)['msg']
	return code, msg, s

def qiandaos1(s):
	sl = s.get("http://loli-h.com/user/", headers=headers, proxies=proxies).content
	headers2 = headers
	headers2["Referer"] = "https://loli-h.com/user/"
	headers2["Accept"] = "application/json, text/javascript, */*; q=0.01"
	headers2["Origin"] = "http://loli-h.com"
	uaid = re.findall('uaid\=base64_encode\("(.*?)"', sl)[0]
	return s, uaid

def qiandaos2(s, uaid):
	newuaid = base64.encodestring(uaid).strip()
	headers2 = headers
	headers2["Referer"] = "https://loli-h.com/user/"
	headers2["Accept"] = "application/json, text/javascript, */*; q=0.01"
	headers2["Origin"] = "http://loli-h.com"
	sc = s.post("http://loli-h.com/auth/_assp.php", headers=headers2, data={"uaid": newuaid}, proxies=proxies).content
	qiandao = s.get("http://loli-h.com/user/_checkin.php", headers=headers2, proxies=proxies)
	qc = qiandao.content
	s.close()
	try:
		msg =  json.loads(qc)['msg']
		code = 1
	except:
		code = 0
		msg = ""
	return code, msg
import subprocess
from subprocess import call
from subprocess import Popen, PIPE
import random
import string
import os
import glob

def random_field(length):
	alpha = 'aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ'
	full = 'aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ-----'
	num = '0123456789'
	word = ''
	word +=random.choice(alpha)
	for i in range(length-2):
		word +=random.choice(full)

	word +=random.choice(alpha)
	return word

def random_values(length):
	alpha = 'aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ'
	allsym = 'aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ--//.@0123456789'
	word = ''
	x = random.randrange(4,11)
	for j in range(length):
		word += random.choice(alpha)
		for i in range(x-2):
			word += random.choice(allsym)
		word += random.choice(alpha)
		if j != length-1:
				word += ', '
	return word

def random_header():
	x = random.randrange(4,11)
	y = random.randrange(1,11)
	header = random_field(x) + ': ' + random_values(y)
	return header

def big_print():
	return (
		[("(0)  Send normal GET/POST request"),
		("(1)  Send HTTP header in chunks, with delay to avoid TCP combining multiple requests"),
		("(2)  Send HTTP header in very small chunks, say 1 byte, with delay to avoid TCP combining multiple requests"),
		("(3)  Send HTTP header in chunk with fields broken across two chunk boundaries"),
		("(4)  Send large HTTP header. Add random unknown fields or increase number of cookies to increase HTTP header size"),
		("(5)  Send HTTP packet without HOST field"),
		("(6)  Send HTTP packet without CONTENTLENGTH field"),
		("(7)  Send HTTP packet with least fields. Send smallest possible HTTP packet"),
		("(8)  Send additional cookies, large cookies"),
		("(9)  Send data in very small chunks. Say send data in 1 byte, add a delay in each send"),
		("(10) Send large size of data"),
		("(11) Send multiple HTTP request on a single connection"),
		("(12) Exit client after sending full packet without waiting for reponse"),
		("(13) Send partial data and exit the client"),
		("(14) Send partial header/data"),
		("(15) Send invalid characters, like Non-ASCII chars in fields"),
		("(16) Compress data and send as binary data"),
		("(17) Send large data to create buffer overflow situation"),
		("(18) Send invalid http request 404 error should come"),
		("(19) Send invalid data with valid http request")]
	)

def check_mapper(x):
	return {

		1: checker,
		2: checker,
		3: checker,
		4: checker,
		5: checker,
		6: checker,
		7: checker_7,
		8: checker,
		9: checker,
		10: checker,
		11: checker_11,

		15: checker_15,
		16: checker,
		17: checker,
		18: checker_18,
		19: checker_19,
	}.get(x, do_nothing)

def get_response(path):
	to_check = []
	try:
		rsp = open(path)
	except FileNotFoundError as fnfe:
		return to_check
	total_lines = sum(1 for _ in rsp)
	rsp.seek(0)
	i = 0
	while i < total_lines:
		try:
			temp = rsp.readline().strip('\n')
			to_check.append(temp)
			i += 1
		except UnicodeDecodeError as ude:
			i += 1
			continue
	rsp.close()
	count = 0
	i = 0
	if os.path.getsize(path) != 0:
		while to_check[i] != '':
			if 'Date: ' in to_check[i] or 'DATE: ' in to_check[i] or 'Expires: ' in to_check[i] or 'EXPIRES: ' in to_check[i]:
				del to_check[i]
				count += 1
			else:
				 i += 1
			if count == 2:
				break
	#print(to_check)
	return to_check

def do_nothing():
	pass

def checker():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '.txt'
	resp_i = get_response(path)
	if resp_0 != resp_i:
		result.write('Test_'+opt+': '+'NOT PASSED\n')
	else:
		result.write('Test_'+opt+': '+'PASSED\n')

def checker_6():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '.txt'
	resp_i = get_response(path)
	if '200 OK' in resp_i[0]:
		result.write('Test_'+opt+': '+'PASSED\n')
	else:
		result.write('Test_'+opt+': '+'NOT PASSED\n')

def checker_7():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '.txt'
	resp_i = get_response(path)
	i = 0
	while resp_0[i] != '' :
		del resp_0[i]
	while resp_i[i] != '' :
		del resp_i[i]
	if resp_0 != resp_i:
		result.write('Test_'+opt+': '+'NOT PASSED\n')
	else:
		result.write('Test_'+opt+': '+'PASSED\n')

def checker_11():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '_1' + '.txt'
	resp_11_1 = get_response(path)
	path_11_2 = 'response/response_' + opt + '_2' + '.txt'
	path_11_3 = 'response/response_' + opt + '_3' + '.txt'
	if resp_0 != resp_11_1:
		result.write('Test_'+opt+': '+'ERROR IN PROGRAM\n')
	else:
		size_2 = os.path.getsize(path_11_2)
		try:
			size_3 = os.path.getsize(path_11_3)
		except FileNotFoundError as fnfe:
			size_3 = 0
		if size_2 == 0 and size_3 == 0:
			result.write('Test_'+opt+': '+'PASSED\n')
		else:
			if get_response(path_11_2) != resp_0 or get_response(path_11_3) != resp_0:
				result.write('Test_'+opt+': '+'INCONSISTENCY\n')
			else:
				result.write('Test_'+opt+': '+'NOT PASSED\n')

def checker_15():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '.txt'
	resp_i = get_response(path)
	if resp_0 == resp_i:
		result.write('Test_'+opt+': '+'PASSED\n')
	else:
		result.write('Test_'+opt+': '+'NOT PASSED\n')

def checker_18():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '.txt'
	resp_i = get_response(path)
	if resp_0 == resp_i:
		result.write('Test_'+opt+': '+'NOT PASSED\n')
	else:
		if '200 OK' not in resp_i[0]:
			result.write('Test_'+opt+': '+'PASSED\n')
		else:
			result.write('Test_'+opt+': '+'INCONSISTENCY\n')

def checker_19():
	resp_0 = get_response('response/response_0.txt')
	path = 'response/response_' + opt + '.txt'
	resp_i = get_response(path)
	if msg[-2] == '\r\n':
		if resp_0 == resp_i:
			result.write('Test_'+opt+': '+'NOT PASSED\n')
		else:
			if '200 OK' not in resp_i[0]:
				result.write('Test_'+opt+': '+'PASSED\n')
			else:
				result.write('Test_'+opt+': '+'INCONSISTENCY\n')
	else:
		if resp_0 == resp_i:
			result.write('Test_'+opt+': '+'PASSED\n')
		else:
			result.write('Test_'+opt+': '+'ERROR IN PROGRAM\n')

def mapper(x):
	return {
		-1: m_one,
		0: zero,
		1: one,
		2: two,
		3: three,
		4: four,
		5: five,
		6: six,
		7: seven,
		8: eight,
		9: nine,
		10: ten,
		11: eleven,
		12: twelve,
		13: thirteen,
		14: fourteen,
		15: fifteen,
		16: sixteen,
		17: seventeen,
		18: eighteen,
		19: nineteen,
	}.get(x, m_two)


def m_two(req_list,request):
	print('Incorrect Response, Try again!\n')

def m_one(req_list,request):
	print('Simulation Ended, Check "Result.txt" for results. Responses are in "response" folder. Please Save this file in some other directory if you want to access them in future before running another simulation!!\n')

def zero(req_list,request):
	cmd = ['./mysslc',host,port,opt,request]
	call(cmd)

def one(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	for i in range(0,len(req_list)):
		cmd.append(req_list[i])
	call(cmd)

def two(req_list,request):
	cmd = ['./mysslc',host,port,opt,request]
	call(cmd)

def three(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	pos = (len(req_list[0]))//2
	cmd.append(req_list[0][:pos])
	cmd.append(req_list[0][pos:])
	length = len(req_list)
	if(req_list[length-2] == '\r\n'):
		for i in range(1,length-1):
			pos = req_list[i].find(':')
			if pos != -1 and pos >= 4:
				cmd.append(req_list[i][:pos-3])
				cmd.append(req_list[i][pos-3:pos+1])
				cmd.append(req_list[i][pos+1:])
			else:
				cmd.append(req_list[i])
		cmd.append(req_list[length-1])
	else:
		for i in range(1,length):
			pos = req_list[i].find(':')
			if pos != -1 and pos >= 4:
				cmd.append(req_list[i][:pos-3])
				cmd.append(req_list[i][pos-3:pos+1])
				cmd.append(req_list[i][pos+1:])
			else:
				cmd.append(req_list[i])
	call(cmd)

def four(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	for i in range(10):
		req_list.insert(1,random_header()+'\r\n')
	new_request = ''
	for i in range(len(req_list)):
		new_request += req_list[i]
	cmd.append(new_request)
	call(cmd)

def five(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	i = 1
	while i < len(req_list):
		if 'Host: ' in req_list[i] or 'HOST: ' in req_list[i]:
			break
		i += 1
	if i < len(req_list):
		del req_list[i]
		new_request = ''
		for i in range(len(req_list)):
			new_request += req_list[i]
		cmd.append(new_request)
		call(cmd)
	else:
		cmd.append(request)
		call(cmd)

def six(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	i = 1
	while i < len(req_list):
		if 'CONTENT-LENGTH: ' in req_list[i] or 'Content-Length: ' in req_list[i]:
			break
		i += 1
	if i < len(req_list):
		del req_list[i]
		new_request = ''
		if req_list[-2] == '\r\n':
			for i in range(len(req_list)-1):
				new_request += req_list[i]
		else:
			for i in range(len(req_list)):
				new_request += req_list[i]
		cmd.append(new_request)
		call(cmd)
	else:
		cmd.append(request)
		call(cmd)

def seven(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	new_request = ''
	if 'GET ' in req_list[0]:
		new_request = req_list[0] + '\r\n'
	elif 'POST ' in req_list[0]:
		i = 1
		while i < len(req_list)-1:
			if not (('CONTENT-LENGTH: ' in req_list[i]) or ('Content-Length: ' in req_list[i]) or (req_list[i] == '\r\n') ):
				del req_list[i]
			else:
				i += 1
		for j in range(len(req_list)):
			new_request += req_list[j]
	cmd.append(new_request)
	call(cmd)

def eight(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	i = 1
	while i < len(req_list):
		if 'Cookie: ' in req_list[i] or 'COOKIE: ' in req_list[i]:
			break
		i += 1
	if i < len(req_list):
		req_list[i] = req_list[i][:-2] + '; PHPSESSID=298zf09hf012fh2; csrftoken=u32t4o3tb3gg43; _gat=1; LSID=DQAAAK…Eaem_vYg; Path=/; Expires=Wed, 13 Jan 2021 22:23:01 GMT; Secure; HttpOnly; HSID=AYQEVn…DKrdst; Path=/; Expires=Wed, 13 Jan 2021 22:23:01 GMT; HttpOnly; SSID=Ap4P…GTEq; Path=/; Expires=Wed, 13 Jan 2021 22:23:01 GMT; Secure; HttpOnly; lu=Rg3vHJZnehYLjVg7qi3bZjzg; Expires=Tue, 15 Jan 2013 21:47:38 GMT; Path=/; Domain=.example.com; HttpOnly'
		for j in range(20):
			req_list[i] += '; ' + random_field(random.randrange(4,11)) + '=' + random_values(1)
		req_list[i] += '\r\n'
	else:
		temp = 'Cookie: '
		temp += 'PHPSESSID=298zf09hf012fh2; csrftoken=u32t4o3tb3gg43; _gat=1; LSID=DQAAAK…Eaem_vYg; Path=/; Expires=Wed, 13 Jan 2021 22:23:01 GMT; Secure; HttpOnly; HSID=AYQEVn…DKrdst; Path=/; Expires=Wed, 13 Jan 2021 22:23:01 GMT; HttpOnly; SSID=Ap4P…GTEq; Path=/; Expires=Wed, 13 Jan 2021 22:23:01 GMT; Secure; HttpOnly; lu=Rg3vHJZnehYLjVg7qi3bZjzg; Expires=Tue, 15 Jan 2013 21:47:38 GMT; Path=/; Domain=.example.com; HttpOnly'
		for j in range(20):
			temp += '; ' + random_field(random.randrange(4,11)) + '=' + random_values(1)
		temp += '\r\n'
		req_list.insert(1,temp)
	new_request = ''
	for i in range(len(req_list)):
		new_request += req_list[i]
	cmd.append(new_request)
	#print(new_request)
	call(cmd)

def nine(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	length = len(req_list)
	if req_list[length-2] == '\r\n':
		new_request = ''
		for i in range(length-1):
			new_request += req_list[i]
		cmd.append(new_request)
		cmd.append(req_list[length-1])
	else:
		cmd.append(request)
	call(cmd)

def ten(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	length = len(req_list)
	if 'POST' in req_list[0]:
		i = 1
		while i < len(req_list):
			if 'CONTENT-LENGTH: ' in req_list[i] or 'Content-Length: ' in req_list[i]:
				break
			i += 1
		if i < len(req_list):
			del req_list[i]
		length = len(req_list)
		if req_list[length-2] == '\r\n':
			for i in range(length):
				cmd.append(req_list[i])
		else:
			for i in range(length):
				cmd.append(req_list[i])
			cmd.append('')
	else:
		cmd.append(request)
	call(cmd)

def eleven(req_list,request):
	cmd = ['./mysslc',host,port,opt,request]
	call(cmd)

def twelve(req_list,request):
	cmd = ['./mysslc',host,port,opt,request]
	call(cmd)

def thirteen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	new_request = ''
	length = len(request)//2
	for i in range(length):
		new_request += request[i]
	cmd.append(new_request)
	call(cmd)

def fourteen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	new_request = ''
	if req_list[len(req_list)-2] == '\r\n':
		for i in range(len(req_list)-1):
			new_request += req_list[i]
		length = (len(req_list[-1]))//2
		for i in range(length):
			new_request += req_list[-1][i]
	else:
		length = len(request)//2
		for i in range(length):
			new_request += request[i]
	cmd.append(new_request)
	call(cmd)

def fifteen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	req_list.insert(1,random_field(5)+'©: '+random_values(1)+'§\r\n')
	req_list.insert(1,random_field(5)+'¶: ¬'+random_values(1)+'\r\n')
	new_request = ''
	for i in range(len(req_list)):
		new_request += req_list[i]
	cmd.append(new_request)
	call(cmd)

def sixteen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	length = len(req_list)
	if req_list[length-2] == '\r\n':
		new_request = ''
		for i in range(length-1):
			new_request += req_list[i]
		cmd.append(new_request)
		cmd.append(req_list[length-1])
	else:
		cmd.append(request)
	call(cmd)

def seventeen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	length = len(req_list)
	if 'POST' in req_list[0]:
		i = 1
		while i < len(req_list):
			if 'CONTENT-LENGTH: ' in req_list[i] or 'Content-Length: ' in req_list[i]:
				break
			i += 1
		if i < len(req_list):
			del req_list[i]
		length = len(req_list)
		if req_list[length-2] == '\r\n':
			for i in range(length):
				cmd.append(req_list[i])
		else:
			for i in range(length):
				cmd.append(req_list[i])
			cmd.append('')
	else:
		cmd.append(request)
	call(cmd)

def eighteen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	i = 1
	while i < len(req_list):
		if 'Accept-Encoding: ' in req_list[i] or 'ACCEPT-ENCODING: ' in req_list[i]:
			break
		i += 1
	if i < len(req_list):
		del req_list[i]
	req_list.insert(1,'Accept-Encoding: asugdagd, saduih,tqq\r\n')
	if 'GET ' in req_list[0]:
		new_request = 'GETYT ' + url + ' KUCHBHI\r\n'
	else:
		new_request = 'POSTFH ' + url + ' KUCHBHI\r\n'
	for i in range(1,len(req_list)):
		new_request += req_list[i]
	cmd.append(new_request)
	call(cmd)

def nineteen(req_list,request):
	cmd = ['./mysslc',host,port,opt]
	if req_list[-2] == '\r\n':
		new_request = ''
		for i in range(len(req_list)-1):
			new_request += req_list[i]
		new_request += random_field(len(req_list[-1]))
		cmd.append(new_request)
	else:
		cmd.append(request)
	call(cmd)


#message = 'GET /fes-bin/public/portal/all/js/propalms.js HTTP/1.0 Accept: */* Accept-Encoding: gzip, deflate, sdch, br Accept-Language: en-US,en;q=0.8 Connection: keep-alive Cookie: httpOnly; httpOnly; httpOnly; httpOnly; httpOnly Host: 172.17.9.54 If-None-Match: "1cb4f-550d2fe65ec40-gzip" Referer: https://172.17.9.54/fes-bin/public/portal/act/loginPage.htm User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
#message = 'POST /fes_agent/sal HTTP/1.0 Accept: */* Accept-Encoding: gzip, deflate, br Accept-Language: en-us Connection: keep-alive Content-Length: 84 Content-Type: xml; charset=UTF-8 Cookie: httpOnly dataType: text Host: 172.17.9.54 Origin:https: //172.17.9.54 Referer:https: //172.17.9.54/fes-bin/public/portal/act/loginPage.htm User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 X-Component: FORTRESS SERVER CLIENT X-Requested-With: XMLHttpRequest <MESSAGE SIZE="95"><HEADER></HEADER><BODY><LOAD_REALM></LOAD_REALM></BODY></MESSAGE>'

'''msg = []
data = ''
x = 0
y = 0
z = 0
i = 0

while i < len(message):
	if i == len(message) - 1:
		msg.append(message[x:y])
		break
	if message[i] == '<':
		msg.append(message[x:y])
		data = message[i:]
		break
	if message[i] == ' ':
		y = i
	if message[i] == ':' and message[i+1] == ' ':
		msg.append(message[x:y])
		x = y + 1
		i = i + 2
	else:
		i = i + 1'''
print("\t\t\t\t\t\t\t\tWELCOME TO INVALID HTTP DATA SIMULATOR\n")

host = 'live.accops.com'
port = '443'

req_path = 'request/'

#for filename in os.listdir(req_path):
	# do your stuff
flag = 0
for filename in glob.glob(os.path.join(req_path, '*.txt')):
	# do your stuff
	flag += 1
	######### MAKE RESPONSE ##########
	fp = open(filename)
	#print('Current Request File is: '+filename+'\n')
	'''mode = input("Select MODE GET/POST (1/2): ")
	if mode == '1':
		fp = open('request_get.txt')
	elif mode == '2':
		fp = open('request_post.txt')
	else:
		print("Incorrect Response for Mode, Setting GET by default")
		fp = open('request_get.txt')'''

	################# Read and Strip \n
	stmts = []
	no_of_lines = sum(1 for _ in fp)
	fp.seek(0)

	stmts = [fp.readline().strip('\n') for i in range(no_of_lines)]
	fp.close()

	################ Find URL and Method
	sim_name = []
	if ':' not in stmts[0]:
		sim_name = list(stmts[0].split(' '))
		del stmts[0]
	msg = []
	found = 0
	i = 0
	url = ''
	method = ''
	while i < len(stmts):
		if 'Request URL' in stmts[i] or 'URL' in stmts[i]:
			pos = stmts[i].find(':') + 1
			while stmts[i][pos] == ' ':
				pos += 1
			url = stmts[i][(pos):]
			del stmts[i]
			found += 1
		elif 'Request Method' in stmts[i] or 'Method' in stmts[i]:
			pos = stmts[i].find(':') + 1
			while stmts[i][pos] == ' ':
				pos += 1
			method = stmts[i][(pos):]
			del stmts[i]
			found += 1
		else:
			i += 1
		if found == 2:
			break

	############## Remove blank lines from above & below
	while(stmts[len(stmts)-1] == '' or stmts[len(stmts)-1].isspace()):
		del stmts[len(stmts)-1]

	while(stmts[0] == '' or stmts[0].isspace()):
		del stmts[0]

	############## make msg without \r\n
	line = method + ' ' + url + ' ' + 'HTTP/1.0'
	msg.append(line)
	for stmt in stmts:
		msg.append(stmt)

	############# add \r\n to msg, make messagge, add ': ' if needed
	data = ''
	message = ''
	message += msg[0] + '\r\n'
	msg[0] = msg[0] + '\r\n'
	if method == 'POST' and (msg[len(msg)-2] == '' or msg[len(msg)-2].isspace()):
		data = msg[len(msg)-1]
		for i in range(1,len(msg)-1):
			pos = msg[i].find(':') + 1
			if pos != 0 and (pos != msg[i].find(': ') + 1):
				message = message + msg[i][:pos] + ' ' + msg[i][pos:] + '\r\n'
				msg[i] = msg[i][:pos] + ' ' + msg[i][pos:]
			else:
				message = message + msg[i] + '\r\n'
			if i < len(msg)-2: 
				msg[i] = msg[i] + '\r\n'
			
		message = message + data
		del msg[len(msg)-1]
		del msg[len(msg)-1]
		msg.append('\r\n')
		msg.append(data)

	else:
		for i in range(1,len(msg)):
			pos = msg[i].find(':') + 1
			if pos != 0 and (pos != msg[i].find(': ') + 1):
				message = message + msg[i][:pos] + ' ' + msg[i][pos:] + '\r\n'
				msg[i] = msg[i][:pos] + ' ' + msg[i][pos:]
			else:
				message = message + msg[i] + '\r\n'
			msg[i] = msg[i] + '\r\n'
		message = message + '\r\n'
		msg.append('\r\n')

	msg = tuple(msg)

	##########################################

	#print(message)
	#print(msg)
	#print(stmts)

	mode = None
	print('Current Request File is: '+filename)
	try:
		mode = int(input('Press 1 for Mannual Selection | Press 2 to run all simulations for request file | Press 0 to skip this file | Press -1 to exit simulator : '))
	except ValueError:
		print('Please Enter Integer Input Only!!')

	if mode == -1:
		break

	if mode == 0:
		continue

	if mode == 1:
		result_name = 'Result.txt'
		result = open(result_name,'w+')
		result.write('URL: '+host+url+':'+port+'\n')
		result.write('Method: '+method+'\n')
		result.write("Result:\n")
		while True:
			print("\n(-1) To quit simulator")																		#-----------------------MENU--------------------#

			for ind in big_print():
				print(ind)

			opt = input("Select Any one of the above: ")

			try:
				mapper(int(opt))((list)(msg),message)
			except ValueError:
				print('Please Enter Integer Input only!!')
				break

			if opt == '-1':
				break

			check_mapper(int(opt))()

		result.write("\n\nINDEX:\n")
		for ind in big_print():
			result.write(ind+'\n')
		result.close()

	elif mode == 2:
		result_name = 'result/Result'
		for i in sim_name:
			result_name += '_' + i
		result_name += '.txt'
		result = open(result_name,'w+')
		result.write('URL: '+host+url+':'+port+'\n')
		result.write('Method: '+method+'\n')
		result.write("Result:\n")
		can_try = [0,1,2,3,4,5,6,7,8,9,10,11,15,16,17,18,19]
		#for ind in big_print():
		#	print(ind)
		print('\nRunning Simulation, Please Wait.....\n')
		for i in can_try:
			opt = str(i)
			mapper(int(opt))((list)(msg),message)
			check_mapper(int(opt))()
		print('Simulation Successful, Check "results" folder for results. Responses are in "response" folder. Please Save these files in some other directory if you want to access them in future before running another simulation!!')
		print('Note: Simulations 12-14 should be done using mode 1 and check server logs to verify them.\n')
		result.write("\n\nINDEX:\n")
		for ind in big_print():
			result.write(ind+'\n')
		result.close()

	elif mode == None:
		pass

	else:
		print('Invalid Response')

if flag == 0:
	print('"request" folder empty, Please save some valid requests in ".txt" format to continue.')
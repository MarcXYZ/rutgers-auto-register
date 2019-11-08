'''By Marc Xu'''
import time
import requests
from getpass import getpass
from bs4 import BeautifulSoup
from datetime import datetime

WEB_REG = 'https://sims.rutgers.edu/webreg/chooseSemester.htm?login=cas'
EDIT_PAGE = 'https://sims.rutgers.edu/webreg/editSchedule.htm'
COURSE_ADD = 'https://sims.rutgers.edu/webreg/addCourses.htm'
COURSE_DROP = 'https://sims.rutgers.edu/webreg/dropCourse.htm'
CAS_AUTH = 'https://cas.rutgers.edu'

header = {
	'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}

course_limit = {
	'spring': 10,
	'summer': 5,
	'fall':	10,
	'winter': 5,
}

login_info = {
	'username': 'saitama',
	'password': ':P Nice Try',
	'authenticationType': 'Kerberos',
	'_eventId': 'submit',
	'submit': 'LOGIN',
}

def get_login():
	netid = raw_input('\nNetID: ')
	password = getpass()
	login_info['username'] = netid
	login_info['password'] = password

# Grab info
semester = raw_input('Semester: ').lower()
while semester not in course_limit:
	print('\nInvalid semester, choose from (Spring, Summer, Fall, Winter)\n')
	semester = raw_input('Semester: ').lower()

courses = raw_input('Course IDs: (Separated by spaces)\n\t').split()
while len(courses) > course_limit[semester]:
	print("MAX is %d courses, try again" % course_limit[semester])
	courses = raw_input('Course IDs: (Separated by spaces)\n\t').split()

get_login()

# Set register time (Optional)
reg_time = raw_input('\nRegister time (hh:mm): Press Enter to Skip')
while reg_time:
	hour, minute = reg_time.strip().split(':')
	try:
		hour = int(hour)
		minute = int(minute)
	except ValueError:
		print('Time format incorrect')
		reg_time = raw_input('\nRegister time (hh:mm): Press Enter to Skip')
		continue
	# Try login
	with requests.Session() as session:
		req = session.get(WEB_REG, headers=header)

		# Check if redircted to authorization
		while req.url.startswith(CAS_AUTH):
			auth_url = req.url
			# get form ready
			req = session.get(auth_url, headers=header)
			soup = BeautifulSoup(req.content, 'html.parser')
			login_info['execution'] = soup.find('input', attrs={'name': 'execution'})['value']
			login_info['lt'] = soup.find('input', attrs={'name': 'lt'})['value']
			# attempt log in
			req = session.post(auth_url, data=login_info, headers=header)
			# check log in status
			if req.url.startswith(CAS_AUTH):
				print('Incorrect NetID or Password, try again\n')
				get_login()
	# Timed wait
	now = datetime.today()
	reg_time = now.replace(hour=hour, minute=minute, second=00, microsecond=00)
	time.sleep((reg_time-now).seconds)
	break
	

with requests.Session() as session:
	req = session.get(WEB_REG, headers=header)

	# Check if redircted to authorization
	while req.url.startswith(CAS_AUTH):
		auth_url = req.url
		# get form ready
		req = session.get(auth_url, headers=header)
		soup = BeautifulSoup(req.content, 'html.parser')
		login_info['execution'] = soup.find('input', attrs={'name': 'execution'})['value']
		login_info['lt'] = soup.find('input', attrs={'name': 'lt'})['value']
		# attempt log in
		req = session.post(auth_url, data=login_info, headers=header)
		# check log in status
		if req.url.startswith(CAS_AUTH):
			print('Incorrect NetID or Password, try again\n')
			get_login()

	soup = BeautifulSoup(req.content, 'html.parser')

	# Find semester ID
	chosen = {
		'submit': 'Continue &#8594;'	# submit button
	}
	semester_id = 0
	for label in soup.findAll('label'):
		if label.text.strip().split()[0].lower() == semester:
			print('\nEnrollment for: %s' % label.text.strip().capitalize())
			semester_id = label.find('input')['value']
			chosen['semesterSelection'] = semester_id
			break

	# Post semester choice
	session.post(EDIT_PAGE, data=chosen, headers=header)
	
	# Prepare to submit course IDs
	data = {}
	for (i, ID) in enumerate(courses):
		data['coursesToAdd[%d].courseIndex' % i] = ID
		print ('\tAttempting to enroll in ' + ID)

	# Register
	response = session.post(COURSE_ADD, data=data, headers=header)
	
	soup = BeautifulSoup(response.content, 'html.parser')
	info = soup.find('div', attrs={'class':'info'})

	res = info.li
	# print('\n' + res.text)

	if res['class'][0] == u'ok':
		print('\nCurrently enrolled in: ')
		for dl in soup.findAll('dl', attrs={'class':'courses'}):
			print('\t' + dl.span.b.text)

	# # Drop courses
	# for course in courses:
	# 	data = {}
	# 	data['dropcourse'] = course
	# 	response = session.post(COURSE_DROP, data=data, headers=header)

	# 	soup = BeautifulSoup(response.content, 'html.parser')
	# 	info = soup.find('div', attrs={'class':'info'})
	# 	res = info.li
	# 	print('\n' + res.text)
	
#!/usr/bin/python
import datetime, sys

ID_CONTACT = 3
MIMETYPE = 2
DATA = [i for i in range(7,23)]

NUMBER = 5
NAME = 7

ID_SMS = 0
NUMBER_EXT = 2
TIMESTAMP = 4
IS_READ = 7
DIRECTION = 9
BODY = 12

class Contact:
	def __init__(self, ID):
		self.valid = False
		self.id = ID
		self.name = None
		self.number = None

	def __str__(self):
		ret = self.id
		if(self.name != None):
			ret += ':'+str(self.name)
		if(self.number != None):
			ret += ':'+str(self.number)
		return ret

class SMS:
	def __init__(self):
		self.id = None
		self.numberExt = None
		self.timestamp = None
		self.isRead = None
		self.direction = None
		self.body = None

	def __str__(self):
		ret = ''
		if(self.id != None):
			ret += str(self.id)
		if(self.numberExt != None):
			ret += ':'+str(self.numberExt)
		if(self.timestamp != None):
			ret += ':'+str(self.timestamp)
		if(self.isRead != None):
			ret += ':'+str(self.isRead)
		if(self.direction != None):
			ret += ':'+str(self.direction)
		if(self.body != None):
			ret += ':'+str(self.body)
		return ret

class Discuss:
	def __init__(self, numberExt):
		self.numberExt = numberExt
		self.contact = None
		self.firstTimestamp = None
		self.lastTimestamp = None
		self.sms = []

	def __gt__(self, other):
		return self.lastTimestamp > other.lastTimestamp

	def __ge__(self, other):
		return self.lastTimestamp >= other.lastTimestamp

	def toHTML(self, ID):
		ret = '<strong id="title-'+str(ID)+'" number="'+str(ID)+'">'
		ret += self.contact.name+'('+self.numberExt+')' if self.contact != None else self.numberExt
		ret += '</strong><table id="sub-'+str(ID)+'">'
		for sms in self.sms:
			ret += '<tr>'
			ret += '<td></td>' if sms.direction == 2 else ''
			ret += '<td><span class="italic">'+datetime.datetime.fromtimestamp(sms.timestamp).strftime("%a %d/%m/%Y %H:%M")+'</span><br/>'+sms.body+'</td>'
			ret += '<td></td>' if sms.direction == 1 else ''
			ret += '</tr>'
		ret += '</table><br/>'
		return ret

	def __str__(self):
		ret = self.contact.name+':\n' if self.contact != None else self.numberExt+':\n'
		for sms in self.sms:
			prefixe = '\t'
			prefixe += ' '*40 if sms.direction == 2 else ''
			ret += '\n'+prefixe+ datetime.datetime.fromtimestamp(sms.timestamp).strftime("%a %d/%m/%Y %H:%M")
			ret += setColumn(sms.body, 35, prefixe=prefixe)
			ret += '\n'
		return ret


def splitCSV(csvLine, separator, delimitor):
	ret = []
	currField = ''
	sepPassed = False
	inside = False
	for c in csvLine:
		if(inside and delimitor == c):
			inside = False
		elif(delimitor == c):
			inside = True
			currField = ''
		elif(inside and delimitor != c):
			currField += c
		elif(not inside and separator == c):
			ret.append(currField)
	return ret

def findContact(contactsDict, number=None):
	if(number != None):
		for i in contactsDict:
			if(contactsDict[i].number == number):
				return contactsDict[i]
	return None

def setColumn(s, length, prefixe=''):
	ret = '\n'+prefixe
	cmpt = 0
	for c in s:
		if(cmpt == length):
			ret += '\n'
			ret += prefixe
			cmpt = 0
		ret += c
		cmpt += 1
	return ret

if __name__ == "__main__":
	if('-h' in sys.argv):
		print("\
Usage: "+sys.argv[0]+" csvSMS [csvContacts] [file.html]\n\
\tcsvContacts and csvSMS are two files extract from android raw database with sqlitebrowser.\n\
\tcsvContacts: \"data\" table from contacts2.db\n\
\tcsvSMS: \"sms\" table from mmssms.db")
		exit(0)

	if(not len(sys.argv) in [2,3,4]):
		print("Usage: "+sys.argv[0]+" csvSMS [csvContacts] [file.html]")
		exit(0)

	contacts = {}
	if(len(sys.argv) != 2 and not(len(sys.argv) == 3 and sys.argv[2].endswith('.html'))):
		contactFile = open(sys.argv[2], 'rb')

		firstLine = True
		for row in contactFile.read().split('\n'):
			row = splitCSV(row, ",",'"')
			if(len(row) == 0):
				break
			if(firstLine):
				firstLine = False
				continue
			if(not row[ID_CONTACT] in contacts):
				contacts[row[ID_CONTACT]] = Contact(row[ID_CONTACT])
			if(int(row[MIMETYPE]) == NUMBER):
				contacts[row[ID_CONTACT]].number = row[DATA[4]]
			elif(int(row[MIMETYPE]) == NAME):
				contacts[row[ID_CONTACT]].name = row[DATA[1]]
		contactFile.close()

	smsFile = open(sys.argv[1], 'rb')

	discussions = {}
	firstLine = True
	for row in smsFile.read().split('\n'):
		row = splitCSV(row, ",",'"')
		if(len(row) == 0):
			break
		if(firstLine):
			firstLine = False
			continue
		if(not row[NUMBER_EXT] in discussions):
			discussions[row[NUMBER_EXT]] = Discuss('+'+row[NUMBER_EXT])
			discussions[row[NUMBER_EXT]].contact = findContact(contacts, number='+'+row[NUMBER_EXT])
		currSms = SMS()
		currSms.id = int(row[ID_SMS])
		currSms.numberExt = '+'+row[NUMBER_EXT]
		currSms.timestamp = int(row[TIMESTAMP][::-1][3:][::-1])
		currSms.isRead = int(row[IS_READ])
		currSms.direction = int(row[DIRECTION])
		currSms.body = row[BODY]
		discussions[row[NUMBER_EXT]].sms.append(currSms)
		if(currSms.timestamp > discussions[row[NUMBER_EXT]].lastTimestamp):
			discussions[row[NUMBER_EXT]].lastTimestamp = currSms.timestamp
		if(currSms.timestamp < discussions[row[NUMBER_EXT]].firstTimestamp):
			discussions[row[NUMBER_EXT]].firstTimestamp = currSms.timestamp
	
	smsFile.close()

	listConversation = []
	if(sys.argv[len(sys.argv)-1].endswith('html')):
		htmlOuput = open(sys.argv[len(sys.argv)-1], 'w')
		htmlOuput.write('<html><head><title>Android conversation</title><meta charset="utf-8"></head><body><h1>Conversation SMS</h1><hr/><input type="button" value="Expend" onclick="expendAll()" /><input type="button" value="Collapse" onclick="collapseAll()" /><hr/><br/>')
		cmpt = 1
		for c in discussions:
			listConversation.append(discussions[c])
		listConversation.sort(reverse=True)
		for d in listConversation:
			htmlOuput.write(d.toHTML(cmpt))
			cmpt += 1
		htmlOuput.write('<style>strong{cursor:pointer}.italic{font-size:0.8em;font-style:italic}body{font-family:arial}table{width:100%;border:1px black solid;border-radius:10px;}td{width:50%}</style><script>var cmpt = 1;\nwhile(true){\nvar title = document.getElementById("title-"+cmpt);\nif(title !== null){\ndocument.getElementById("sub-"+cmpt).hidden = true;\ntitle.onclick = function(){\nvar sub = document.getElementById("sub-"+this.getAttribute("number"));\nsub.hidden = !sub.hidden;\n};\n}else{\nbreak;\n}cmpt++;\n}\nfunction change(b){\nvar cmpt = 1;\nwhile(true){\nvar title = document.getElementById("title-"+cmpt);\nif(title !== null){\ndocument.getElementById("sub-"+cmpt).hidden = b;\n}\nelse{\nbreak;}\ncmpt++;\n}\n};\nfunction expendAll(){\nchange(false);\n}\nfunction collapseAll(){\nchange(true);\n}\n</script></body></html>')
		htmlOuput.close()
	else:
		for c in discussions:
			listConversation.append(discussions[c])
		listConversation.sort(reverse=True)
		for d in listConversation:
			print d
	

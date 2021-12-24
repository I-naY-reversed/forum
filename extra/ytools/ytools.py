_A='\x1b[0m'
import datetime,random,string
def log(s):print('\x1b[96m'+s+_A)
def warn(s,log=True):
	if log==True:
		with open('extra/ytools/log.yxl','a')as A:A.write(f"\n::Warning issued [{datetime.datetime.utcnow()}]::\n Details:"+s)
	print('\x1b[93m'+s+_A)
class Severity:
	nid=0
	def __init__(A,name,desc,id=nid+1):A.id=id;Severity.nid+=1;A.name=name;A.desc=desc
class Rep:
	def __init__(A,title,content,severity):
		C=severity;B=title;A.title=B;A.content=content;A.sev=C;warn(C.name+' level report has been issued.');D=string.ascii_letters+string.digits
		with open('extra/ytools/reps/'+B+str(''.join([A for A in random.choice(D)]))+'.yrep','w')as E:E.write('<|'+A.title+'|>\n\n'+A.conent+'\n\n'+A.sev.name+': '+A.sev.desc+'\n\n\n'+str(datetime.datetime.utcnow()))
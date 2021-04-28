from flask import Flask, render_template, request, abort
import csv
import re
import datetime
import difflib
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
app.static_folder = 'static'
# Channel Access Token
line_bot_api = LineBotApi('x7ssKkqI8hm6utdM1WJn635QPY6FcjlwXjtkjlskFiAZSpiVAixz2EVjOGUO/QIXF2iy9YiM8kQ+61y4qQ1y+m4JEyLNEtATLEE5esYtmrUjDD8tZbTDKq1+HLjTmclrrw5wvgtAGxhlJI2NkrRrxQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('8403ef9dfaa3dbf9ad6945784ca550d5')

currdate = (datetime.datetime.now()).timetuple().tm_yday            #ngambil tanggal saat ini sebagai hari ke n dari awal tahun
tasks=["ujian","kuis","pr","tubes","tucil"]                         #keyword jenis task
times=["hari","minggu"]                                             #keyword satuan waktu:
doneList=["sudah","telah","selesai","beres", "udah"]                #keyword selesai:
taskList = "pr|tubes|tucil|ujian|kuis"                              #taskList
deadlineKey = ["apa saja","apa aja", "sebutkan"]                    #keyword deadline
undurKey = ["undur","ubah", "ganti", "pindah"]                      #keyword undur

dictioneri = ["ujian","kuis","pr","tubes","tucil","hari","tanggal","minggu","sudah","telah","selesai","beres", "udah","saja", "sebutkan","undur","ubah", "ganti", "pindah"]


def DatetoInt(tanggal): #mengubah dari tanggal menjadi hari ke n dari awal tahun terus ngereturn integer hari ke n dari awal 
    tanggal = tanggal.strip()
    if(tanggal[1]=='/'):
        tanggal = '0'.strip() + tanggal.strip()
    tanggal = datetime.datetime.strptime(tanggal,"%m/%d/%Y")
    return tanggal.timetuple().tm_yday

def bacaDB(): # membaca database terus ngereturn list deadlinenya
    with open('databasenew.csv',newline='') as DB:
        reader = csv.reader(DB)
        listMatkul = []
        for row in reader:
            listMatkul.append(row)
    return listMatkul

def mirip(a,b):
    return difflib.SequenceMatcher(a=a.lower(),b=b.lower()).ratio()


def karakterUseless(text):
    textbaru = text
    for ch in ['\\',',','?','`','`','*','_','{','}','[',']','(',')','>','#','+','-','.','!','$','\'']:
        if ch in text:
            textbaru = textbaru.replace(ch,'')
    return textbaru

def tambahTugas(tanggal, matkul, jenis, topik): # fungsi untuk memasukkan tugas baru ke data base
    with open('databasenew.csv','a',newline='') as DB:
        tanggal = tanggal.strip()
        writer = csv.writer(DB)
        newTugas = [str(len(arrayDB)),tanggal,matkul.upper(),jenis.lower(),topik,"FALSE"]
        arrayDB.append(newTugas)
        writer.writerow(newTugas)

def tampilTugas(): # fungsi untuk menampilkan semua tugas yang belum beres
    isi= []
    for row in arrayDB:
        if(row[5]=="FALSE"):
            isi.append(row)
    return isi

def tampilTugasDayToDay(hariDua, hariSatu=currdate): #fungsi untuk menampilkan daftar deadline diantara 2 tanggal ngereturn list deadline
    temp=[]
    tempstr = ""
    for row in arrayDB:
        if(row[5]=="FALSE"):
            deadlineTugas = datetime.datetime.strptime(row[1],"%m/%d/%Y")
            deadlineTugas = deadlineTugas.timetuple().tm_yday
            if((deadlineTugas >= hariSatu) and (deadlineTugas <= hariDua)):
                temp.append(row)
    return temp

def tampilDeadline(jenis,matkul='all'): #berfungsi untuk menampilkan deadline dari matkul dengan jenis yg diinputkan
    isExist=False
    deadlinestr = ""
    if(matkul!='all'):
        for row in arrayDB:
            if(row[2].lower()==matkul and row[3].lower()==jenis):
                deadlineTugas = datetime.datetime.strptime(row[1],"%m/%d/%Y")
                deadlineTugas = deadlineTugas.timetuple().tm_yday
                if (deadlineTugas >= currdate):
                    deadlinestr += row[1] +" "+ row[4] + " ("+ row[2] + ")" + "<br>"
        return deadlinestr
        isExist=True
    else:
        for row in arrayDB:
            if(row[3].lower()==jenis):
                deadlineTugas = datetime.datetime.strptime(row[1],"%m/%d/%Y")
                deadlineTugas = deadlineTugas.timetuple().tm_yday
                if (deadlineTugas >= currdate):
                    deadlinestr += row[1] +" "+ row[4] + " ("+ row[2] + ")" + "<br>"
        return deadlinestr
        isExist=True 
    if isExist==False:
        return("tidak ada deadline terdaftar dari ",jenis," ",matkul)

def updateTanggal(id,tanggal):#berfungsi mengupdate task dengan ID id ke tanggal sesuai parameter
    tanggal = tanggal.strip()
    for row in arrayDB:
        if(row[0]==str(id)):
            row[1]=tanggal
    with open('databasenew.csv', 'w', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(arrayDB)

def isInDB(tanggal,matkul,jenis): #return boolean true jika ditemukan di db 
    tanggal = tanggal.strip()
    for row in arrayDB:
        if (row[1]==tanggal and row[2].lower()==matkul and row[3].lower()==jenis):
            return True
    return False

def done(id):#mengeset deadline dengan id sesuai parameter input menjadi true
    for row in arrayDB:
        if(row[0]==str(id)):
            row[5]='TRUE'
    with open('databasenew.csv', 'w', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(arrayDB)

def tampilHelp():
    return('''Gunakan keyword dibawah untuk mendapatkan hasil yang diinginkan <br>
<li>Untuk mengundur: 'undur' bersama dengan nomor tugas</li> <br>
<li>Menandai tugas sudah selesai: 'beres', 'selesai', 'telah', dan nomor tugas</li> <br>
<li>Menambah deadline matkul: 'ujian' or 'tubes' or 'tugas' or 'tucil' or 'kuis' + kode matkul + tanggal dalam format mm/dd/yyyy</li> <br>
<li>Menampilkan deadline: 'apa saja' + x hari / x minggu / hari ini / besok / minggu ini + tanggal deadline (mm/dd/yyyy) + jenis task (opsional)</li> <br>
<li>Nambah deadline: kode mata kuliah + 'ujian' or 'tubes' or 'tugas' or 'tucil' + mm/dd/yyyy + topik task menggunakan single quote (cth: 'milestone 3')</li> <br>
<li>Add ID line : @550fgvpw dan buka cetakcetekbot.herokuapp.com untuk some surprise </li> <br>''')

def patternMatching(pattern,teks):#Boyer-Moore
    m=len(pattern)
    n=len(teks)
    i=m-1
    dict={}
    for a in range(m):
        dict[pattern[a]]=a

    if(i>n-1):
        return False
    j=m-1
    while (i<n):
        if(pattern[j]==teks[i]):
            if(j==0):
                return True
            else:
                i=i-1
                j=j-1
        else:
            if (teks[i] in dict):
                lo = dict[teks[i]]
            else:
                lo = -1
            i = i + m - min(j, 1+lo)
            j = m-1
    return False


#list pencocokan
def isNewTask(input): #mengecek apakah mengandung keyword untuk menambahkan task baru
    for task in tasks:
        if (patternMatching(task,input)==True):
            return True
    return False

def isDeadlineList(input): #mengecek apakah mengandung keyword untuk menampilkan list deadline
    for DKey in deadlineKey: 
        if (patternMatching(DKey,input)==True):
            return True
    return False

def isDeadlineTask(input): #mengecek apakah mengandung keyword untuk menampilkan waktu deadline dari suatu task
    return  (patternMatching("kapan",input))

def isUndurTask(input): #mengecek apakah mengandung keyword untuk mengundur task
    for uKey in undurKey: 
        if (patternMatching(uKey,input)==True):
            return True
    return False

def isDoneTask(input): # mengecek apakah mengandung keyword untuk megubah status task 
    for pattern in doneList:
        if (patternMatching(pattern, input)==True):
            return True
    return False

def isHelp(input): # mengecek apakah mengandung keyword untuk menampilkan bantuan
    return ((patternMatching("bantu",input)) or (patternMatching("help",input)) or (patternMatching("perintah",input)))

def chat(): # main programnya gitu jadi ngeloop buat minta input terus sampe di input "STOP YA BEROW" baru berhenti loop
    command = input().lower()
    while (command != "stop ya berow"):
        reply(command)
        command = input().lower()
def ArrayToText1(arraynya):
    tempstr = ""
    for isi in arraynya:
        isistr = isi[0] + ') ' + isi[1] + ' • ' + isi[2] + ' • ' + isi[3]  + ' • ' + isi[4]
        tempstr += isistr + " <br>"
    tempstr = tempstr.replace("FALSE", "")
    if (tempstr == ""):
        return "Tidak ada deadline."
    return tempstr

def reply(command):#command nih input dari penggunanya yg nanti kita tentukan maksudnya mau ngapain di botnya

    if (isHelp(command)): # kalo isHelp dari input pengguna bernilai true tampilin daftar bantuan/Help
        return tampilHelp()

    elif (isUndurTask(command)): # kalo isUndurTask dari input bernilai true 
        x = re.findall("task \d+", command) + (re.findall("id \d+", command)) + (re.findall("tugas \d+", command))
        y = re.findall("../../....",command)
        if (x == []):           #kalo ga ketemu task yg ingin diundur print task ga ditemukan gt
            return("maaf sepertinya anda lupa menulis task mana yang ingin diundur")
        elif (y == []):         #kalo ga ketemu tanggal print kurang tanggal gt kek dia mau diundur ke tanggal brp
            return("anda belum menuliskan tasknya mau diundur ke tanggal berapa")
        else:                   #kalo ketemu task dan tanggalnya update tanggal di db terus print task telah diundur
            z = re.findall("\d+",x[0])
            if (z != []):
                updateTanggal(z[0],y[0])
                return("Task telah diundur")
            else :
                return("Tidak ada task tersebut di list task.")

    elif(isDoneTask(command)): # kalo isDoneTask dari input bernilai true 
        x = re.findall("task \d+", command) + re.findall("id \d+", command) + re.findall("tugas \d+", command)
        if (x==[]):     # cek kalo misal ga ada keyword task yg mana yg pengen diubah statusnya print gt klo tasknya belom terdeteksi
            return("Apakah Anda lupa memasukkan task mana yang sudah selesai dikerjakan?")
        else:       #kalo ketemu keyword tasknya update status task dengan id itu di db terus print kalo sudah ditandai selesai
            id=re.findall("\d+",x[0])
            if(id != []):
                done(id[0])
                return("oke task sudah ditandai sebagai telah selesai")
            else:
                return("Tidak ada task tersebut di list task.")

    elif(isDeadlineTask(command)): # kalo isDeadlineTask dari input true
        x = re.findall(taskList,command)
        y = re.findall("if\d+|ku\d+",command)
        if(x==[] and y==[]): #kalo misal ga ketemu jenis task dan matkulnya print format ga dikenal gt
            return("sepertinya kami tidak mengenal format yang anda masukkan")
        elif (x==[]): # kalo misal jenis taskny ga ketemu print jenisnya ga tau gt
            return("jenis task apa yang ingin anda ketahui deadlinenya")
        elif (y==[]): # sama kek bagian jenis task tapi ini matkul
            return tampilDeadline(x[0])
        else: # kalo keyword lengkap tampilin deadline dari matkul dan jenis task itu
            return tampilDeadline(x[0],y[0])

    elif(isDeadlineList(command)):
        x = re.findall("deadline",command)
        y = re.findall(taskList,command)
        listDeadline=[]
        ListDeadline=""
        printed=False
        if(x!=[] or y!=[]):# kalo keywordny mengandung jenis task atau kata deadline 
            deadlineHari=re.findall("\d+ hari ke\s*depan",command)
            deadlineMinggu=re.findall("\d+ minggu ke\s*depan",command)
            deadlineMingguini=re.findall("minggu ini",command)
            todayDeadline = re.findall("hari ini",command)
            BesokDeadline = re.findall("besok",command)
            fromDaytoDay = re.findall("../../....",command)
            
            if (deadlineHari):# cek apakah mau nampilin deadline n hari ke depan klo iy masukkin list deadlineny ke listDeadline dan tandain printed sebagai true 
                days=re.findall("\d+",deadlineHari[0])[0]
                listDeadline = tampilTugasDayToDay(currdate+int(days),currdate)
                ListDeadline += ArrayToText1(tampilTugasDayToDay(currdate+int(days),currdate))
                printed=True
            elif(deadlineMinggu):# ini bagian n minggu ke depan prinsipny kek n hari ke depantapi kali 7
                days=re.findall("\d+",deadlineMinggu[0])[0]
                listDeadline = tampilTugasDayToDay(currdate+int(days)*7,currdate)                
                ListDeadline += ArrayToText1(tampilTugasDayToDay(currdate+int(days)*7,currdate))
                printed=True
            elif(deadlineMingguini):# ini bagian n minggu ke depan prinsipny kek n hari ke depantapi kali 7
                listDeadline = tampilTugasDayToDay(currdate+7,currdate)                
                ListDeadline += ArrayToText1(tampilTugasDayToDay(currdate+7,currdate))
                printed=True
            elif(BesokDeadline):# ini bagian n minggu ke depan prinsipny kek n hari ke depantapi kali 7
                listDeadline = tampilTugasDayToDay(currdate+1,currdate+1)                
                ListDeadline += ArrayToText1(tampilTugasDayToDay(currdate+1,currdate+1))
                printed=True
            elif(todayDeadline): # bagian ini buat yg cek deadline hari ini
                listDeadline = tampilTugasDayToDay(currdate)
                ListDeadline += ArrayToText1(tampilTugasDayToDay(currdate))
                printed=True
            elif(len(fromDaytoDay)==2): # kalo ini dari 2 tanggal berbeda
                listDeadline = tampilTugasDayToDay(DatetoInt(fromDaytoDay[1]),DatetoInt(fromDaytoDay[0]))
                ListDeadline += ArrayToText1(tampilTugasDayToDay(DatetoInt(fromDaytoDay[1]),DatetoInt(fromDaytoDay[0])))
                printed=True
            elif(len(fromDaytoDay)==1): # kalo ini dari 1 tanggal berbeda
                listDeadline = tampilTugasDayToDay(DatetoInt(fromDaytoDay[0]),DatetoInt(fromDaytoDay[0]))
                ListDeadline += ArrayToText1(tampilTugasDayToDay(DatetoInt(fromDaytoDay[0]),DatetoInt(fromDaytoDay[0])))
                printed=True
            else:
                listDeadline = tampilTugas()
                ListDeadline += ArrayToText1(tampilTugas())
                printed=True
            

            listDeadline2=[] # ini buat nyimpen deadline yang jenis taskny ditemukan di command
            if(y!=[]):#kalo ketemu keyword jenis taskny
                for item in listDeadline:
                    if(item[3].lower()==y[0]):
                        listDeadline2.append(item) # masukkin deadline yg jenis taskny sm dengan keyword yang ditemukan ke listDeadline2
                if(listDeadline2!=[]):# kalo listDeadline2 ndak kosong print isiny
                    return ArrayToText1((listDeadline2))
                else: #kalo kosong print ga ada deadline yg ditemukan
                    return("tidak ada deadline yang ditemukan")

            else: # kalo ga ketemu keyword jenis tasknya
                if (ListDeadline!=""): #kalo ad deadline yg bs di print kita print ke layar
                    return (ListDeadline)

                if(ListDeadline==""): # kalo ga ada
                    if(x[0]=="deadline" and printed==False): #kalo mengandung keyword deadline berarti kan bs general kita print seluruh deadline karena ga masuk ke keyword waktu manapun
                        return ArrayToText1(tampilTugas())
                    else: # kalo ga ada keyword deadline dan kosong listDeadlinenya print kalo ga ada deadline
                        return("Tidak ada deadline yang ditemukan pada rentang tersebut")

        else: # kalo keyword deadline dan jenis task nggak ditemukan print ini
            return("sepertinya format tidak dikenali")

    elif(isNewTask(command)): #untuk nambahin task baru
        tanggal = re.findall("../../....",command)
        matkul = re.findall("if\d+|ku\d+",command)
        jenis = re.findall(taskList,command)
        topic_quoted = re.findall("'.+'",command) # topik dibatasi single quote mark
        if topic_quoted!=[]:
            topik = re.sub("'","",topic_quoted[0])
        else:
            topic_quoted = re.findall("tentang [^\n]+",command)
            if topic_quoted!=[]:
                topik = re.sub("'","",topic_quoted[0])
                topik = topik.replace("tentang ","")
            else:
                topik=""
        if(tanggal!=[] and matkul!=[] and jenis!=[] and topik!=[]):
            if(isInDB(tanggal[0],matkul[0],jenis[0])==True):
                return("Task tersebut sudah pernah tercatat, insertion failed") #kalo sudah ad di db print ke layar 
            else:
                tambahTugas(tanggal[0], matkul[0], jenis[0], topik)
                return ("insertion success") # kalo sukses print sukses
    else:
        katayangbenar = command
        kata = karakterUseless(command).split(' ')
        for a in kata:
            for b in dictioneri:
                if(mirip(a,b)>=0.75):
                    katayangbenar = katayangbenar.replace(a,b)
        if(katayangbenar != command):
            return("mungkin maksud anda "+ '"'+katayangbenar+'"')
        else :
            return("command tidak ditemukan") # kalo command nggak mengandung keyword apapun print ini



arrayDB=bacaDB()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = str(request.args.get('msg'))
    jawaban = (reply(userText.lower()))
    return jawaban



@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text=event.message.text
    hasil = (reply(text.lower())).replace("<br>","\n").replace("<li>","•").replace("</li>","")
    message = TextSendMessage(hasil)
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    app.run()
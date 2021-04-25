import csv
import re
import datetime

currdate = (datetime.datetime.now()).timetuple().tm_yday

def DatetoInt(tanggal):
    tanggal = datetime.datetime.strptime(tanggal,"%m/%d/%Y")
    return tanggal.timetuple().tm_yday

def bacaDB():
    with open('databasenew.csv',newline='') as DB:
        reader = csv.reader(DB)
        listMatkul = []
        for row in reader:
            listMatkul.append(row)
    return listMatkul

def tambahTugas(tanggal, matkul, jenis, topik):
    with open('databasenew.csv','a',newline='') as DB:
        writer = csv.writer(DB)
        newTugas = [str(len(arrayDB)),tanggal,matkul.upper(),jenis.upper(),topik,"FALSE"]
        arrayDB.append(newTugas)
        writer.writerow(newTugas)

def tampilTugas():
    for row in arrayDB:
        if(row[5]=="FALSE"):
            print(row)

def tampilTugasDayToDay(hariDua, hariSatu=currdate):
    temp=[]
    for row in arrayDB:
        if(row[5]=="FALSE"):
            deadlineTugas = datetime.datetime.strptime(row[1],"%m/%d/%Y")
            deadlineTugas = deadlineTugas.timetuple().tm_yday
            if((deadlineTugas >= hariSatu) and (deadlineTugas <= hariDua)):
                temp.append(row)
    return temp

def tampilDeadline(jenis,matkul):
    isExist=False
    for row in arrayDB:
        if(row[2].lower()==matkul and row[3].lower()==jenis):
            print(row[1],row[4])
            isExist=True
    if isExist==False:
        print("tidak ada deadline terdaftar dari ",jenis," ",matkul)

def updateTanggal(id,tanggal):
    for row in arrayDB:
        if(row[0]==str(id)):
            row[1]=tanggal
    with open('databasenew.csv', 'w', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(arrayDB)

def isInDB(tanggal,matkul,jenis):
    for row in arrayDB:
        if (row[1]==tanggal and row[2].lower()==matkul and row[3].lower()==jenis):
            return True
    return False

def done(id):
    for row in arrayDB:
        if(row[0]==str(id)):
            row[5]='TRUE'
    with open('databasenew.csv', 'w', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(arrayDB)

def tampilHelp():
    print('''
Udang Mayones merupakan salah satu menu favorit di restoran chinese atau restoran seafood. 
Udang digoreng renyah dengan balutan tepung dipadukan dengan campuran saus mayones yang segar. 
Ternyata menu restoran ini sangat mudah dibuat asalkan tahu tips & tricksnya. 
Cocok dijadikan camilan atau lauk untuk anak-anak dan keluarga di rumah.

Langkah:
1.  Belah udang menjadi potongan butterfly
2.  Masukkan jahe halus, baking soda, putih telur, garam, merica, dan sedikit tepung maizena. 
    Aduk rata lalu diamkan 10-15 menit di suhu ruangan
3.  Buat dynamite mayo original. 
    Campurkan mayones, air jeruk nipis, susu kental manis, dan madu. Aduk rata, tambahkan sedikit garam
4.  Buat dynamite mayo pedas dengan menambahkan saus sambal dan bawang putih. Aduk rata
5.  Setelah udang di marinasi, masukkan ke dalam tepung maizena, aduk rata hingga seluruh permukaannya terlapisi, lalu saring
6.  Goreng udang hingga matang, angkat lalu tiriskan
7.  Campur udang goreng dengan dynamite mayo, aduk rata
8.  Siapkan bihun jagung goreng, garnish dengan biji wijen hitam dan daun bawang. Udang Mayones siap disajikan

    ''')

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

#keyword jenis task
tasks=["ujian","kuis","tugas","tubes","tucil"]

#keyword satuan waktu:
times=["hari","minggu"]

#keyword selesai:
doneList=["sudah","telah","selesai","beres"]

#taskList
taskList = "tugas|tubes|tucil|ujian|kuis"

#list pencocokan
def isNewTask(input):
    for task in tasks:
        if (patternMatching(task,input)==True):
            return True
    return False

def isDeadlineList(input):
    return (patternMatching("apa saja",input))

def isDeadlineTask(input):
    return  (patternMatching("kapan",input))

def isUndurTask(input):
    return (patternMatching("undur",input))

def isDoneTask(input):
    for pattern in doneList:
        if (patternMatching(pattern, input)==True):
            return True
    return False

def isHelp(input):
    return ((patternMatching("bantu",input)) or (patternMatching("help",input)))

def chat():
    command = input().lower()
    while (command != "STOP YA BEROW"):
        reply(command)
        command = input().lower()

def reply(command):

    if (isHelp(command)):
        tampilHelp()

    elif (isUndurTask(command)):
        x = re.findall("task \d+", command)
        y = re.findall("../../....",command)
        if (x == []):
            print("maaf sepertinya anda lupa menulis task mana yang ingin diundur")
        elif (y == []):
            print("anda belum menuliskan tasknya mau diundur ke tanggal berapa")
        else:
            z = re.findall("\d+",x[0])
            updateTanggal(z[0],y[0])
            print("Task telah diundur")

    elif(isDoneTask(command)):
        x = re.findall("task \d+", command)
        if (x==[]):
            print("Apakah Anda lupa memasukkan task mana yang sudah selesai dikerjakan?")
        else:
            id=re.findall("\d+",x[0])[0]
            done(id)
            print("oke task sudah ditandai sebagai telah selesai")

    elif(isDeadlineTask(command)):
        x = re.findall(taskList,command)
        y = re.findall("if\d+|ku\d+",command)
        if(x==[] and y==[]):
            print("sepertinya kami tidak mengenal format yang anda masukkan")
        elif (x==[]):
            print("jenis task apa yang ingin anda ketahui deadlinenya")
        elif (y==[]):
            print("mata kuliah apa yang ingin anda ketahui deadline ",x[0],"nya")
        else:
            tampilDeadline(x[0],y[0])

    elif(isDeadlineList(command)):
        x = re.findall("deadline",command)
        y = re.findall(taskList,command)
        printed=False
        if(x!=[] or y!=[]):
            deadlineHari=re.findall("\d+ hari ke\s*depan",command)
            deadlineMinggu=re.findall("\d+ minggu ke\s*depan",command)

            todayDeadline = re.findall("hari ini",command)
            fromDaytoDay = re.findall("../../....",command)
            listDeadline=[]
            if (deadlineHari):
                days=re.findall("\d+",deadlineHari[0])[0]
                listDeadline = tampilTugasDayToDay(currdate+int(days),currdate)
                printed=True
            elif(deadlineMinggu):
                days=re.findall("\d+",deadlineMinggu[0])[0]
                listDeadline = tampilTugasDayToDay(currdate+int(days)*7,currdate)
                printed=True
            elif(todayDeadline):
                listDeadline = tampilTugasDayToDay(currdate)
                printed=True
            elif(fromDaytoDay):
                listDeadline = tampilTugasDayToDay(DatetoInt(fromDaytoDay[1]),DatetoInt(fromDaytoDay[0]))
                printed=True

            listDeadline2=[]
            if(y!=[]):
                for item in listDeadline:
                    if(item[3].lower()==y[0]):
                        listDeadline2.append(item)
                if(listDeadline2!=[]):
                    for row in listDeadline2:
                        print(row)
                else:
                    print("tidak ada deadline yang ditemukan")

            else:
                if (listDeadline!=[]):
                    for item in listDeadline:
                        print(item)

                if(listDeadline==[]):
                    if(x[0]=="deadline" and printed==False):
                        tampilTugas()
                        print()
                    else:
                        print("Tidak ada deadline yang ditemukan pada rentang tersebut")

        else:
            print("sepertinya format tidak dikenali")

    elif(isNewTask(command)):
        tanggal = re.findall("../../....",command)
        matkul = re.findall("if\d+|ku\d+",command)
        jenis = re.findall(taskList,command)
        topic_quoted = re.findall("'.+'",command) # topik dibatasi single quote mark
        if topic_quoted!=[]:
            topik = re.sub("'","",topic_quoted[0])
        else:
            topik=""
        if(tanggal!=[] and matkul!=[] and jenis!=[] and topik!=[]):
            if(isInDB(tanggal[0],matkul[0],jenis[0])==True):
                print("Task tersebut sudah tercatat, insertion failed")
            else:
                tambahTugas(tanggal[0], matkul[0], jenis[0], topik)
                print("insertion success")
    else:
        print("punten kang aing teu ngertos maneh ngomong naon")



arrayDB=bacaDB()
chat()

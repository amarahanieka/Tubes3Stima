import csv
import re
import datetime

fungsi =    {'tambahTugas': r'.*\s*tambah tugas*',
            'tampilTugas': r'.*tampilkan*',
            'tampilDeadline': r'.*cube.*(\d+)',
            'updateTanggal': r'.*cube.*(\d+)',
            'done': r'.*cube.*(\d+)',
            'help': r'.*bantu.*'
                }
currdate = (datetime.datetime.now()).timetuple().tm_yday

def bacaDB():
    with open('databasenew.csv',newline='') as DB:
        reader = csv.reader(DB)
        listMatkul = []
        for row in reader:
            listMatkul.append(row)
    return listMatkul

def patternMatching(pattern,teks):#Boyer-Moore
    m=len(pattern)
    n=len(teks)
    i=m-1
    dict={}
    for a in range(m):
        dict[pattern[a]]=a

    if(i>n-1):
        return -1
    j=m-1
    while (i<n):
        if(pattern[j]==teks[i]):
            if(j==0):
                return i
            else:
                i=i-1
                j=j-1
        else:
            lo = dict[teks[i]]
            i = i + m - min(j, 1+lo)
            j = m-1
    return -1
    
def tambahTugas(tanggal, matkul, jenis, topik):
    with open('databasenew.csv','a',newline='') as DB:
        writer = csv.writer(DB)
        newTugas = [str(len(arrayDB)),tanggal,matkul,jenis,topik,"FALSE"]
        arrayDB.append(newTugas)
        writer.writerow(newTugas)

def tampilTugas():
    for row in arrayDB:
        if(row[5]=="FALSE"):
            print(row)

def tampilTugasDayToDay(hariDua, hariSatu=currdate):
    for row in arrayDB:
        if(row[5]=="FALSE"):
            deadlineTugas = datetime.datetime.strptime(row[1],"%m/%d/%Y")
            deadlineTugas = deadlineTugas.timetuple().tm_yday
            if((deadlineTugas >= hariSatu) and (deadlineTugas <= hariDua)):
                print(row)
    
def tampilDeadline(matkul):
    for row in arrayDB:
        if(row[2]==matkul):
            print(row[1])

def tampilJenis(tugas):
    for row in arrayDB:
        if(row[3]==tugas):
            print(row)

def updateTanggal(id,tanggal):
    for row in arrayDB:
        if(row[0]==str(id)):
            row[1]=tanggal
    with open('databasenew.csv', 'w', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(arrayDB)

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

def chat():
    command = input().lower()
    while (command != "STOP YA BEROW"):
        reply(command)
        command = input().lower()

def reply(command):
    for key,value in fungsi.items():
        intent = key
        pattern = value
        found_match = re.match(pattern, command)
        if found_match and intent =='tambahTugas':
            return tambahTugas('4/24/2021','OOP','Tubes','engimon')
        elif found_match and intent =='tampilTugas':
            return tampilTugas()
        elif found_match and intent == 'tampilDeadline':
            return tampilDeadline(matkul)
        elif found_match and intent == 'updateTanggal':
            return updateTanggal(28, "4/28/2021")
        elif found_match and intent == 'done':
            return done(25)
        elif found_match and intent == 'help':
            return tampilHelp()
    else:
        print("punten kang aing teu ngertos maneh ngomong naon")

arrayDB = bacaDB()

tampilTugasDayToDay(120)
print("-----------------")
tampilTugasDayToDay(120,90)
# tambahTugas('4/24/2021','OOP','Tubes','engimon')
# updateTanggal(26, "4/30/2021")
# done(25)
# tampilTugas()
# tampilHelp()
chat()

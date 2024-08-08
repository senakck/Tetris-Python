import sys
import math
import random
import threading

from enum import Enum

from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QComboBox, QLabel, QFileDialog, QMessageBox, \
    QLineEdit
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QSize, Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QCursor, QPixmap, QFont, QColor, QKeyEvent

blokBoyut = 40
kenarBoyut = 20
ustBosluk = 100
timer = QTimer()
Seviye = 1
Puan = 1000
periyod = 1000

class tasTip(Enum):
    I = 0
    Z = 1
    S = 2
    T = 3
    L = 4
    J = 5
    O = 6


class yonTip(Enum):
    Sola = 0
    Saga = 1
    Asagi = 2

class sesTip(Enum):
    sesTasYerlestir = 0
    sesSatirSil = 1
    sesOyunBitti = 2
    

class Blok():
    x = 0
    y = 0
    doluMu = False

    def __init__(self, x, y, doluMu):
        self.x = x
        self.y = y
        self.doluMu = doluMu

    @staticmethod
    def koorHesap(x, y):
        global kenarBoyut, blokBoyut
        return kenarBoyut + x * blokBoyut, kenarBoyut + y * blokBoyut

    def getKoord(self):
        return self.koorHesap(self.x, self.y)


class Tahta():  # Tetris oyununun oynanacağı tahta
    konum = [[Blok(i, j, False) for j in range(18)] for i in range(12)]

    def __init__(self):
        pass

    def reset(self): # Tahta konum daki bütün blokların doluMu özelliğini false yapar
        for j in range(18):
            for i in range(12):
                self.konum[i][j].doluMu = False
                
    def satirDoluMu(self, satir):  # Belirtilen satırdaki tüm bloklar dolu ise True, değilse False döndürür.
        for sutun in range(12):
            if self.konum[sutun][satir].doluMu == False:
                return False
        return True

    def satirTemizle(self, satir):  # Belirtilen satırdaki tüm blokların doluMu özelliğini False yapar
        for sutun in range(12):
            self.konum[sutun][satir].doluMu = False

    def satirSil(self, satir):  # Belirtilen satırın üzerindeki tüm satırların doluMu özelliğini aşağı taşır
        global Puan
        for s in range(satir, 0, -1):
            for sutun in range(12):
                bAlt=self.konum[sutun][s]
                bUst=self.konum[sutun][s-1]
                bAlt.doluMu=bUst.doluMu
        self.satirTemizle(0)
        Puan += 250
        


        
    def getSonDoluSatir(self):  # Tüm bloklar dolu olan en sondaki satirın numarasını döndürür.
        for satir in range(17, -1, -1):
            if self.satirDoluMu(satir) == True:
                return satir
        return -1

    def doluSatirlariSil(self):  # Alttan başlayarak tüm dolu satırları siler
        print("DOLU SATIR KONTROL")
        doluSatir = 0
        satirSilindi = False
        while doluSatir > -1:
            doluSatir = self.getSonDoluSatir()
            if doluSatir > -1:
                print("SATIR SİLİNECEK")
                self.satirSil(doluSatir)
                satirSilindi = True
        return satirSilindi

    def tasKontrol(self, tas):
        # Taş tahta içinde midir?
        for blok in tas.bloklar:
            if blok.x < 0 or blok.x > 11 or blok.y < 0 or blok.y > 17:
                return False
            if self.konum[blok.x][blok.y].doluMu == True:
                return False
        return True

    def tasDusurHesap(self, tas):  # Taşın ne kadar aşağı düşürülebileceğini hesap etsin
        h = 0
        t = tas
        for i in range(18):
            t = Tas.tasTasi(t, yonTip.Asagi)
            if self.tasKontrol(t) == False:
                return h

            h += 1
        return h

    def tasYerlestir(self, tas):
        global timer
        yerVar=True
        timer.stop()
        h = self.tasDusurHesap(tas)
        for b in tas.bloklar:
            k = self.konum[b.x][b.y + h]
            k.doluMu = True
            if k.y <=1 :
                yerVar=False

        return yerVar

class Tas():
    tip = None
    durum = 0
    bloklar = []

    def __init__(self, tip):
        self.tip = tip
        self.bloklar = []
        self.durum = 0

    def blokEkle(self, x0, y0, x1, y1, x2, y2, x3, y3):
        self.bloklar.append(Blok(x0, y0, True))
        self.bloklar.append(Blok(x1, y1, True))
        self.bloklar.append(Blok(x2, y2, True))
        self.bloklar.append(Blok(x3, y3, True))

    def kopyala(self):
        kopya = Tas(self.tip)
        kopya.durum = self.durum
        for blok in self.bloklar:
            kopya.bloklar.append(Blok(blok.x, blok.y, True))

        return kopya

    @staticmethod
    def tasTasi(tas, yon):
        yeni = tas.kopyala()
        for blok in yeni.bloklar:
            if yon == yonTip.Sola:
                blok.x -= 1
            elif yon == yonTip.Saga:
                blok.x += 1
            elif yon == yonTip.Asagi:
                blok.y += 1

        return yeni

    def tasi(self, yon):
        return Tas.tasTasi(self, yon)

    def dondur(self):
        return Tas.tasDondur(self)

    @staticmethod  # hiçbir nesneye özel değil = static
    def tasDondur(tas):  # Taşı saat yönünde 90 derece döndür.
        if tas.tip == tasTip.I:
            return Tas.tasDondurI(tas)
        elif tas.tip == tasTip.Z:
            return Tas.tasDondurZ(tas)
        elif tas.tip == tasTip.S:
            return Tas.tasDondurS(tas)
        elif tas.tip == tasTip.T:
            return Tas.tasDondurT(tas)
        elif tas.tip == tasTip.L:
            return Tas.tasDondurL(tas)
        elif tas.tip == tasTip.J:
            return Tas.tasDondurJ(tas)
        else:
            return tas.kopyala()

    @staticmethod
    def tasDondurI(tas):  # I tipi Taşı saat yönünde 90 derece döndür.
        yeni = tas.kopyala()
        if tas.durum == 0:
            # Dik durumdan Yataya çevir
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x + 1
            yeni.bloklar[2].y = tas.bloklar[2].y - 1

            yeni.bloklar[3].x = tas.bloklar[3].x + 2
            yeni.bloklar[3].y = tas.bloklar[3].y - 2
            yeni.durum = 1
        else:
            # Yatay durumdan Dike çevir
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x - 1
            yeni.bloklar[2].y = tas.bloklar[2].y + 1

            yeni.bloklar[3].x = tas.bloklar[3].x - 2
            yeni.bloklar[3].y = tas.bloklar[3].y + 2
            yeni.durum = 0

        return yeni

    @staticmethod
    def tasDondurZ(tas):  # Z tipi Taşı saat yönünde 90 derece döndür.
        yeni = tas.kopyala()
        if tas.durum == 0:
            # Yatay durumdan Dik duruma çevir
            yeni.bloklar[0].x = tas.bloklar[0].x + 2
            yeni.bloklar[0].y = tas.bloklar[0].y

            yeni.bloklar[1].x = tas.bloklar[1].x + 1
            yeni.bloklar[1].y = tas.bloklar[1].y + 1

            yeni.bloklar[2].x = tas.bloklar[2].x
            yeni.bloklar[2].y = tas.bloklar[2].y

            yeni.bloklar[3].x = tas.bloklar[3].x - 1
            yeni.bloklar[3].y = tas.bloklar[3].y + 1
            yeni.durum = 1

        else:
            # Dik durumdan Yatay duruma çevir
            yeni.bloklar[0].x = tas.bloklar[0].x - 2
            yeni.bloklar[0].y = tas.bloklar[0].y

            yeni.bloklar[1].x = tas.bloklar[1].x - 1
            yeni.bloklar[1].y = tas.bloklar[1].y - 1

            yeni.bloklar[2].x = tas.bloklar[2].x
            yeni.bloklar[2].y = tas.bloklar[2].y

            yeni.bloklar[3].x = tas.bloklar[3].x + 1
            yeni.bloklar[3].y = tas.bloklar[3].y - 1
            yeni.durum = 0

        return yeni

    @staticmethod
    def tasDondurS(tas):  # S tipi Taşı saat yönünde 90 derece döndür.
        yeni = tas.kopyala()
        if tas.durum == 0:
            # Yatay durumdan Dik duruma çevir
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y + 2

            yeni.bloklar[2].x = tas.bloklar[2].x + 1
            yeni.bloklar[2].y = tas.bloklar[2].y - 1

            yeni.bloklar[3].x = tas.bloklar[3].x
            yeni.bloklar[3].y = tas.bloklar[3].y
            yeni.durum = 1

        else:
            # Dik durumdan Yatay duruma çevir
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y - 2

            yeni.bloklar[2].x = tas.bloklar[2].x - 1
            yeni.bloklar[2].y = tas.bloklar[2].y + 1

            yeni.bloklar[3].x = tas.bloklar[3].x
            yeni.bloklar[3].y = tas.bloklar[3].y
            yeni.durum = 0

        return yeni

    @staticmethod
    def tasDondurT(tas):  # T tipi Taşı saat yönünde 90 derece döndür.
        yeni = tas.kopyala()
        if tas.durum == 0:
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x + 1
            yeni.bloklar[1].y = tas.bloklar[1].y - 1

            yeni.bloklar[2].x = tas.bloklar[2].x
            yeni.bloklar[2].y = tas.bloklar[2].y

            yeni.bloklar[3].x = tas.bloklar[3].x - 1
            yeni.bloklar[3].y = tas.bloklar[3].y + 1
            yeni.durum = 1

        elif tas.durum == 1:
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x - 1
            yeni.bloklar[1].y = tas.bloklar[1].y + 1

            yeni.bloklar[2].x = tas.bloklar[2].x
            yeni.bloklar[2].y = tas.bloklar[2].y

            yeni.bloklar[3].x = tas.bloklar[3].x + 1
            yeni.bloklar[3].y = tas.bloklar[3].y - 1
            yeni.durum = 2

        elif tas.durum == 2:
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x + 1
            yeni.bloklar[1].y = tas.bloklar[1].y + 1

            yeni.bloklar[2].x = tas.bloklar[2].x
            yeni.bloklar[2].y = tas.bloklar[2].y

            yeni.bloklar[3].x = tas.bloklar[3].x - 1
            yeni.bloklar[3].y = tas.bloklar[3].y - 1
            yeni.durum = 3

        else:
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x - 1
            yeni.bloklar[1].y = tas.bloklar[1].y - 1

            yeni.bloklar[2].x = tas.bloklar[2].x
            yeni.bloklar[2].y = tas.bloklar[2].y

            yeni.bloklar[3].x = tas.bloklar[3].x + 1
            yeni.bloklar[3].y = tas.bloklar[3].y + 1
            yeni.durum = 0

        return yeni

    @staticmethod
    def tasDondurL(tas):  # L tipi Taşı saat yönünde 90 derece döndür.
        yeni = tas.kopyala()
        if tas.durum == 0:
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x - 1
            yeni.bloklar[2].y = tas.bloklar[2].y - 1

            yeni.bloklar[3].x = tas.bloklar[3].x - 2
            yeni.bloklar[3].y = tas.bloklar[3].y
            yeni.durum = 1

        elif tas.durum == 1:
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x + 1
            yeni.bloklar[2].y = tas.bloklar[2].y - 1

            yeni.bloklar[3].x = tas.bloklar[3].x
            yeni.bloklar[3].y = tas.bloklar[3].y - 2
            yeni.durum = 2

        elif tas.durum == 2:
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x + 1
            yeni.bloklar[2].y = tas.bloklar[2].y + 1

            yeni.bloklar[3].x = tas.bloklar[3].x + 2
            yeni.bloklar[3].y = tas.bloklar[3].y
            yeni.durum = 3

        else:
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x - 1
            yeni.bloklar[2].y = tas.bloklar[2].y + 1

            yeni.bloklar[3].x = tas.bloklar[3].x
            yeni.bloklar[3].y = tas.bloklar[3].y + 2
            yeni.durum = 0
        return yeni

    @staticmethod
    def tasDondurJ(tas):  # J tipi Taşı saat yönünde 90 derece döndür.
        yeni = tas.kopyala()
        if tas.durum == 0:
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x - 1
            yeni.bloklar[2].y = tas.bloklar[2].y - 1

            yeni.bloklar[3].x = tas.bloklar[3].x
            yeni.bloklar[3].y = tas.bloklar[3].y - 2
            yeni.durum = 1

        elif tas.durum == 1:
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y + 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x + 1
            yeni.bloklar[2].y = tas.bloklar[2].y - 1

            yeni.bloklar[3].x = tas.bloklar[3].x + 2
            yeni.bloklar[3].y = tas.bloklar[3].y
            yeni.durum = 2

        elif tas.durum == 2:
            yeni.bloklar[0].x = tas.bloklar[0].x - 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x + 1
            yeni.bloklar[2].y = tas.bloklar[2].y + 1

            yeni.bloklar[3].x = tas.bloklar[3].x
            yeni.bloklar[3].y = tas.bloklar[3].y + 2
            yeni.durum = 3

        else:
            yeni.bloklar[0].x = tas.bloklar[0].x + 1
            yeni.bloklar[0].y = tas.bloklar[0].y - 1

            yeni.bloklar[1].x = tas.bloklar[1].x
            yeni.bloklar[1].y = tas.bloklar[1].y

            yeni.bloklar[2].x = tas.bloklar[2].x - 1
            yeni.bloklar[2].y = tas.bloklar[2].y + 1

            yeni.bloklar[3].x = tas.bloklar[3].x - 2
            yeni.bloklar[3].y = tas.bloklar[3].y
            yeni.durum = 0

        return yeni


# ANA PROGRAM

class MainWindow(QMainWindow):
    imgBlok = None
    imgBos = None

    taslar = []
    tahta = Tahta()
    secTas = None

    renkSiyah = Qt.black
    kalemSiyah = QPen(renkSiyah, 2)
    renkKahve = QColor(165, 42, 42)
    kalemKahve = QPen(renkKahve, 20)

    
    labSeviye = None
    labPuan = None
    
    player = QMediaPlayer()
 
    
    def __init__(self):
        global blokBoyut, kenarBoyut, ustBosluk, timer, Puan, Seviye

        QMainWindow.__init__(self)
        self.setFocusPolicy(Qt.StrongFocus)
        tahtaBoyutX = 12 * blokBoyut + 2 * kenarBoyut
        tahtaBoyutY = ustBosluk + 18 * blokBoyut + 2 * kenarBoyut

        self.setMinimumSize(QSize(tahtaBoyutX, tahtaBoyutY))

        fontBaslik = QFont('Calibri', 18, QFont.Bold)
        fontEtiket = QFont('Calibri', 12, QFont.Bold)

        labBaslik = QLabel("TETRİS OYUNU", self)
        labBaslik.resize(250, 36)
        labBaslik.move(kenarBoyut, 5)
        labBaslik.setFont(fontBaslik)

        lab1 = QLabel("Seviye", self)
        lab1.resize(60, 36)
        lab1.move(350, 12)
        lab1.setFont(fontEtiket)

        self.labSeviye = QLabel("1", self)
        self.labSeviye.resize(80, 30)
        self.labSeviye.move(420, 12)

        self.labSeviye.setStyleSheet("""
            QLabel {
                border: 2px solid black;  /* Çerçeve rengi ve kalınlığı */
                background-color: lightblue;  /* Zemin rengi */
                padding: 5px;  /* Metin ile çerçeve arasındaki boşluk */
                font-size: 16px;  /* Yazı tipi boyutu */
            }
        """)

        lab2 = QLabel("Puan", self)
        lab2.resize(60, 24)
        lab2.move(350, 50)
        lab2.setFont(fontEtiket)

        self.labPuan = QLabel("1000", self)
        self.labPuan.resize(80, 30)
        self.labPuan.move(420, 50)
        self.labPuan.setStyleSheet("""
            QLabel {
                border: 2px solid black;  /* Çerçeve rengi ve kalınlığı */
                background-color: lightblue;  /* Zemin rengi */
                padding: 5px;  /* Metin ile çerçeve arasındaki boşluk */
                font-size: 16px;  /* Yazı tipi boyutu */
            }
        """)
        
        self.paused = False
    

        btnBasla = QPushButton('RESET', self)
        btnBasla.clicked.connect(self.reset_click)
        btnBasla.resize(100, 35)
        btnBasla.move(kenarBoyut, 50)

        btnBasla = QPushButton('BAŞLA', self)
        btnBasla.clicked.connect(self.basla_click)
        btnBasla.resize(100, 35)
        btnBasla.move(kenarBoyut + 120, 50)

        self.imgBlok = QPixmap('Images/Blok.png')
        self.imgBos = QPixmap('Images/Bos.png')
        self.TasYukle()
        timer.timeout.connect(self.tasAsagi)
            
    def TasYukle(self):
        t0 = Tas(tasTip.I)
        t0.blokEkle(5, 1, 5, 2, 5, 3, 5, 4)
        self.taslar.append(t0)

        t1 = Tas(tasTip.Z)
        t1.blokEkle(4, 1, 5, 1, 5, 2, 6, 2)
        self.taslar.append(t1)

        t2 = Tas(tasTip.S)
        t2.blokEkle(5, 1, 6, 1, 4, 2, 5, 2)
        self.taslar.append(t2)

        t3 = Tas(tasTip.T)
        t3.blokEkle(5, 1, 4, 2, 5, 2, 6, 2)
        self.taslar.append(t3)

        t4 = Tas(tasTip.L)
        t4.blokEkle(5, 1, 5, 2, 5, 3, 6, 3)
        self.taslar.append(t4)

        t5 = Tas(tasTip.J)
        t5.blokEkle(5, 1, 5, 2, 5, 3, 4, 3)
        self.taslar.append(t5)

        t6 = Tas(tasTip.O)
        t6.blokEkle(4, 1, 5, 1, 4, 2, 5, 2)
        self.taslar.append(t6)

    def RastgeleTasGetir(self):
        sec = random.choice(self.taslar)
        return sec.kopyala()

    def sesDosyaYurut(self, tip):
        if (tip == sesTip.sesTasYerlestir):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile("Sounds/tas_yerlestir.wav")))
        elif (tip == sesTip.sesSatirSil):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile("Sounds/satir_silindi.wav")))
        elif (tip == sesTip.sesOyunBitti):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile("Sounds/oyun_bitti.wav")))
        
        self.player.play()   
       
    def reset_click(self):
        self.ResetGame()
    
    def seviyeDegistir(self):
        global Puan, Seviye, periyod
        if Puan >= Seviye * 2000:
            Seviye += 1       
        periyod = int(1000/Seviye)
        self.labSeviye.setText(str(Seviye))
        
        
    
    def puanDegistir(self, fark):
        global Puan
        Puan += fark
        self.labPuan.setText(str(Puan))
        
    def yeniTas(self):
        global timer
        self.secTas = self.RastgeleTasGetir()
        self.puanDegistir(-10)
        self.seviyeDegistir()
        timer.start(periyod)
    

    def basla_click(self):
        self.setFocus()
        self.yeniTas()

    def cizimBlok(self, painter, blok):  # tek blok çizim
        global kenarBoyut, blokBoyut, ustBosluk

        x1 = kenarBoyut + blok.x * blokBoyut
        y1 = ustBosluk + kenarBoyut + blok.y * blokBoyut
        if blok.doluMu:
            painter.drawPixmap(QRect(x1, y1, blokBoyut, blokBoyut), self.imgBlok)
        else:
            painter.drawPixmap(QRect(x1, y1, blokBoyut, blokBoyut), self.imgBos)

    def cizimTas(self, painter, tas):  # Taşın tüm bloklarını sıra ile çizer
        for blok in tas.bloklar:
            self.cizimBlok(painter, blok)

    def cizimTahta(self, painter, tahta):  # tek blok çizim
        global kenarBoyut, blokBoyut, ustBosluk
        w = kenarBoyut * 2 + blokBoyut * 12
        h = ustBosluk + kenarBoyut * 2 + blokBoyut * 18

        painter.setPen(self.kalemSiyah)
        painter.setBrush(self.renkKahve)
        painter.drawRect(0, ustBosluk, w, h)

        painter.setBrush(Qt.white)
        painter.drawRect(kenarBoyut, ustBosluk + kenarBoyut, blokBoyut * 12, blokBoyut * 18)

        for y in range(18):
            for x in range(12):
                blok = tahta.konum[x][y]
                self.cizimBlok(painter, blok)

    def cizim(self):
        painter = QPainter(self)
        self.cizimTahta(painter, self.tahta)
        if self.secTas != None:
            self.cizimTas(painter, self.secTas)
        painter.end()
        return True

    def tasAsagi(self):
        t = self.secTas.tasi(yonTip.Asagi)
        if self.tahta.tasKontrol(t) == True:
            self.secTas = t
        else:
            yerVar=self.tahta.tasYerlestir(self.secTas)
            self.sesDosyaYurut(sesTip.sesTasYerlestir)
            if yerVar == True:
                self.tahta.doluSatirlariSil()
                self.puanDegistir(0)
                self.seviyeDegistir()
                self.yeniTas()
            else:
                self.oyunBitir()
                return


    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        self.cizim()
        self.update()
 

    def pause_game(self):
        if self.paused:
            timer.start(periyod)
            print("DEVAM EDİYOR")
        else:
            timer.stop()  # Zamanlayıcıyı durdur
            self.paused = True  # Durum değişkenini durdurulmuş olarak ayarla
            print("DURDUR")
            

    def keyPressEvent(self, event: QKeyEvent):
        yeni = None
        if event.key() == Qt.Key_Up:
            print("DÖNDÜR")
            yeni = self.secTas.dondur()
        elif event.key() == Qt.Key_Left:
            print("SOLA")
            yeni = self.secTas.tasi(yonTip.Sola)
        elif event.key() == Qt.Key_Right:
            print("SAGA")
            yeni = self.secTas.tasi(yonTip.Saga)
        elif event.key() == Qt.Key_Down:
            print("DÜŞÜR")
            yerVar=self.tahta.tasYerlestir(self.secTas)
            self.sesDosyaYurut(sesTip.sesTasYerlestir)
            if yerVar == True:
                if self.tahta.doluSatirlariSil() == True:
                    self.sesDosyaYurut(sesTip.sesSatirSil)
                self.yeniTas()
            else:
                self.oyunBitir()
                return
        elif event.key() == Qt.Key_Space:
            self.pause_game()
 
        else:
            print("YOK")

        if yeni != None and self.tahta.tasKontrol(yeni):
            self.secTas = yeni
    
    
    def ResetGame(self):
        global timer, Puan, Seviye, periyod

        timer.stop()
        
        # Oyun değişkenlerini sıfırlama
        Puan = 1000
        Seviye = 1
        periyod = 1000/Seviye

        # Tahtayı sıfırlama
        self.tahta.reset()
        
        # Etiketleri güncelleme
        self.labPuan.setText(str(Puan))
        self.labSeviye.setText(str(Seviye))
        
        self.secTas = None
  
    def oyunBitir(self):
        global timer
        timer.stop()
        self.sesDosyaYurut(sesTip.sesOyunBitti)
        QMessageBox.information(self,"Oyun bitti","Oyun bitti kaybettin :( Tekrar dene! ")
       
        yanit = QMessageBox.question(self, "Oyun Bitti",
                                     "Tekrar oynamak ister misiniz?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if yanit == QMessageBox.Yes:
            self.ResetGame()
        else:
            QMessageBox.information(self,"Oyun bitti","Oynadiğiniz için teşekkür ederiz.")
            QApplication.quit()
            
            
            
            
   
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


# commiting again for github


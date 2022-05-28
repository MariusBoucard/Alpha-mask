#!/usr/bin/python
from email.mime import image
from tokenize import String
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow, QGraphicsScene,QGraphicsPixmapItem
from PyQt5.uic import loadUi
import subprocess
import platform
from PyQt5.QtCore import Qt, QSettings
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
import cv2
import tempfile
import csv


class MainWindow(QMainWindow):
    
    def __init__(self):
        self.settings = QSettings("AlphaMasker","BrubruThelord")
        super(MainWindow,self).__init__()
        self.pathui=resource_path("Main 2.ui")
        loadUi(self.pathui,self)
        self.image_qt=QImage()
        self.Charger.triggered.connect(self.loadimg)

        if self.settings.value("DropList") ==None :
            self.droplist = ['T-shirt','Jean','Corps','Tete','Chaussures']
            self.settings.setValue("DropList",self.droplist)
            self.settings.setValue(self.droplist[0],40)
            self.settings.setValue(self.droplist[1],80)
            self.settings.setValue(self.droplist[2],120)
            self.settings.setValue(self.droplist[3],160)
            self.settings.setValue(self.droplist[4],200)
        self.tmp = tempfile.gettempdir()
        self.droplist = self.settings.value("DropList")



        self.ExpConstantes.triggered.connect(self.export_CVS)
        self.Add.clicked.connect(self.add)
        self.Remove.clicked.connect(self.remove)
        self.DropDown.addItems(self.droplist)
        
    def export_CVS(self):
        filename = QFileDialog.getSaveFileName(self, 'Sauvegarder les nuances de gris', '', "All Files (*);; Fichier csv (*.csv);;Fichier txt (*.txt)", options=QFileDialog.DontUseNativeDialog)
        
        if filename[0] == '':
            return 0

        filename = filename[0]
        with open(filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Partie du corps","Nuance de gris associée"])
            for part in self.droplist :
                i=int(self.settings.value(part))
                a = [part,i]
                writer.writerow(a)
        
        
        f.close()
        print('file saved')

    def loadimg(self):
    
        fname=QFileDialog.getOpenFileName(self, 'Ouvrir une image sortie de caracter creator', './',"*.*")
        self.imgPath = fname[0]
        self.PathLabel.setText(self.imgPath)
        self.InfectButton.setEnabled(True)

        if not self.imgPath:
            return

        self.image_qt = QImage(self.imgPath)

        self.pixmap = QPixmap.fromImage(self.image_qt)
        w = self.ImageView.width()
        h=self.ImageView.height()
        self.ImageView.setPixmap(self.pixmap.scaled(w,h,Qt.KeepAspectRatio)) 

        self.ImageView.mousePressEvent = self.getPixel

        # Permet de a peut pret calibrer la fenetre mais c est cheum
        imh =self.image_qt.height()
        imw = self.image_qt.width()
        ivh = self.ImageView.height()
        ivw = self.ImageView.width()
        w = ivw /imw
        h=ivh / imh

        
        self.InfectButton.clicked.connect(self.inf)
        self.Sauvegarder.triggered.connect(self.dialog_save)
    
    def add(self) :
        # attetnion add a verif si deja present
        partie = self.PartieCorps.text()
        value = int(self.GreyValue.text())
        self.droplist.append(partie)

        self.settings.setValue("DropList",self.droplist)
        self.settings.setValue(partie,value)
        self.DropDown.clear()
        self.DropDown.addItems(self.droplist)
        self.Etape.setText("La partie du corps "+partie+" a été ajoutée, avec la valeur de gris : "+str(value))

    def remove(self) :
        partie = self.PartieCorps.text()
        try :
            self.droplist.remove(partie)
        except :
            self.Etape.setText("Cette partie du corps n'existait vraisemblablement pas")
            return
        
        self.settings.setValue("DropList",self.droplist)
        self.settings.remove(partie)
        self.DropDown.clear()
        self.DropDown.addItems(self.droplist)
        self.Etape.setText("La partie du corps "+partie+" a été supprimée")

    def getPixel(self, event):
        x = event.pos().x()
        y = event.pos().y()

        print("getPixel : "+str(x)+" "+str(y))

        self.colorierZone(x,y)
    
    def colorierZone(self,x,y) :
        self.image_qt.save(self.tmp+"colorzone.jpg","PNG",100)
        image= cv2.imread(self.tmp+"colorzone.jpg")
        part = self.DropDown.currentText()
        print(part)
        print(len(self.contours))
        
        # Remise à l'echelle du pixel recupere par rapport a la taille du Label et de l image

        h, w, _ = image.shape

        hi=self.ImageView.height()
        wi=self.ImageView.width()


        factx = h/hi
        facty =w/wi

        x=x*factx
        y=y*facty

        for cnt in self.contours :
            dist = cv2.pointPolygonTest(cnt,(x,y),False)
            if dist > 0 :
        # ajouter un choix en fct du dropdown

                i=int(self.settings.value(part))
                print(i)
                cv2.fillPoly(image, [cnt], color=(i,i,i))
        
        cv2.imwrite(self.tmp+"image.jpg", image)
        self.image_qt = QImage(self.tmp+"image.jpg")
        self.pixmap = QPixmap.fromImage(self.image_qt)
        w = self.ImageView.width()
        h=self.ImageView.height()
        self.ImageView.setPixmap(self.pixmap.scaled(w,h,Qt.KeepAspectRatio)) 

    #Suppression des fichiers temporaires commes on peut pas aller facilement dans temp dans windaubex 

    def inf(self) :
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(0)
        image = cv2.imread(self.imgPath)
        self.progressBar.setValue(10)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.progressBar.setValue(20)
        self.contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, self.contours, -1, (0, 255, 0), 1)
        self.progressBar.setValue(50)
        cv2.fillPoly(image, self.contours, color=(255,255,255))
        self.progressBar.setValue(70)
        cv2.imwrite(self.tmp+"image.jpg", image)
        self.progressBar.setValue(80)
        self.image_qt = QImage(self.tmp+"image.jpg")
        self.progressBar.setValue(90)
        self.pixmap = QPixmap.fromImage(self.image_qt)
        w = self.ImageView.width()
        h=self.ImageView.height()
        self.ImageView.setPixmap(self.pixmap.scaled(w,h,Qt.KeepAspectRatio)) 
        self.progressBar.setValue(100)


    def dialog_save(self):
    
        filename = QFileDialog.getSaveFileName(self, 'Sauvegarder l\'alpha mâle', '', "All Files (*);; Fichier png (*.png);;Fichier jpg (*.jpg)", options=QFileDialog.DontUseNativeDialog)
        
        if filename[0] == '':
            return 0

        filename = filename[0]
        print(filename[1])
        ret = self.image_qt.save(filename,format="PNG",quality=100)
        print(ret)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':

    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    
    widget.show()
    sys.exit(app.exec_())
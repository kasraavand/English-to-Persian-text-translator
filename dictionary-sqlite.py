#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3 as lite
import sys,codecs
from PySide import QtGui
from PySide import QtCore
from PySide.QtGui import QFrame, QPalette
from PySide.QtGui import QTableWidget, QTableWidgetItem, QColor, QPixmap
import re
#import itertools
from nltk.stem import LancasterStemmer,PorterStemmer,RegexpStemmer,WordNetLemmatizer
from nltk.tokenize import sent_tokenize,word_tokenize
#from itertools import groupby ,chain
from nltk.tag import pos_tag
from nltk.corpus import wordnet

dic1={}

#import data from database

con = lite.connect('Generic_English_Persian.m2')
with con:    
    cur = con.cursor()    
    cur.execute("SELECT * FROM word")
    rows = cur.fetchall()
    for row in rows:
         un_paretthesis=re.sub(r'\(.*\)','',row[2],flags=re.UNICODE)
         dic1[row[1]]=filter(bool,re.split(u'،',un_paretthesis,flags=re.UNICODE))

#print dic1['apple']
stemmer=LancasterStemmer()
lemmatizer=WordNetLemmatizer()
#classes and other objects 



class InputDialog(QtGui.QMainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)
    self.menu = self.menuBar().addMenu(self.tr('View'))
    self.action = self.menu.addAction(self.tr('New Window'))
    self.action.triggered.connect(self.handleNewWindow)
    self.menu.sizeHint()
    self.lbl3 = QtGui.QLabel('Enter yor text here !', self)
    self.lbl3.setGeometry(600,83,600,80)
    self.setGeometry(150,150,1000,600)
    self.setWindowTitle('PERSDIC')
    #self.button=HoverButton(self)
    self.button = QtGui.QPushButton('Translate',self)
    self.button.setIconSize(QtCore.QSize(183,30))
    #self.button.setFocusPolicy(QtCore.Qt.NoFocus)
    self.button.move(135,80)
    self.connect(self.button, QtCore.SIGNAL('clicked()'), self.insert)
    self.button2 = QtGui.QPushButton('All Possibilities',self)
    self.button2.setIconSize(QtCore.QSize(183,30))
    #self.button.setFocusPolicy(QtCore.Qt.NoFocus)
    self.button2.move(645,560)
    #self.connect(self.button, QtCore.SIGNAL('clicked()'), self.insert)

    self.button1= QtGui.QPushButton('Update Translete', self)
    self.button1.move(10,560)
    self.connect(self.button1, QtCore.SIGNAL('clicked()'), self.update)
    self.setFocus()
    #self.icon1 = QtGui.QIcon()
    #self.icon1.addPixmap(QtGui.QPixmap('unnamed.png'))
    #self.label = QtGui.QLineEdit(self)
    #self.label.setGeometry(130,40,260,30)
    self.image = QtGui.QLabel(self)
    self.image.setPixmap(QtGui.QPixmap('png1.png'))
    self.image.setGeometry(440,20,128,128)
    self.mess=QtGui.QMessageBox(self)
    #self.errorMessageDialog = QtGui.QErrorMessage(self)
    self.dialogbox=QtGui.QInputDialog()
    #self.dialogbox.setGeometry(200,200,200,200)
    self.label6 = QtGui.QTextEdit(self)
    self.label6.setGeometry(530,150,430,400)  
    self.lbl5 = QtGui.QTextEdit(self)
    self.lbl5.setReadOnly(True)
    self.lbl5.setGeometry(30,150,430,400)
    self.setStyleSheet("QWidget {border-radius:4px;color :black;font-weight:500; font-size: 12pt}QPushButton{color:#099000;border-style: outset;border-width: 2px;border-radius: 10px;border-color: beige;font: bold 14px;min-width: 10em;padding: 6px;}QLineEdit{background-color:white; color:black}QTextEdit{background-color:#ffffff; color:#000000}")

    #bottom = QtGui.QFrame(self)
    #bottom.setFrameShape(QtGui.QFrame.StyledPanel)
    #bottom.setGeometry(30,150,430,400)
    with open('Words.txt','a+') as f:
       b= sum(1 for _ in f)
       self.lbl4 = QtGui.QLabel('[{}] word exist in your dictionary...!'.format(str(b)),self)
       self.lbl4.setGeometry(100,90,600,82)
       f.close()

  def insert(self):

      inword=self.label6.toPlainText().lower()
      #inword=stemmer.stem(inword)
      f=open('Words.txt','a+')
      if inword+'\n' in f.readlines():
         self.mess.information(self,"Word exist in personal words !",' '.join(dic1[inword.encode('unicode-escape')]))
         #self.label.clear()
      elif inword in dic1.keys():
          self.lbl5.clear()
          if isinstance(dic1[inword],list):
            self.lbl5.append('\n'.join(dic1[inword]))
          else :
            self.lbl5.append(dic1[inword])

          f.write(inword)
          f.write('\n')

      elif len(inword.split()) > 1:
        self.sentence_translator(inword)

      else :
        text,ok=self.dialogbox.getText(QtGui.QInputDialog(),'Create Persian meaning','Enter meaning here: ',QtGui.QLineEdit.Normal,'meaning')
        if ok :  
         dic1[str(inword)]=text
         #print text.encode('utf-8')
         self.update(text,inword,flag=True)
         f.write(inword)
         f.write('\n')

  def update(self,text='',flag=False):

    inword=self.label6.toPlainText().lower()
    words=inword.split()
    con = lite.connect('Generic_English_Persian.m2')
    if len(words)>1:
      for w in words :
          text,ok=self.dialogbox.getText(QtGui.QInputDialog(),'Update meaning of {}'.format(w),'Enter meaning here: ',QtGui.QLineEdit.Normal,'{}'.format('|'.join(dic1[w]).encode('utf-8')))
          if ok :
            dic1[str(inword)]=text
            with con:
             cur = con.cursor()  
             cur.execute("SELECT * FROM word")
             cur.execute("UPDATE word SET Wmean=? WHERE Wname=?",[text+' '+' '.join(dic1[w]), str(w)])       
             con.commit()
    elif not flag:
          text,ok=self.dialogbox.getText(QtGui.QInputDialog(),'Update meaning of {}'.format(words[0]),'',QtGui.QLineEdit.Normal,'')
          if ok :
            dic1[str(inword)]=text
            with con:
             cur = con.cursor()  
             cur.execute("SELECT * FROM word")
             cur.execute("UPDATE word SET Wmean=? WHERE Wname=?",[text+' '+' '.join(dic1[words[0]]), str(words[0])])       
             con.commit()
    else:
            print 'aaaaaaa'
            with con:
                cur = con.cursor()  
                cur.execute("SELECT * FROM word")
                rows = cur.fetchall()
                i=len(rows)+1
                cur.execute("insert into word (s_id,Wname,Wmean) values (?, ?, ?)",(i,inword,unicode(text)))        

   

  def keyPressEvent(self, e):
          if e.key() == QtCore.Qt.Key_Escape:
              self.insert()


  def sentence_translator (self,sentence) :
    sentence=' '.join(self.text_refiner(sentence))
    #sentences=sent_tokenize(sentence)
    l=re.split(r',|\.',sentence)
    T= [pos_tag(word_tokenize(i)) for i in l]
    #print T

    for j in T :
        for i,t in enumerate(j):
          if 'V' in t[1]:
            j.append(j.pop(i))
    
    word_list=[zip(*i)[0] for i in T if i]
    all_trans=[dic1[j][0] if j in dic1 else j for i in word_list for j in self.word_refiner(*i)]


    self.lbl5.clear()
    self.lbl5.append(' '.join(all_trans))

  def word_refiner(*args):
    Portst = PorterStemmer()
    Landst=LancasterStemmer()
    Regst=RegexpStemmer('ing|ed|ly|lly')
    args=[i for i in args if isinstance(i,unicode)]

    for w in map(str,args):
      
      if w in dic1:
        yield w

      else:
       st1=Portst.stem(w)
       if st1 in dic1:
        yield st1

       else:
         st2=Landst.stem(w)
         if st2 in dic1:
          yield st2

         else :
           st3=Regst.stem(w)
           if st3 in dic1:
            yield st3
           else:
            yield w
  
  def  text_refiner(self,s):
      flag=True
      patterns = [
(r'won\'t', 'will not'),
(r'can\'t', 'cannot'),
(r'i\'m', 'i am'),
(r'ain\'t', 'is not'),
(r'(\w+)\'ll', '\g<1> will'),
(r'(\w+)n\'t', '\g<1> not'),
(r'(\w+)\'ve', '\g<1> have'),
(r'(\w+)\'s', '\g<1> is'),
(r'(\w+)\'re', '\g<1> are'),
(r'(\w+)\'d', '\g<1> would')
]


      patterns = [(re.compile(regex), repl) for (regex, repl) in patterns]
      for (pattern, repl) in patterns:
        (s, count) = re.subn(pattern, repl, s)

      def replacer(word):
          repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
          repl = r'\1\2\3'
          if wordnet.synsets(word):
            return word
          repl_word = repeat_regexp.sub(repl, word)
          if repl_word != word:
            return replacer(repl_word)
          else:
            return repl_word

      for w in s.split():
          yield replacer(w)




  def handleNewWindow(self):
        window = QtGui.QMainWindow(self)
        window.setWindowTitle(self.tr('New Window'))
        window.setGeometry(150,150,1000,600)
        window.lbl5 = QtGui.QTextEdit(self)
        window.lbl5.setGeometry(30,150,430,400)
        window.setStyleSheet("QWidget {border-radius:4px;color :black;font-weight:500; font-size: 12pt}QPushButton{color:#099000;border-style: outset;border-width: 2px;border-radius: 10px;border-color: beige;font: bold 14px;min-width: 10em;padding: 6px;}QLineEdit{background-color:white; color:black}QTextEdit{background-color:#ffffff; color:#000000}")
        window.show()


app = QtGui.QApplication(sys.argv)
icon = InputDialog()
icon.show()
app.exec_()

# End of script


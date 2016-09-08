#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3 as lite
import sys
from PySide import QtGui
from PySide import QtCore
import re
from nltk.stem import LancasterStemmer, PorterStemmer, RegexpStemmer
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet
from string import punctuation

dic1 = {}

# import data from database

con = lite.connect('Generic_English_Persian.m2')
with con:
    cur = con.cursor()
    cur.execute("SELECT * FROM word")
    rows = cur.fetchall()
    for row in rows:
        un_paretthesis = re.sub(r'\(.*\)', '', row[2], flags=re.UNICODE)
        dic1[row[1]] = filter(bool, re.split(ur'[،,]', un_paretthesis, flags=re.UNICODE))


class InputDialog(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.lbl3 = QtGui.QLabel('Enter yor text here !', self)
        self.lbl3.setGeometry(600, 83, 600, 80)
        self.setGeometry(150, 150, 1000, 600)
        self.setWindowTitle('PERSDIC')
        self.button = QtGui.QPushButton('Translate', self)
        self.button.setIconSize(QtCore.QSize(183, 30))
        self.button.move(135, 80)
        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.insert)
        self.button2 = QtGui.QPushButton('All Possibilities', self)
        self.button2.setIconSize(QtCore.QSize(183, 30))
        self.button2.move(645, 560)

        self.button1 = QtGui.QPushButton('Update Translete', self)
        self.button1.move(10, 560)
        self.connect(self.button1, QtCore.SIGNAL('clicked()'), self.update)
        self.setFocus()
        self.image = QtGui.QLabel(self)
        self.image.setPixmap(QtGui.QPixmap('png1.png'))
        self.image.setGeometry(440, 20, 128, 128)
        self.mess = QtGui.QMessageBox(self)
        self.dialogbox = QtGui.QInputDialog()
        self.label6 = QtGui.QTextEdit(self)
        self.label6.setGeometry(530, 150, 430, 400)
        self.lbl5 = QtGui.QTextEdit(self)
        self.lbl5.setReadOnly(True)
        self.lbl5.setGeometry(30, 150, 430, 400)
        self.setStyleSheet("""QWidget {border-radius:4px;color :black;font-weight:500;
        font-size: 12pt}QPushButton{color:#099000;border-style: outset;
        border-width: 2px;border-radius: 10px;border-color: beige;font: bold 14px;
        min-width: 10em;padding: 6px;}QLineEdit{background-color:white; color:black}
        QTextEdit{background-color:#ffffff; color:#000000}""")


    def insert(self):
        inword = self.label6.toPlainText().lower()
        if inword in dic1.keys():
            self.lbl5.clear()
            if isinstance(dic1[inword], list):
                self.lbl5.append('\n'.join(map(lambda x: x.strip(punctuation), dic1[inword])))
            else:
                self.lbl5.append(dic1[inword])

        elif len(inword.split()) > 1:
            self.sentence_translator(inword)

        else:
            self.update(flag=True)

    def update(self, flag=False):
        inword = self.label6.toPlainText().lower()
        words = inword.split()
        con = lite.connect('Generic_English_Persian.m2')
        if len(words) > 1:
            for w in words:
                try:
                    text, ok = self.dialogbox.getText(QtGui.QInputDialog(),
                                                      'Update meaning of {}'.format(w),
                                                      'Enter meaning here: ',
                                                      QtGui.QLineEdit.Normal,
                                                      ','.join(dic1[w]))
                    if ok:
                        dic1[str(inword)] = text
                        with con:
                            cur = con.cursor()
                            cur.execute("SELECT * FROM word")
                            cur.execute("UPDATE word SET Wmean=? WHERE Wname=?",[text, str(w)])
                            con.commit()
                except KeyError:
                    self.createor(w)
        elif not flag:
            text, ok = self.dialogbox.getText(QtGui.QInputDialog(),
                                              'Update meaning of {}'.format(words[0]),
                                              '',
                                              QtGui.QLineEdit.Normal,
                                              ','.join(dic1[words[0]]))
            if ok:
                dic1[str(inword)] = text
                with con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM word")
                    cur.execute("UPDATE word SET Wmean=? WHERE Wname=?", [text, str(inword)])
                    con.commit()
        else:
            self.createor(inword)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.insert()

    def createor(self, inword):
        text, ok = self.dialogbox.getText(QtGui.QInputDialog(),
                                          'Update meaning of {}'.format(inword),
                                          '',
                                          QtGui.QLineEdit.Normal,
                                          '')
        if ok:
            dic1[str(inword)] = text
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM word")
                rows = cur.fetchall()
                i = len(rows) + 1
                cur.execute("insert into word (s_id,Wname,Wmean) values (?, ?, ?)",
                            (i, inword, unicode(text)))

    def sentence_translator(self, sentence):
        sentence = ' '.join(self.text_refiner(sentence))
        l = re.split(r',|\.', sentence)
        T = [pos_tag(map(lambda x: x.strip('?!'), word_tokenize(i))) for i in l]
        for j in T:
            for i, t in enumerate(j):
                if 'V' in t[1]:
                    j.append(j.pop(i))

        word_list = [zip(*i)[0] for i in T if i]
        all_trans = [dic1[j][0].strip(punctuation) if j in dic1 else j for i in word_list for j in self.word_refiner(*i)]

        self.lbl5.clear()
        if '?' in sentence:
            self.lbl5.append(' '.join(all_trans) + '?')
        elif '!':
            self.lbl5.append(' '.join(all_trans) + '!')

    def word_refiner(*args):
        Portst = PorterStemmer()
        Landst = LancasterStemmer()
        Regst = RegexpStemmer('ing|ed|ly|lly')
        args = [i for i in args if isinstance(i, unicode)]

        for w in map(str, args):
            if w in dic1:
                yield w
            else:
                st1 = Portst.stem(w)
                if st1 in dic1:
                    yield st1
                else:
                    st2 = Landst.stem(w)
                    if st2 in dic1:
                        yield st2
                    else:
                        st3 = Regst.stem(w)
                        if st3 in dic1:
                            yield st3
                        else:
                            yield w

    def text_refiner(self, s):
        flag = True
        patterns = [(r'won\'t', 'will not'),
                    (r'can\'t', 'cannot'),
                    (r'i\'m', 'i am'),
                    (r'ain\'t', 'is not'),
                    (r'(\w+)\'ll', '\g<1> will'),
                    (r'(\w+)n\'t', '\g<1> not'),
                    (r'(\w+)\'ve', '\g<1> have'),
                    (r'(\w+)\'s', '\g<1> is'),
                    (r'(\w+)\'re', '\g<1> are'),
                    (r'(\w+)\'d', '\g<1> would')]

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

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = InputDialog()
    icon.show()
    app.exec_()

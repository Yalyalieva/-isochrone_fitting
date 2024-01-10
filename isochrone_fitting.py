# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 14:23:08 2017

@author: Sony
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import pandas as pd
from scipy import interpolate
import math
import re

class CanvasIsoch(FigureCanvas):
    def __init__(self, parent):
        self.N=15
        self.Color_name='Color'
        self.M_name='Filter'
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(121)
        self.ax1.set_xlabel('radius')
        self.ax1.set_ylabel('density')
        self.ax2 = self.fig.add_subplot(122)
        self.ax2.set_xlabel(self.Color_name)
        self.ax2.set_ylabel(self.M_name)
        self.ax2.invert_yaxis()
        self.fig.subplots_adjust(left=0.08)
        self.fig.subplots_adjust(bottom=0.08)
        self.fig.subplots_adjust(top=0.94)
        self.fig.subplots_adjust(right=0.95)
        self.fig.subplots_adjust(wspace=0.22)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
                      
    def UpdatePlot(self,M,Color):
        try:
            self.line1[0].remove()
        except (AttributeError,ValueError):
            pass
        finally:
            self.line1=self.ax2.plot(Color,M,'b')
            self.fig.canvas.draw()
            
    def InvertY(self):
        try: 
            self.ax2.invert_yaxis()
            self.fig.canvas.draw()
        except AttributeError:
            pass
            
    def UpdateDensPlot(self,r,flag,flag_r):
        idx = pd.IndexSlice
        flag=flag.fillna(False)
        try:
            self.densAll[0].remove()
        except (AttributeError,ValueError):
            pass
        finally:
            try:
                self.densClust[0].remove()
            except (AttributeError,ValueError):
                pass
            finally:
                R=max(r)
                S=[]
                r_list=[R/self.N*i for i in range(0,self.N+1)]
                r_median=[R/self.N*(i+0.5) for i in range(0,self.N)]
                for i in range(0,self.N):
                    S.append(math.pi*(r_list[i+1]**2-r_list[i]**2))    
                Dens=[]
                AllDens=[]
                NumStarSum=0
                AllNumStarSum=0
                NumStar=0
                AllNumStar=0
                for i in range(0,self.N):
                    NumStarSum=NumStarSum+NumStar
                    AllNumStarSum=AllNumStarSum+AllNumStar
                    try:
                        NumStar=((r.loc[idx[flag]] < R/self.N*(i+1)).value_counts()).loc[True] - NumStarSum
                    except:
                        NumStar=0
                    AllNumStar=((r.loc[idx[(-flag) & flag_r]] < R/self.N*(i+1)).value_counts()).loc[True] - AllNumStarSum
                    Dens.append(NumStar/S[i])
                    AllDens.append(AllNumStar/S[i])
                self.densClust=self.ax1.plot(r_median,Dens,'go')
                self.densAll=self.ax1.plot(r_median,AllDens,'bo',mfc='none',mec='b')
                self.densClust[0].set_label('Close to isochrone')
                self.densAll[0].set_label('Far from isochrone')
                self.ax1.legend()
                self.fig.canvas.draw()
        
    def UpdateDataPlot(self,Data_M,Data_Color,flag):
        try:
            self.line2[0].remove()
        except (AttributeError,ValueError):
            if flag:
                M1=max(Data_M)+0.2
                M2=min(Data_M)-0.2
            else:
                M1=min(Data_M)-0.2
                M2=max(Data_M)+0.2     
            self.ax2.axis([min(Data_Color)-0.2,max(Data_Color)+0.2,M1,M2])
        finally:
            self.line2=self.ax2.plot(Data_Color,Data_M,'k.')
            self.fig.canvas.draw()
            
            
        
class MyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MyWidget,self).__init__(parent)
        self.M='Filter'
        self.Color='Color'
        
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        
        self.font1=QtGui.QFont() 
        self.font1.setPixelSize(16) 
        
        self.font2=QtGui.QFont() 
        self.font2.setPixelSize(13)
        
        self.LabelThIs=QtWidgets.QLabel(self);
        self.LabelThIs.setFont(self.font1)
        self.LabelThIs.setText(u'Теоретические изохроны')
        
        self.LoadIsBut=QtWidgets.QPushButton(self);
        self.LoadIsBut.setText(u'Загрузить\nвыбранные изохроны');
        
        self.SetBut=QtWidgets.QPushButton(self);
        self.SetBut.setText(u'Загрузить новые\nтеоретические изохроны')      
        
        self.LabelMetal=QtWidgets.QLabel(self);
        self.LabelMetal.setFont(self.font1)
        self.LabelMetal.setText(u'Металличность')        
        
        self.ComboThIs = QtWidgets.QComboBox(self)        
        self.UpdateComboThIs()
        
        self.ComboMetal = QtWidgets.QComboBox(self)
        self.ComboMetalSet('')
        
        self.LabelData=QtWidgets.QLabel(self)
        self.LabelData.setFont(self.font1)
        self.LabelData.setText(u'Данные')
        
        self.ClearBut=QtWidgets.QPushButton(self)
        self.ClearBut.setText(u'Очистить\nграфик')
        
        self.LoadDataBut=QtWidgets.QPushButton(self)
        self.LoadDataBut.setText(u'Загрузить\nданные')   
        
        self.LabelDataName=QtWidgets.QLabel(self)
        self.LabelDataName.setText('')
        self.LabelDataName.setFont(self.font2)
        self.LabelDataName.setEnabled(False)
        
        self.LabelMaxR=QtWidgets.QLabel(self)
        self.LabelMaxR.setText(u'Радиус области')
        self.LabelMaxR.setFont(self.font2)
        
        self.edMaxR=QtWidgets.QLineEdit(self)
        
        self.LabelMaxM=QtWidgets.QLabel(self)
        self.LabelMaxM.setText(u'Ограничение по звездной величине\nдля построения графика плотности')
        self.LabelMaxM.setFont(self.font2)
        
        self.edMaxM=QtWidgets.QLineEdit(self)
        
        self.cbInvertY=QtWidgets.QCheckBox(self)
        self.cbInvertY.setChecked(True)
        self.cbInvertY.setText(u'Инвертировать ось Y')
                
        self.LabelParam=QtWidgets.QLabel(self)
        self.LabelParam.setText(u'Параметры')
        self.LabelParam.setFont(self.font1)
        
        self.Labellogt=QtWidgets.QLabel(self)
        self.Labellogt.setText('log t')
        self.Labellogt.setFont(self.font2)
        
        self.Combologt = QtWidgets.QComboBox(self)
        self.Combologt.setEnabled(False)
        
        self.LabelMm=QtWidgets.QLabel(self)
        self.LabelMm.setText('Видимый модуль\nрасстояния')
        self.LabelMm.setFont(self.font2)
        
        self.edMm = QtWidgets.QLineEdit(self)
        
        self.LabelColorEx=QtWidgets.QLabel(self)
        self.LabelColorEx.setText('Избыток цвета')
        self.LabelColorEx.setFont(self.font2)
        
        self.edColorEx = QtWidgets.QLineEdit(self)
        
        self.LabelhColorEx=QtWidgets.QLabel(self)
        self.LabelhColorEx.setText(u'Шаг')
        self.LabelhColorEx.setFont(self.font2)
        
        self.edhColorEx = QtWidgets.QLineEdit(self)
        
        self.LabelhMm=QtWidgets.QLabel(self)
        self.LabelhMm.setText(u'Шаг')
        self.LabelhMm.setFont(self.font2)
        
        self.edhMm = QtWidgets.QLineEdit(self)
        
        grid=QtWidgets.QGridLayout() 
        grid.setSpacing(30)
        grid.addWidget(self.LabelThIs, 0, 0)
        grid.addWidget(self.LabelMetal, 0,1)
        grid.addWidget(self.ComboThIs, 1,0)
        grid.addWidget(self.ComboMetal, 1,1)
        grid.addWidget(self.LoadIsBut,2,0)
        grid.addWidget(self.SetBut, 2,1)
        vbox = QtWidgets.QVBoxLayout() 
        vbox.addStretch()
        grid.addLayout(vbox,3,0)
        grid.addWidget(self.LabelData, 4,0)
        grid.addWidget(self.LabelDataName, 4,1)
        grid.addWidget(self.LoadDataBut, 5,0)
        grid.addWidget(self.ClearBut, 5,1)
        grid.addWidget(self.LabelMaxR,6,0)
        grid.addWidget(self.edMaxR,6,1)
        grid.addWidget(self.LabelMaxM,7,0)
        grid.addWidget(self.edMaxM,7,1)
        grid.addWidget(self.cbInvertY,8,0)
        vbox2 = QtWidgets.QVBoxLayout() 
        vbox2.addStretch()
        grid.addLayout(vbox2,9,0)
        grid.addWidget(self.LabelParam,10,0)
        gridpar=QtWidgets.QGridLayout() 
        gridpar.addWidget(self.Labellogt,0,0)
        gridpar.addWidget(self.Combologt,0,1)
        gridpar.addWidget(self.LabelMm,1,0)
        gridpar.addWidget(self.edMm,1,1)
        gridpar.addWidget(self.LabelhMm,1,2)
        gridpar.addWidget(self.edhMm,1,3)
        gridpar.addWidget(self.LabelColorEx,2,0)
        gridpar.addWidget(self.edColorEx,2,1)
        gridpar.addWidget(self.LabelhColorEx,2,2)
        gridpar.addWidget(self.edhColorEx,2,3)
        grid.addLayout(gridpar,11,0,2,3)
        self.setLayout(grid)   
        
        self.LoadDialog = FigDialog(None)
        self.ComboThIs.currentIndexChanged[str].connect(self.ComboMetalSet)
        self.SetBut.clicked.connect(self.SetIsoch)
        self.LoadDialog.ExitBut.clicked.connect(self.UpdateComboThIs)
                     
    def ComboMetalSet(self,name):
        self.ComboMetal.clear()
        if name!='' and name!='M_Color_System':
            self.ComboMetal.clear()
            self.isochname=name
            name=name.split(' ')
            M=name[0]
            Color=name[1]
            System=name[2]
            for i in range(len(self.TheorIsoch)):
                if self.TheorIsoch['M'][i]==M and self.TheorIsoch['Color'][i]==Color and self.TheorIsoch['System'][i]==System:
                    self.ComboMetal.addItem(str(self.TheorIsoch['Metal'][i]))
            self.ComboMetal.setEnabled(True)
        else:
            self.ComboMetal.addItem(u'Металличность')
            self.ComboMetal.setCurrentIndex(0)
            self.ComboMetal.setEnabled(False)
        
    def SetIsoch(self):
        self.LoadDialog.show()
        
    def UpdateComboThIs(self):
        self.ComboThIs.clear()
        self.ComboThIs.addItem('M_Color_System')
        self.ComboThIs.setCurrentIndex(0)
        self.ComboThIs.model().item(0).setEnabled(False)
        self.TheorIsoch=pd.read_csv('isochrones/TheorIsochList.dat',sep=' ',dtype={'Metal':str})
        self.TheorIsochName=set()        
        for i in range(len(self.TheorIsoch)):
            self.TheorIsochName.add(self.TheorIsoch['M'][i]+' '+self.TheorIsoch['Color'][i]+' '+self.TheorIsoch['System'][i])
        ListTheorIsochName=list(self.TheorIsochName)
        ListTheorIsochName.sort()
        self.ComboThIs.addItems(ListTheorIsochName)
        
    def paintEvent(self, event):
        self.qp = QtGui.QPainter()
        self.qp.begin(self)
        pen = QtGui.QPen(QtGui.QColor(180,20,100),2)
        self.qp.setPen(pen)
        r=self.rect().adjusted(5,5,-5,-5)
        self.qp.drawRect(r)
        self.qp.end()
        
class FigDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Загрузка теоретических изохрон')
        self.font1=QtGui.QFont() 
        self.font1.setPixelSize(16) 
        self.font2=QtGui.QFont() 
        self.font2.setPixelSize(13)
        
        self.LoadIsochBut=QtWidgets.QPushButton(self)
        self.LoadIsochBut.setText(u'Загрузить')
        
        self.LabelIsochName=QtWidgets.QLabel(self)
        self.LabelIsochName.setText('')
        self.LabelIsochName.setFont(self.font2)
        self.LabelIsochName.setEnabled(False)
        
        self.LabelIsochInfo=QtWidgets.QLabel(self)
        self.LabelIsochInfo.setText(u'Данные об изохронах')
        self.LabelIsochInfo.setFont(self.font1)
        
        self.LabelM=QtWidgets.QLabel(self)
        self.LabelM.setText(u'Фильтр')
        self.LabelM.setFont(self.font2)
        
        self.edM = QtWidgets.QLineEdit(self)
        
        self.LabelColor=QtWidgets.QLabel(self)
        self.LabelColor.setText(u'Цвет')
        self.LabelColor.setFont(self.font2)
        
        self.edColor = QtWidgets.QLineEdit(self)
        
        self.LabelSystem=QtWidgets.QLabel(self)
        self.LabelSystem.setText(u'Система фильтров')
        self.LabelSystem.setFont(self.font2)
        
        self.edSystem = QtWidgets.QLineEdit(self)
        
        self.LabelMetal=QtWidgets.QLabel(self)
        self.LabelMetal.setText(u'Металличность')
        self.LabelMetal.setFont(self.font2)
        
        self.edMetal = QtWidgets.QLineEdit(self)
        
        self.SaveIsochBut=QtWidgets.QPushButton(self)
        self.SaveIsochBut.setText(u'Сохранить')
        
        self.ExitBut=QtWidgets.QPushButton(self)
        self.ExitBut.setText(u'Закрыть')
        
        digrid=QtWidgets.QGridLayout()
        digrid.addWidget(self.LoadIsochBut,0,0)
        digrid.addWidget(self.LabelIsochName,0,1)
        digrid.addWidget(self.LabelIsochInfo,1,0)
        digrid.addWidget(self.LabelM,2,0)
        digrid.addWidget(self.edM,2,1)
        digrid.addWidget(self.LabelColor,3,0)
        digrid.addWidget(self.edColor,3,1)
        digrid.addWidget(self.LabelSystem,4,0)
        digrid.addWidget(self.edSystem,4,1)
        digrid.addWidget(self.LabelMetal,2,3)
        digrid.addWidget(self.edMetal,2,4)
        digrid.addWidget(self.SaveIsochBut,5,3)
        digrid.addWidget(self.ExitBut,5,4)
        self.setLayout(digrid)
        
        self.LoadIsochBut.clicked.connect(self.LoadIsochData)
        self.SaveIsochBut.clicked.connect(self.SaveNewIsoch)             
        self.ExitBut.clicked.connect(self.ExitDialog)			 
                     
    def LoadIsochData(self):
        self.IsochFileName=QtWidgets.QFileDialog.getOpenFileName(self)[0]
        self.LabelIsochName.setText(self.IsochFileName.split('/')[-1])
          
    def SaveNewIsoch(self):
        if (self.edColor.text()=='' or self.edSystem.text()=='' or self.edMetal.text()=='' or self.edM.text()==''):
            QtWidgets.QMessageBox.information(self, 
                            u'Внимание!',
                            u'Введите параметры изохрон!')
        else:
            try:
                self.IsochM=self.edM.text()
                self.IsochColor=self.edColor.text()
                self.IsochSystem=self.edSystem.text()
                self.IsochMetal=self.edMetal.text()
                df=pd.read_table(self.IsochFileName,engine='python',sep=' ',names=['logt',self.IsochM,self.IsochColor],comment='#',dtype={'logt':str})
                df['k']=pd.to_numeric(df['logt'])
                icount=df['k'].value_counts().sort_index()
                ind=icount.index
                val=icount.values
                logt=np.array([ind[0] for j in range(val[0])])
                num=np.array([j for j in range(val[0])])
                for i in range(1,len(ind)):
                    logt=np.append(logt,[ind[i] for j in range(val[i])])
                    num=np.append(num,[j for j in range(val[i])])
                arrays=[logt,num]
                df.drop('logt',1,inplace=True)
                df.drop('k',1,inplace=True)
                df.index=arrays
                df.index.names=('logt','num')
                df.to_csv('isochrones/'+self.IsochM+' '+self.IsochColor+' '+self.IsochSystem+' '+self.IsochMetal+'.csv')
                with open('isochrones/TheorIsochList.dat', 'a') as OutFile: 
                    OutFile.writelines(self.IsochM+' '+self.IsochColor+' '+self.IsochSystem+' '+self.IsochMetal) 
                    OutFile.write('\n')
            except:
                QtWidgets.QMessageBox.information(self, 
                                u"Системное сообщение",
                                u"Ошибка!")
            else:
                QtWidgets.QMessageBox.information(self, 
                                    u"Системное сообщение",
                                    u"Сохранено!")
    def ExitDialog(self):
        self.LabelIsochName.setText('')
        self.edM.clear()
        self.edColor.clear()
        self.edSystem.clear()
        self.edMetal.clear()
        self.close()

class HelpDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Help')
        self.textEdit = QtWidgets.QLabel(self)
        font1=QtGui.QFont() 
        font1.setPixelSize(12)
        self.textEdit.setFont(font1)
        vbox = QtWidgets.QVBoxLayout() 
        vbox.addWidget(self.textEdit)
        self.setLayout(vbox)

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(50, 50, screen.width()-200, screen.height()-200)
        self.setWindowTitle('Isochrone Fitting')
        self.setStyleSheet('background-color: white')
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)
        self.HelpWindow=HelpDialog(self)
        self.HelpWindow.setGeometry(600, 200, 600, 400)
        self.HelpWindow.textEdit.setGeometry(0,0,self.HelpWindow.width(),self.HelpWindow.height())
        menubar = self.menuBar()
        Help = menubar.addMenu('&Help')
        AboutProgr = QtWidgets.QAction(u'О программе', self)
        Help.addAction(AboutProgr)
        AboutProgr.triggered.connect(self.OpenHelp)
        
    def OpenHelp(self):
       self.HelpWindow.show()
       with open('Help.txt', 'r') as f:
           self.HelpWindow.textEdit.setText(f.read())
        
class MainWidget(QtWidgets.QWidget): 
    def __init__(self, parent=None):
        super(MainWidget,self).__init__(parent)   
        
        self.ColorEx=0
        self.Mm=0
        self.hColorEx=0.5
        self.hMm=0.5
        
        self.infwidget=MyWidget(self)
        self.isograph=CanvasIsoch(self)
        self.infwidget.LoadIsBut.clicked.connect(self.LoadIs)   
        self.infwidget.LoadDataBut.clicked.connect(self.LoadData)
        self.infwidget.Combologt.currentIndexChanged[int].connect(self.logtEdit)
        self.infwidget.edColorEx.textEdited[str].connect(self.ColorExEdit)
        self.infwidget.edhColorEx.textEdited[str].connect(self.hColorExEdit)
        self.infwidget.edMm.textEdited[str].connect(self.MmEdit)
        self.infwidget.edhMm.textEdited[str].connect(self.hMmEdit)
        self.infwidget.edMaxR.textEdited[str].connect(self.MaxREdit)
        self.infwidget.edMaxM.textEdited[str].connect(self.MaxMEdit)
        self.infwidget.ClearBut.clicked.connect(self.ClearGraph)
        self.infwidget.cbInvertY.stateChanged.connect(self.isograph.InvertY)
		
        hlayout = QtWidgets.QHBoxLayout()
        ntb_isoch= NavigationToolbar(self.isograph, self)
        hntb=QtWidgets.QHBoxLayout()
        hntb.addStretch()
        hntb.addStretch()
        hntb.addWidget(ntb_isoch)
        hlayout.addWidget(self.infwidget, 1)
        hlayout.addWidget(self.isograph, 2)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addLayout(hntb)
        self.setLayout(vlayout)
        
    def MaxREdit(self,text):
        try:
            self.Data['flag_r']=self.Data.r < float(text)
            idx = pd.IndexSlice
            self.isograph.UpdateDataPlot(self.Data.M.loc[idx[self.Data.flag_r]],self.Data.Color.loc[idx[self.Data.flag_r]],self.infwidget.cbInvertY.isChecked())
            self.makeDensPlot()
        except (ValueError,TypeError,AttributeError):
            pass
    
    def ClearGraph(self):
        try:
            self.isograph.line1[0].remove()
            self.isograph.fig.canvas.draw()
        except:
            pass
        try:
            self.isograph.line2[0].remove()
            self.isograph.fig.canvas.draw()
        except:
            pass
        try:
            self.isograph.densAll[0].remove()
            self.isograph.fig.canvas.draw()
        except:
            pass
        try:
            self.isograph.densClust[0].remove()
            self.isograph.fig.canvas.draw()
        except:
            pass
    
    def MaxMEdit(self,text):
        try:
            self.makeDensPlot()
        except (ValueError,TypeError,AttributeError):
            pass
               
    def logtEdit(self,n):
        self.AgeInd=n
        self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
        try:
            self.makeDensPlot()
        except:
            pass
        
    def ColorExEdit(self,text):
        try:
            self.ColorEx=float(text)
            self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
        except (ValueError,TypeError):
            pass
        else:
            try:
                self.makeDensPlot()
            except:
                pass
        
    def hColorExEdit(self,text):
        try:
            self.ColorEx=float(text)
        except (ValueError,TypeError):
            pass    
    
    def MmEdit(self,text):
        try:
            self.Mm=float(text)
            self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
        except (ValueError,TypeError):
            pass
        else:
            try:
                self.makeDensPlot()
            except:
                pass
            
    def hMmEdit(self,text):
        try:
            self.hMm=float(text)
        except (ValueError,TypeError):
            pass
        
    def LoadIs(self):
        if self.infwidget.ComboThIs.currentText()!='M_Color_System':
            self.path='isochrones/'+self.infwidget.isochname+' '+str(self.infwidget.ComboMetal.currentText())+'.csv'
            self.Isochrone=pd.read_csv(self.path)
            self.Isochrone.set_index(['logt','num'],inplace=True)
            self.Ages=self.Isochrone.index.levels[0].values
            self.AgeInd=0
            self.isograph.Color_name=self.infwidget.ComboThIs.currentText().split(' ')[1]
            self.isograph.M_name=self.infwidget.ComboThIs.currentText().split(' ')[0]
            self.isograph.ax2.set_xlabel(self.isograph.Color_name)
            self.isograph.ax2.set_ylabel(self.isograph.M_name)
            self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]],self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]])
            self.infwidget.edColorEx.setText('0')
            self.infwidget.edMm.setText('0')
            self.infwidget.Combologt.clear()
            self.infwidget.Combologt.addItems([str(self.Ages[i]) for i in range(len(self.Ages))])
            self.infwidget.Combologt.setEnabled(True)
            self.infwidget.edhColorEx.setText(str(self.hColorEx))
            self.infwidget.edhMm.setText(str(self.hMm))
            try:
                self.Data
            except AttributeError:
                pass
            else:
                self.makeDensPlot()
        
    def LoadData(self):
        self.DataFileName=QtWidgets.QFileDialog.getOpenFileName(self)[0]
        try:
            self.isograph.line2[0].remove()
        except:
            pass
        finally:
            self.infwidget.LabelDataName.setText(self.DataFileName.split('/')[-1])
            try:
                fline='#'
                with open(self.DataFileName) as fd:
                    while(fline[0]=='#'):
                          fline=fd.readline()
                pattern=re.compile(r'[^\d^\.]+')
                sep=pattern.search(fline)[0]
                self.Data=pd.read_csv(self.DataFileName,engine='python',sep=sep,names=['r','M','Color'],comment='#',index_col=False)
                if self.infwidget.edMaxR.text()=='':
                    self.infwidget.edMaxR.setText(str(round(max(self.Data['r']),5)))
                    self.Data['flag_r']=True
                else:
                    self.Data['flag_r']=self.Data.r < float(self.infwidget.edMaxR.text())
                if self.infwidget.edMaxM.text()=='':
                    self.infwidget.edMaxM.setText(str(round(max(self.Data['M']),5)))
                try:
                    self.Isochrone
                except AttributeError:
                    self.Data['flag_M']=False
                else:
                    self.makeDensPlot()
                finally:
                    idx = pd.IndexSlice
                    self.isograph.UpdateDataPlot(self.Data.M.loc[idx[self.Data.flag_r]],self.Data.Color.loc[idx[self.Data.flag_r]],self.infwidget.cbInvertY.isChecked())
            except FileNotFoundError:
                pass
        
    def makeDensPlot(self):
        self.makeDensInd(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]],self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]])
        self.isograph.UpdateDensPlot(self.Data.r,self.Data.flag_M,self.Data['flag_r'])
    
    def makeDensInd(self,x,y):
        self.IsochInterpol=interpolate.interp1d(x+self.Mm,y+self.ColorEx, kind='linear')
        One_M=self.Data.M<float(self.infwidget.edMaxM.text())
        One_r=self.Data.r<float(self.infwidget.edMaxR.text())
        One=One_M & One_r
        Two=self.Data.M>min(x+self.Mm)
        Three=self.Data.M<max(x+self.Mm)
        Flag1=One & Two
        Flag=Flag1 & Three
        idx = pd.IndexSlice
        new_y=self.IsochInterpol(self.Data.M.loc[idx[Flag]])
        Four=self.Data.Color.loc[idx[Flag]] > new_y-0.05
        Five=self.Data.Color.loc[idx[Flag]] < new_y+0.05
        self.Data['flag_M']=Four & Five
    
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Comma:
            try:
                self.ColorEx=self.ColorEx-self.hColorEx
                self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
                self.infwidget.edColorEx.setText(str(round(self.ColorEx,5)))
            except AttributeError:
                pass
            try:
                self.makeDensPlot()
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_Period:
            try:
                self.ColorEx=self.ColorEx+self.hColorEx
                self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
                self.infwidget.edColorEx.setText(str(round(self.ColorEx,5)))
            except AttributeError:
                pass
            try:
                self.makeDensPlot()
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_A:
            try:
                if self.infwidget.cbInvertY.isChecked():
                    a=1
                else:
                    a=-1
                self.Mm=self.Mm-math.copysign(self.hMm,a)
                self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
                self.infwidget.edMm.setText(str(round(self.Mm,5)))
            except AttributeError:
                pass
            try:
                self.makeDensPlot()
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_Z:
            try:
                if self.infwidget.cbInvertY.isChecked():
                    a=1
                else:
                    a=-1
                self.Mm=self.Mm+math.copysign(self.hMm,a)
                self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
                self.infwidget.edMm.setText(str(round(self.Mm,5)))
            except AttributeError:
                pass
            try:
                self.makeDensPlot()
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_P:
            try:
                if self.AgeInd>=1:
                    self.AgeInd=self.AgeInd-1
                self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
                self.infwidget.Combologt.setCurrentIndex(self.AgeInd)
            except AttributeError:
                pass
            try:
                self.makeDensPlot()
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_N:
            try:
                if self.AgeInd<len(self.Ages)-1:
                    self.AgeInd=self.AgeInd+1
                self.isograph.UpdatePlot(self.Isochrone[self.isograph.M_name].loc[self.Ages[self.AgeInd]]+self.Mm,self.Isochrone[self.isograph.Color_name].loc[self.Ages[self.AgeInd]]+self.ColorEx)
                self.infwidget.Combologt.setCurrentIndex(self.AgeInd)
            except AttributeError:
                pass
            try:
                self.makeDensPlot()
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_BracketLeft:
            try:
                self.hMm=self.hMm/2
                self.infwidget.edhMm.setText(str(round(self.hMm,5)))
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_BracketRight:
            try:
                self.hMm=self.hMm*2
                self.infwidget.edhMm.setText(str(round(self.hMm,5)))
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_Semicolon:
            try:
                self.hColorEx=self.hColorEx/2
                self.infwidget.edhColorEx.setText(str(round(self.hColorEx,5)))
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_Apostrophe:
            try:
                self.hColorEx=self.hColorEx*2
                self.infwidget.edhColorEx.setText(str(round(self.hColorEx,5)))
            except AttributeError:
                pass
        if e.key() == QtCore.Qt.Key_ParenRight:
            try:
                self.isograph.densAll
            except AttributeError:
                pass
            else:
                self.isograph.N=self.isograph.N*2
                self.makeDensPlot()
        if e.key() == QtCore.Qt.Key_ParenLeft:
            try:
                self.isograph.densAll
            except AttributeError:
                pass
            else:
                self.isograph.N=int(self.isograph.N/2)
                self.makeDensPlot()
        
    def mousePressEvent(self, e):
        QtWidgets.QApplication.focusWidget().clearFocus()
        self.infwidget.setFocus()
        
        
app = QtWidgets.QApplication(sys.argv)
mainDialog = MyWindow(None)
mainDialog.show()
sys.exit(app.exec_())  
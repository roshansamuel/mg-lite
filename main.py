#!/usr/bin/python3

#################################################################################
# MG-Lite
# 
# Copyright (C) 2020, Roshan J. Samuel
#
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#     3. Neither the name of the copyright holder nor the
#        names of its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#################################################################################

# Import all necessary modules
import sys
import mgLite as mgSolver
import PyQt5.QtGui as qgui
import PyQt5.QtCore as qcore
import PyQt5.QtWidgets as qwid

################################## MAIN WINDOW ##################################

class mainWindow(qwid.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(450, 500)
        self.initUI()

    def initUI(self):
        # Widgets to get and set sInd
        gsLabel = qwid.QLabel("Select number of points in domain", self)
        gsLabel.resize(gsLabel.sizeHint())
        gsLabel.move(30, 32)

        self.gsCBox = qwid.QComboBox(self)
        self.gsCBox.setToolTip("Grid sizes are of form 2^n + 1 to facilitate restrictions and prolongations of V-Cycle")
        for i in range(2, 15):
            n = 2**i + 1
            self.gsCBox.addItem(str(n))
        self.gsCBox.currentIndexChanged.connect(self.gsCBoxSelection)
        self.gsCBox.move(300, 25)

        # Widgets to get and set VDepth
        vdLabel = qwid.QLabel("Set depth for multi-grid V-Cycles", self)
        vdLabel.resize(vdLabel.sizeHint())
        vdLabel.move(30, 82)

        self.vdSBox = qwid.QSpinBox(self)
        self.vdSBox.setToolTip("Depth is restricted by number of points chosen above")
        self.vdSBox.setMinimum(1)
        self.vdSBox.setMaximum(1)
        self.vdSBox.move(300, 75)

        # Widgets to set vcCnt, preSm and pstSm
        vcLabel = qwid.QLabel("Enter number of V-Cycles to be computed", self)
        vcLabel.resize(vcLabel.sizeHint())
        vcLabel.move(30, 132)

        preLabel = qwid.QLabel("Enter number pre-smoothing iterations", self)
        preLabel.resize(preLabel.sizeHint())
        preLabel.move(30, 182)

        pstLabel = qwid.QLabel("Enter number post-smoothing iterations", self)
        pstLabel.resize(pstLabel.sizeHint())
        pstLabel.move(30, 232)

        self.vcSBox = qwid.QSpinBox(self)
        self.vcSBox.setMinimum(1)
        self.vcSBox.setMaximum(32)
        self.vcSBox.move(300, 125)

        self.preSBox = qwid.QSpinBox(self)
        self.preSBox.setMinimum(1)
        self.preSBox.setMaximum(16)
        self.preSBox.move(300, 175)

        self.pstSBox = qwid.QSpinBox(self)
        self.pstSBox.setMinimum(1)
        self.pstSBox.setMaximum(16)
        self.pstSBox.move(300, 225)

        # Widgets to set tolerance
        tolLabel = qwid.QLabel("Enter tolerance for Gauss-Seidel", self)
        tolLabel.resize(tolLabel.sizeHint())
        tolLabel.move(30, 282)

        self.tolLEdit = qwid.QLineEdit("1.0e-6", self)
        self.tolLEdit.setToolTip("Please enter tolerance in scientific notion as shown")
        self.tolLEdit.setAlignment(qcore.Qt.AlignRight)
        self.tolLEdit.move(300, 275)

        # Widgets to decide what should be plotted
        self.solChBox = qwid.QCheckBox("Plot computed and analytical solution", self)
        self.solChBox.resize(self.solChBox.sizeHint())
        self.solChBox.move(30, 332)

        self.errChBox = qwid.QCheckBox("Plot error in computed solution", self)
        self.errChBox.resize(self.errChBox.sizeHint())
        self.errChBox.move(30, 362)

        self.conChBox = qwid.QCheckBox("Plot convergence of residual", self)
        self.conChBox.resize(self.conChBox.sizeHint())
        self.conChBox.move(30, 392)

        # Start button
        startButton = qwid.QPushButton('Start', self)
        startButton.clicked.connect(self.startSolver)
        startButton.resize(startButton.sizeHint())
        startButton.move(180, 440)

        # Quit button
        quitButton = qwid.QPushButton('Quit', self)
        quitButton.clicked.connect(self.close)
        quitButton.resize(quitButton.sizeHint())
        quitButton.move(300, 440)

        self.setWindowTitle('MG-Lite')
        self.setWindowIcon(qgui.QIcon('icon.png'))

        self.show()

    def gsCBoxSelection(self, i):
        maxDepth = i + 1
        self.vdSBox.setMaximum(i + 1)

    def startSolver(self):
        mgSolver.sInd = int(self.gsCBox.currentIndex()) + 2
        mgSolver.VDepth = self.vdSBox.value()
        mgSolver.vcCnt = self.vcSBox.value()
        mgSolver.preSm = self.preSBox.value()
        mgSolver.pstSm = self.pstSBox.value()
        mgSolver.tolerance = float(self.tolLEdit.text())

        self.cWindow = consoleWindow(self.solChBox, self.errChBox, self.conChBox)
        self.cWindow.runSolver()

    def closeEvent(self, event):
        reply = qwid.QMessageBox.question(self, 'Close Window', "Are you sure?", qwid.QMessageBox.Yes | qwid.QMessageBox.No, qwid.QMessageBox.No)

        if reply == qwid.QMessageBox.Yes:
            try:
                self.cWindow.close()
            except:
                pass

            event.accept()
        else:
            event.ignore()

############################### CONSOLE WINDOW ##################################

class consoleWindow(qwid.QMainWindow):
    def __init__(self, sCBox, eCBox, rCBox):
        super().__init__()

        self.sPlot = sCBox.isChecked()
        self.ePlot = eCBox.isChecked()
        self.rPlot = rCBox.isChecked()

        self.setFixedSize(400, 400)
        self.initUI()

    def initUI(self):
        # Text edit box to output console stream
        self.conTEdit = qwid.QTextEdit(self)
        self.conTEdit.resize(340, 300)
        self.conTEdit.move(30, 30)

        # Plot button
        plotButton = qwid.QPushButton('Plot', self)
        plotButton.clicked.connect(self.plotSolution)
        plotButton.resize(plotButton.sizeHint())
        plotButton.move(165, 350)

        if (self.sPlot or self.ePlot or self.rPlot):
            plotButton.setEnabled(True)
        else:
            plotButton.setEnabled(False)

        # Close button
        closeButton = qwid.QPushButton('Close', self)
        closeButton.clicked.connect(self.close)
        closeButton.resize(closeButton.sizeHint())
        closeButton.move(275, 350)

        self.setWindowTitle('MG-Lite Console Output')
        self.setWindowIcon(qgui.QIcon('icon.png'))

        self.show()

    def runSolver(self):
        mgSolver.main(self)
        qwid.QApplication.processEvents()

    def updateTEdit(self, cOutString):
        self.conTEdit.append(cOutString)
        qwid.QApplication.processEvents()

    def plotSolution(self):
        if self.sPlot:
            mgSolver.plotResult(0)
        if self.ePlot:
            mgSolver.plotResult(1)
        if self.rPlot:
            mgSolver.plotResult(2)


############################## THAT'S IT, FOLKS!! ###############################

if __name__ == '__main__':
    app = qwid.QApplication(sys.argv)
    welWindow = mainWindow()

    sys.exit(app.exec_())

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

        self.setFixedSize(427, 550)
        self.initUI()

    def initUI(self):
        # Widgets to get grid size
        gsLabel = qwid.QLabel("Number of points in the domain", self)
        gsLabel.resize(gsLabel.sizeHint())
        gsLabel.move(32, 32)

        self.gsCBox = qwid.QComboBox(self)
        self.gsCBox.setToolTip("<p>Grid should have 2^n + 1 points to enable restriction and prolongation during V-Cycles<\p>")
        for i in range(2, 15):
            n = 2**i + 1
            self.gsCBox.addItem(str(n))
        self.gsCBox.currentIndexChanged.connect(self.gsCBoxSelection)
        self.gsCBox.move(295, 25)

        # Widgets to get depth of V-Cycles
        vdLabel = qwid.QLabel("Depth of multi-grid V-Cycles", self)
        vdLabel.resize(vdLabel.sizeHint())
        vdLabel.move(32, 82)

        self.vdSBox = qwid.QSpinBox(self)
        self.vdSBox.setToolTip("<p>Depth is restricted by the number of points chosen above<\p>")
        self.vdSBox.setMinimum(1)
        self.vdSBox.setMaximum(1)
        self.vdSBox.move(295, 75)

        # Widgets to get number of V-Cycles
        vcLabel = qwid.QLabel("Number of V-Cycles to be computed", self)
        vcLabel.resize(vcLabel.sizeHint())
        vcLabel.move(32, 132)

        self.vcSBox = qwid.QSpinBox(self)
        self.vcSBox.setMinimum(1)
        self.vcSBox.setMaximum(32)
        self.vcSBox.move(295, 125)
        self.vcSBox.valueChanged.connect(self.vcCountCheck)

        # Widgets to get number of pre-smoothing iterations
        preLabel = qwid.QLabel("Number of pre-smoothing iterations", self)
        preLabel.resize(preLabel.sizeHint())
        preLabel.move(32, 182)

        self.preSBox = qwid.QSpinBox(self)
        self.preSBox.setMinimum(1)
        self.preSBox.setMaximum(16)
        self.preSBox.move(295, 175)

        # Widgets to get number of post-smoothing iterations
        pstLabel = qwid.QLabel("Number of post-smoothing iterations", self)
        pstLabel.resize(pstLabel.sizeHint())
        pstLabel.move(32, 232)

        self.pstSBox = qwid.QSpinBox(self)
        self.pstSBox.setMinimum(1)
        self.pstSBox.setMaximum(16)
        self.pstSBox.move(295, 225)

        # Widgets to get tolerance for iterative solver
        tolLabel = qwid.QLabel("Tolerance of Gauss-Seidel solver", self)
        tolLabel.resize(tolLabel.sizeHint())
        tolLabel.move(32, 282)

        self.tolLEdit = qwid.QLineEdit("1.0e-6", self)
        self.tolLEdit.setToolTip("<p>It is best to enter tolerance in scientific notion as shown<\p>")
        self.tolLEdit.setAlignment(qcore.Qt.AlignRight)
        self.tolLEdit.move(295, 275)

        # A Frame widget containing widgets to enable or disable non-uniform grid
        nuFrame = qwid.QFrame(self)
        nuFrame.setFrameStyle(qwid.QFrame.StyledPanel)
        nuFrame.resize(375, 46)
        nuFrame.move(25, 322)

        # Check box to enable non-uniform grid
        self.nugChBox = qwid.QCheckBox("Enable non-uniform grid", self)
        self.nugChBox.setToolTip("<p>Use a tangent-hyperbolic grid which is fine near the boundaries and coarse at the center of the domain<\p>")
        self.nugChBox.resize(self.nugChBox.sizeHint())
        self.nugChBox.move(40, 335)
        self.nugChBox.stateChanged.connect(self.nuGridCheck)

        # Widgets to get the tangent-hyperbolic grid stretching factor, beta
        self.betLabel = qwid.QLabel("Beta", self)
        self.betLabel.setToolTip("<nobr>Stretching parameter for <\nobr>tangent-hyperbolic grid")
        self.betLabel.resize(self.betLabel.sizeHint())
        self.betLabel.setEnabled(False)
        self.betLabel.move(275, 337)

        self.betLEdit = qwid.QLineEdit("0.5", self)
        self.betLEdit.setToolTip("<p>Must be a floating point number greater than 0, but not greater than 3<\p>")
        self.betLEdit.setAlignment(qcore.Qt.AlignRight)
        self.betLEdit.setEnabled(False)
        self.betLEdit.resize(70, 30)
        self.betLEdit.move(322, 330)

        # A few check boxes to decide what should be plotted
        self.solChBox = qwid.QCheckBox("Plot computed and analytical solution", self)
        self.solChBox.resize(self.solChBox.sizeHint())
        self.solChBox.move(30, 382)

        self.errChBox = qwid.QCheckBox("Plot error in computed solution", self)
        self.errChBox.resize(self.errChBox.sizeHint())
        self.errChBox.move(30, 412)

        self.conChBox = qwid.QCheckBox("Plot convergence of residual", self)
        self.conChBox.resize(self.conChBox.sizeHint())
        self.conChBox.setToolTip("<p>To plot residual convergence, we need at least 3 V-Cycles<\p>")
        self.conChBox.setEnabled(False)
        self.conChBox.move(30, 442)

        # Start button - to start the simulation :)
        startButton = qwid.QPushButton('Start', self)
        startButton.clicked.connect(self.startSolver)
        startButton.resize(startButton.sizeHint())
        startButton.move(180, 490)

        # Quit button - to quit the program :(
        quitButton = qwid.QPushButton('Quit', self)
        quitButton.clicked.connect(self.close)
        quitButton.resize(quitButton.sizeHint())
        quitButton.move(300, 490)

        # Window title and icon
        self.setWindowTitle('MG-Lite')
        self.setWindowIcon(qgui.QIcon('icon.png'))

        # Reveal thyself
        self.show()

    # This function restricts the maximum value of the SpinBox used to set V-Cycle depth.
    # This maximum value is obtained from the grid-size, passed as an index, i
    def gsCBoxSelection(self, i):
        maxDepth = i + 1
        self.vdSBox.setMaximum(i + 1)

    # This function enables or disables the CheckBox to plot convergence of resiudal
    # This is decided by the number of V-Cycles to be computed.
    # It makes no sense to plot convergence for less than 3 V-Cycles
    def vcCountCheck(self):
        if self.vcSBox.value() > 2:
            self.conChBox.setEnabled(True)
        else:
            self.conChBox.setEnabled(False)
            self.conChBox.setChecked(False)

    # This function enables or disables the LineEdit used to enter the tangent-hyperbolic
    # grid stretching parameter, beta.
    # This decision is based on the state of the CheckBox for non-uniform grid.
    def nuGridCheck(self):
        if self.nugChBox.isChecked() == True:
            self.betLabel.setEnabled(True)
            self.betLEdit.setEnabled(True)
        else:
            self.betLabel.setEnabled(False)
            self.betLEdit.setEnabled(False)

    # This function interfaces with the multi-grid solver and sets its parameters.
    # These parameters are read from the inputs given in the window.
    # It then opens the console window and hands the baton to it.
    def startSolver(self):
        tolValue = 0.0
        # Check if tolerance specified is valid
        try:
            tolValue = float(self.tolLEdit.text())
        except:
            errDialog = qwid.QMessageBox.critical(self, 'Invalid Tolerance', "The specified tolerance is not a valid floating point number! :(", qwid.QMessageBox.Ok)
            return 1

        # Check if uniform grid flag is enabled
        mgSolver.nuFlag = self.nugChBox.isChecked()
        if mgSolver.nuFlag:
            betValue = 0.0
            # Check if beta value specified is valid
            try:
                betValue = float(self.betLEdit.text())
            except:
                errDialog = qwid.QMessageBox.critical(self, 'Invalid Stretching Parameter', "The specified beta is not a valid floating point number! :(", qwid.QMessageBox.Ok)
                return 1

            # If valid floating point is available, check if it is usable
            if betValue <= 0.0:
                errDialog = qwid.QMessageBox.critical(self, 'Bad Stretching Parameter', "Beta should be greater than 0! :o", qwid.QMessageBox.Ok)
                return 1

            if betValue <= 0.0 or betValue > 3.0:
                errDialog = qwid.QMessageBox.critical(self, 'Bad Stretching Parameter', "Beta is too high (> 3.0) to make a useful grid. :-|", qwid.QMessageBox.Ok)
                return 1

            # If both above checks are passed, have no fear! Set the value of beta.
            mgSolver.beta = betValue

        # Now set all the other less complicated parameters
        mgSolver.sInd = int(self.gsCBox.currentIndex()) + 2

        mgSolver.VDepth = self.vdSBox.value()
        mgSolver.vcCnt = self.vcSBox.value()
        mgSolver.preSm = self.preSBox.value()
        mgSolver.pstSm = self.pstSBox.value()

        mgSolver.tolerance = tolValue

        # Open console window and run the solver
        self.cWindow = consoleWindow(self.solChBox, self.errChBox, self.conChBox)
        self.cWindow.runSolver()

    # Clingy function for a clingy app - makes sure that the user wants to quit the app
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

        # Three boolean flags for the three check boxes in the main window for plots
        self.sPlot = sCBox.isChecked()
        self.ePlot = eCBox.isChecked()
        self.rPlot = rCBox.isChecked()

        self.setFixedSize(400, 400)
        self.initUI()

    def initUI(self):
        # Text box to output console stream
        self.conTEdit = qwid.QTextEdit(self)
        self.conTEdit.resize(340, 300)
        self.conTEdit.move(30, 30)

        # Plot button
        plotButton = qwid.QPushButton('Plot', self)
        plotButton.clicked.connect(self.plotSolution)
        plotButton.resize(plotButton.sizeHint())
        plotButton.move(165, 350)

        # The plot button will be disabled if none of the check boxes in main window are checked
        if (self.sPlot or self.ePlot or self.rPlot):
            plotButton.setEnabled(True)
        else:
            plotButton.setEnabled(False)

        # Close button
        closeButton = qwid.QPushButton('Close', self)
        closeButton.clicked.connect(self.close)
        closeButton.resize(closeButton.sizeHint())
        closeButton.move(275, 350)

        # Window title and icon
        self.setWindowTitle('MG-Lite Console Output')
        self.setWindowIcon(qgui.QIcon('icon.png'))

        # Reveal thyself
        self.show()

    # As the function name says, it calls the main() of the MG solver
    def runSolver(self):
        mgSolver.main(self)
        qwid.QApplication.processEvents()

    # This function is called by the MG solver at all places where it normally uses the print()
    # command. The string passed to the print command is instead passed to this function,
    # which sends it to the text box of the console window.
    def updateTEdit(self, cOutString):
        self.conTEdit.append(cOutString)
        qwid.QApplication.processEvents()

    # This function is called by the 'Plot' button when clicked.
    # It merely calls the plotResult() function of the MG solver, with appropriate arguments.
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

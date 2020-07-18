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
import numpy as np
import matplotlib.pyplot as plt

################################ GRID CONSTANTS #################################

# N should be of the form 2^n + 1
# Then there will be 2^n + 3 staggered points, including 2 ghost points
sLst = [2**x + 1 for x in range(15)]

# Choose grid size as an index from below list
# Size index: 0 1 2 3  4  5  6  7   8   9   10   11   12   13    14
# Grid sizes: 2 3 5 9 17 33 65 129 257 513 1025 2049 4097 8193 16385
sInd = 7

############################# MULTI-GRID CONSTANTS ##############################

# Tolerance value in iterative solver
tolerance = 1.0e-6

# Depth of each V-cycle in multigrid (ideally VDepth = sInd - 1)
VDepth = 6

# Number of V-cycles to be computed
vcCnt = 10

# Number of iterations during pre-smoothing
preSm = 2

# Number of iterations during post-smoothing
pstSm = 2

# Maximum number of iterations while solving
maxCount = 10*sLst[sInd]

############################### GLOBAL VARIABLES ################################

# Get array of grid sizes
N = sLst[sInd:sInd - VDepth - 1:-1]

# Define array of grid spacings
hx = [1.0/(x-1) for x in N]

# Square of hx, used in finite difference formulae
hx2 = [x*x for x in hx]

# Integer specifying the level of V-cycle at any point while solving
vLev = 0

# Flag to determine if non-zero homogenous BC has to be applied or not
zeroBC = False

############################## MULTI-GRID SOLVER ###############################

np.set_printoptions(precision=3)

def multigrid(H):
    global N
    global vcCnt

    rData[vLev] = H
    chMat = np.zeros(N[0] + 2)

    for i in range(vcCnt):
        v_cycle()

        chMat = laplace(pData[vLev])
        resVal = np.amax(np.abs(H[1:N[0]+1] - chMat[1:N[0]+1]))

        print("Residual after V-Cycle ", i, " is ", resVal)

    return pData[vLev]


#Multigrid V-cycle without the use of recursion
def v_cycle():
    global hx
    global VDepth
    global vLev, zeroBC
    global pstSm, preSm

    vLev = 0
    zeroBC = False

    # Pre-smoothing
    smooth(preSm)

    zeroBC = True
    for i in range(VDepth):
        # Compute residual
        calcResidual()

        # Copy smoothed pressure for later use
        sData[vLev] = np.copy(pData[vLev])

        # Restrict to coarser level
        restrict()

        # Reinitialize pressure at coarser level to 0
        pData[vLev].fill(0.0)

        if vLev == VDepth:
            solve()
        else:
            smooth(preSm + pstSm)

    # Prolongation operations
    for i in range(VDepth):
        # Prolong pressure to next finer level
        prolong()

        # Add previously stored smoothed data
        pData[vLev] += sData[vLev]

        if vLev:
            zeroBC = True
        else:
            zeroBC = False

        # Post-smoothing
        smooth(pstSm)


#Uses jacobi iteration to smooth the solution passed to it.
def smooth(iteration_times):
    global N
    global hx2
    global vLev

    n = N[vLev]
    tData = np.zeros(n)
    for i in range(iteration_times):
        imposeBC(pData[vLev])

        tData = (pData[vLev][2:] + pData[vLev][:n] - hx2[vLev]*rData[vLev][1:n+1])*0.5

        pData[vLev][1:n+1] = np.copy(tData)


#Compute the residual and store it into iTemp array
def calcResidual():
    global vLev
    global iTemp, rData, pData

    iTemp[vLev].fill(0.0)
    iTemp[vLev] = rData[vLev] - laplace(pData[vLev])


#Reduces the size of the array to a lower level, 2^(n - 1) + 1
def restrict():
    global vLev
    global iTemp, rData

    pLev = vLev
    vLev += 1

    for i in range(1, N[vLev] + 1):
        i2 = i*2
        rData[vLev][i] = 0.5*(iTemp[pLev][i2 - 1]) + 0.25*(iTemp[pLev][i2 - 2] + iTemp[pLev][i2])


# Increases the size of the array to a higher level, 2^(n + 1) + 1
def prolong():
    global vLev
    global pData

    pLev = vLev
    vLev -= 1

    for i in range(1, N[vLev] + 1):
        i2 = int(i/2) + 1;
        if i % 2:
            pData[vLev][i] = pData[pLev][i2]
        else:
            pData[vLev][i] = (pData[pLev][i2] + pData[pLev][i2 - 1])*0.5;


#This function solves at coarsest level using an iterative solver
def solve():
    global vLev
    global N, hx2
    global maxCount
    global tolerance
    global pData, rData

    n = N[vLev]
    solLap = np.zeros(n)

    jCnt = 0
    while True:
        imposeBC(pData[vLev])

        # Gauss-Seidel iterative solver
        pData[vLev][1:n+1] = (pData[vLev][2:] + pData[vLev][:n] - hx2[vLev]*rData[vLev][1:n+1])*0.5

        solLap = (pData[vLev][:n] - 2.0*pData[vLev][1:n+1] + pData[vLev][2:])/hx2[vLev]

        maxErr = np.amax(np.abs(rData[vLev][1:n+1] - solLap))
        if maxErr < tolerance:
            break

        jCnt += 1
        if jCnt > maxCount:
            print("ERROR: Jacobi not converging. Aborting")
            quit()

    imposeBC(pData[vLev])


def laplace(function):
    global vLev
    global N, hx2

    n = N[vLev]

    gradient = np.zeros_like(function)
    gradient[1:n+1] = (function[:n] - 2.0*function[1:n+1] + function[2:])/hx2[vLev]

    return gradient


def initVariables():
    global N
    global nList, pData, rData, sData, iTemp

    nList = np.array(N)

    pData = [np.zeros(x) for x in nList + 2]

    rData = [np.zeros_like(x) for x in pData]
    sData = [np.zeros_like(x) for x in pData]
    iTemp = [np.zeros_like(x) for x in pData]


############################## BOUNDARY CONDITION ###############################


def imposeBC(P):
    global pWall
    global zeroBC

    # Dirichlet BC
    if zeroBC:
        # Homogenous BC
        P[0] = -P[2]
        P[-1] = -P[-3]
    else:
        # Non-homogenous BC
        P[0] = 2.0*pWall - P[2]
        P[-1] = 2.0*pWall - P[-3]


############################### TEST CASE DETAIL ################################


def initDirichlet():
    global N
    global hx
    global pWall, pAnlt

    # Compute analytical solution, (r^2)/2
    pAnlt = np.zeros(N[0] + 2)

    halfIndX = int(N[0]/2) + 1
    for i in range(N[0] + 2):
        xDist = hx[0]*(i - halfIndX)
        pAnlt[i] = xDist*xDist/2.0

    # Value of P at wall according to analytical solution
    pWall = pAnlt[1]


############################### PLOTTING ROUTINE ################################


def plotResult(pSoln):
    global N
    global pAnlt

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["mathtext.fontset"] = 'cm'
    plt.rcParams["font.weight"] = "medium"

    plt.figure(figsize=(14,10))

    x = np.linspace(0.0, 1.0, N[0])
    plt.plot(x, pAnlt[1:-1], label='Analytic', marker='*', markersize=20, linewidth=4)
    plt.plot(x, pSoln[1:-1], label='Computed', marker='+', markersize=20, linewidth=4)
    plt.xlabel('x', fontsize=40)
    plt.ylabel('p', fontsize=40)

    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.legend(fontsize=40)
    plt.show()


##################################### MAIN ######################################


def main():
    global N
    global nList, iTemp

    initDirichlet()
    initVariables()

    mgRHS = np.ones(N[0] + 2)
    mgLHS = multigrid(mgRHS)

    plotResult(mgLHS)


if __name__ == "__main__":
    main()


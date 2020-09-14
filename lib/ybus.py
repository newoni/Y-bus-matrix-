#<20.09.11> make Y bus matrix
import numpy as np
import pandas as pd
'''
mkYbus
----------------------------------------------------------
|   input
----------------------------------------------------------
busData : Data frame type bus data
lineData : Data frame type line data
transData : Data frame type transformer data
----------------------------------------------------------
 | main method and it's output
----------------------------------------------------------
main method : mkYbus
output : np.ndarray type Y bus matrix

----------------------------------------------------------
|   example
----------------------------------------------------------
sample_object = Ybus_maker(busData=grid_data[0], lineData=grid_data[1], transData=grid_data[2])

yBusMatrix = sample_object.mkYbus


'''
class Ybus_maker:
    def __init__(self, busData, lineData, transData, shuntCapData):
        self.busData = busData
        self.lineData = lineData
        self.transData = transData
        self.shuntCapData = shuntCapData

        self.numBus = len(self.busData)
        self.numBranch = len(self.lineData)
        self.numTrans = len(self.transData)


    def mkYbus(self):

        self.incidence_matrix = self.mkIncidence_matrix()
        self.diag_Ymatrix = self.mkDiagAdmittance_matrix()
        self.b_matrix = self.mkBadmittance_matrix()

        # shunt capacitor 가 있을 경우 추가
        try:
            self.shuntCap_matrix = self.mkShuntCap_matrix()

        except:
            self.shuntCap_matrix = np.zeros((self.numBus,self.numBus), dtype=np.complex)
        ####e

        # tap ratio 고려 한 trans matrix 부르기
        try:
            self.trans_matrix = self.mkTrans_matrix()

        except:
            self.trans_matrix = np.zeros((self.numBus,self.numBus), dtype=np.complex)


        # A^T * diag_Y * A 로 Y-Buse matrix 만들기 (pi model admittance와 변압기 저항 고려)
        self.yBus_matrix = np.matmul(np.transpose(self.incidence_matrix), self.diag_Ymatrix)
        self.yBus_matrix = np.matmul(self.yBus_matrix, self.incidence_matrix)
        self.yBus_matrix = self.yBus_matrix + self.b_matrix + self.shuntCap_matrix + self.trans_matrix

        return self.yBus_matrix


    def mkIncidence_matrix(self):

        incidence_matrix = np.zeros((self.numBranch, self.numBus))

        for i in range(self.numBranch):
            incidence_matrix[i][self.lineData[self.lineData.columns[0]][self.lineData.index[i]]-1] = 1     # from bus에 연결될 경우 1
            incidence_matrix[i][self.lineData[self.lineData.columns[1]][self.lineData.index[i]]-1] = -1     # to bus에 연결될 경우 -1

        return incidence_matrix

    def mkDiagAdmittance_matrix(self):
        diag_Ymatrix = np.zeros((self.numBranch, self.numBranch),dtype=np.complex)

        for i in range(self.numBranch):
            try:
                diag_Ymatrix[i,i] += 1/ complex(self.lineData[self.lineData.columns[2]][self.lineData.index[i]],
                                           self.lineData[self.lineData.columns[3]][self.lineData.index[i]])

            except:
                print("can't fine line's resistance and reactance")
                diag_Ymatrix[i,i] += 0

        return diag_Ymatrix

    def mkBadmittance_matrix(self):

        b_matrix = np.zeros((self.numBus, self.numBus), dtype=np.complex)

        for i in range(self.numBranch):
            #from bus에 1/2 값 넣어주기
            b_matrix[
                self.lineData[self.lineData.columns[0]][self.lineData.index[i]] - 1, self.lineData[self.lineData.columns[0]][self.lineData.index[i]] - 1] += complex(
                0, self.lineData[self.lineData.columns[4]][self.lineData.index[i]] / 2)

            # to bus에 1/2 값 넣어주기
            b_matrix[
                self.lineData[self.lineData.columns[1]][self.lineData.index[i]] - 1, self.lineData[self.lineData.columns[1]][self.lineData.index[i]] - 1] += complex(
                0, self.lineData[self.lineData.columns[4]][self.lineData.index[i]] / 2)

        return b_matrix

    def mkShuntCap_matrix(self):

        shuntCap_matrix = np.zeros((self.numBus,self.numBus), dtype=np.complex)

        for i in range(len(self.shuntCapData)):
            shuntCap_matrix[self.shuntCapData[self.shuntCapData.columns[0]][i]-1,self.shuntCapData[self.shuntCapData.columns[0]][i]-1]=complex(0,self.shuntCapData[self.shuntCapData.columns[1]][i])

        return shuntCap_matrix

    def mkTrans_matrix(self):

        trans_matrix = np.zeros((self.numBus,self.numBus), dtype=np.complex)

        for i in range(self.numTrans):
            # from bus 와 tap side bus 가 같은 경우; from bus가 tap side bus
            if self.transData[self.transData.columns[0]][i] == self.transData["Tap Side Bus"][i]:
                # From bus 행 from bus 열
                trans_matrix[self.transData[self.transData.columns[0]][i]-1][self.transData[self.transData.columns[0]][i]-1] =\
                1/complex(0,self.transData["Specified X (pu)"][i])/(abs(complex(self.transData["Tap a"][i])))**2

                # From bus 행 to bus 열
                trans_matrix[self.transData[self.transData.columns[0]][i]-1][self.transData[self.transData.columns[1]][i]-1] =\
                -1 * 1/complex(0,self.transData["Specified X (pu)"][i])/complex(self.transData["Tap a"][i]).conjugate()

                # to bus 행 from bus 열
                trans_matrix[self.transData[self.transData.columns[1]][i]-1][self.transData[self.transData.columns[0]][i]-1] =\
                -1 * 1/complex(0, self.transData["Specified X (pu)"][i]) / complex(self.transData["Tap a"][i])

                # to bus행 to bus 열
                trans_matrix[self.transData[self.transData.columns[1]][i]-1][self.transData[self.transData.columns[1]][i]-1] =\
                1/complex(0, self.transData["Specified X (pu)"][i])

            # from bus와 tap side bus가 다른 경우; to bus가 tap side bus
            else:
                #from bus 행 from bus 열
                trans_matrix[self.transData[self.transData.columns[1]][i]-1][self.transData[self.transData.columns[1]][i]-1] =\
                1/complex(0, self.transData["Specified X (pu)"][i]) / (abs(complex(self.transData["Tap a"][i]))) ** 2

                # From bus 행 to bus 열
                trans_matrix[self.transData[self.transData.columns[1]][i] - 1][self.transData[self.transData.columns[0]][i]-1] =\
                -1 * 1/complex(0, self.transData["Specified X (pu)"][i]) / complex(self.transData["Tap a"][i]).conjugate()

                # to bus 행 from bus 열
                trans_matrix[self.transData[self.transData.columns[0]][i] - 1][self.transData[self.transData.columns[1]][i] - 1] =\
                -1 * 1/complex(0, self.transData["Specified X (pu)"][i]) / complex(self.transData["Tap a"][i])

                # to bus행 to bus 열
                trans_matrix[self.transData[self.transData.columns[0]][i]-1][self.transData[self.transData.columns[0]][i]-1] =\
                1/complex(0, self.transData["Specified X (pu)"][i])

        return trans_matrix
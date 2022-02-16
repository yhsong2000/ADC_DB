import os
import io
import traceback
import PIL.Image as pilimg
import numpy as np
import struct
import cv2
import binascii
import time
import shutil
from collections import namedtuple
import concurrent.futures
# from Review.DefectClass import DefectList
# from Common.FTPmanager import FTP
# from Common.generalFunc import *

from enum import IntEnum
 
class ImageType(IntEnum):
    GRAY = 0
    COLOR = 1

class DefectClass:
    def __init__(self,labelList,binTList,binBList,binSList,typeList):
        self.topBinDict={}
        self.checkBincode = None
        self.labels = labelList
        self.bin_t = binTList
        self.bin_b = binBList
        self.bin_s = binSList
        self.types = typeList

        self.__check_bincode()
        self.__create_top_bin_dict()

    def __create_top_bin_dict(self):
        for idx,bincode in enumerate(self.bin_t):
            self.topBinDict[self.bin_t[idx]] =bincode
            self.topBinDict[self.bin_b[idx]] =bincode
            self.topBinDict[self.bin_s[idx]] =bincode

    def __check_bincode(self):
        for idx,type in enumerate(self.types):
            if 'check' == type.lower():
                self.checkBincode = self.bin_t[idx]

    def get_top_bincode(self,bincode):
        if bincode in self.topBinDict.keys():
            return self.topBinDict[bincode]
        return bincode

    def convert_to_checkbincode_if_checktype(self,bincode):
        if bincode not in self.topBinDict.keys():
            return  self.checkBincode
        return bincode

    def convert_vrsbincode(self,bincode):
        newBincode = self.get_top_bincode(bincode)
        return self.convert_to_checkbincode_if_checktype(newBincode)

    def convert_bincode_to_label(self,bincode):
        newBincode  = self.get_top_bincode(bincode)
        newBincode = self.convert_to_checkbincode_if_checktype(newBincode)
        idx = self.bin_t.index(newBincode)
        return self.labels[idx]

class VSImage():
    ''' vsimage file manager
    :param nType: vsimage type (ImageType.GRAY, ImageType.COLOR)
    '''
    def __init__(self,nType):
        self.__type = nType
        # self.ftp = FTP()
        self.resetParam()
        self.__MachineName = "SetToNone"

    def resetParam(self):
        self.StartOffset = 0
        self.ImageOffset = 0
        self.ImageWidth = 320
        self.ImageHeight = 240
        self.defectNum = 0
        self.defectInfo = []
        self.restInfo=[]
        self.Origin = []
        self.ImageNum = 0
        self.readFrom = 0
        self.bInProcess = False
        self.Barcode = None
        self.InspType = "Insp Type : "  
        self.Angle = "Angle 0.000000"
        # self.ftp.Reset()
        self.res=None
        self.outSize=224
        self.readyALL=None
        self.indexAll=None
        self.countIndex=0
        #self.__MachineName = None

    #strVSImageFile = "C:\\WISVision\\VSData\\Test.vs_Image"
    VScoord = namedtuple('VSDefect', ['RawImagePSR', 'RawImagePAD', 'RawImageAXS'])
    #GrayImage default
    VSIMAGE_HEADERSIZE = 14 #(4+1+1+4+4, 3int, 2byte)
    VSIMAGE_BLOCKSIZE = 28 #(4*7, 4float, 3int)

    ## Type 0 : Semi, Type 1 : PCB
    ## Type 0 : Gray, Type 1 : RGB
    nType = 0

    nPsrLength = 0
    nPadLength = 0
    nAxsLength = 0

    ImgFromVS = {}
    ImgAddressVSList = []
    ImgAddressVS  = {}

 

    def SetMachineName(self,name):
        if "V2" in name or "V4" in name:
            self.__MachineName = name
        else:
            self.__MachineName = "SetToNone"
        #print("machine name set to ",self.__MachineName)

    def GetMachineName(self):
        return self.__MachineName

    def ChangeMachineName(self):
        if "V2" in self.__MachineName:
            self.__MachineName = "V4"
            return True
        elif "V4" in self.__MachineName:
            self.__MachineName =  "SetToNone"
        return False

    def CheckCorrespondingV4(self,V2Path):
        if os.path.exists(V2Path.replace(self.__MachineName,self.__MachineName.replace("V2","V4")) ): ## V2 파일이 V4에도 있는지 확인
            print("CheckCorrespondingV4 Exist")
            return True
        else:
            print("NO CheckCorrespondingV4")
            self.__MachineName =  "SetToNone"
            return False    

    def GetDefectCode(self,index,defectCodeIndex=4):
        return int(self.defectInfo[index][defectCodeIndex])

    def ReadVSInfo(self,strFileName):
        self.defectInfo = []
        self.Origin = []
        self.restInfo=[]
        blockYRead=False
        with open(strFileName,'r') as vsFile:
            for line in vsFile:
                if blockYRead:
                    self.restInfo.append(line)
                else:
                    if line.split(" ")[0] == '':
                        temp = line.split(" ")
                        if temp[0] =='':
                            temp.pop(0)
                        self.defectInfo.append(temp)
                    elif line.split(" ")[0] == "Defect_Num":
                        self.defectNum = int(line.split(" ")[1].replace("\n",""))
                    elif line.split(" ")[0] == "BlockX":
                        self.BlockX = line
                    elif line.split(" ")[0] == "BlockY":
                        self.BlockY = line
                        blockYRead=True
                    elif line.split(" ")[0] == "Angle":
                        self.Angle  = line
                    elif line.split(" ")[0] == "Insp":
                        self.InspType  = line
                    elif line.split(" ")[0] == "Origin":
                        self.Origin.append(line)
                    elif line.split(" ")[0] == "Barcode":
                        self.Barcode = line
        if len(self.defectInfo[0])==1:
            self.defectInfo.pop(0)
           
    def DeleteDirIfEmpty(self,dir):
        tmpVsList = get_file_list(dir, getFullPath = False, extension = "")
        if len(tmpVsList) ==0:
            delete_folder(dir)

    def DeleteCompletedFolder(self,root,modelName):
        iter = True
        while iter:
            iter = False
            for dirpath, dirnames, filenames in os.walk(root):
                if len(dirnames) ==0 and len(filenames) ==0 and modelName in os.path.basename(dirpath):
                    delete_folder(dirpath)
                    iter = True
                         
    def WriteVSFile(self,strFileName):
        print("WriteVSFile - ",strFileName )
        if os.path.exists(strFileName) and not os.path.exists(strFileName.replace(".vs",".vs_backup")):  ## 기존 vs backup
            os.rename(strFileName,strFileName.replace(".vs",".vs_backup"))
        with open(strFileName,'w') as vsFile:
            vsFile.write(self.InspType)
            for l in self.Origin:
                vsFile.write(l)
            vsFile.write(self.Angle)
            if self.Barcode is not None:
                vsFile.write(self.Barcode)
            vsFile.write(self.defectNum)
            for l in self.defectInfo:
                vsFile.write(" "+' '.join(l))
            vsFile.write(self.BlockX+"\n")
            vsFile.write(self.BlockY)
            for l in self.restInfo:
                vsFile.write(l)
            vsFile.write("\n")

    def ReadVSImageInfo(self,strFileName):
        #self.ReadVSInfo(strFileName.replace(".vs_image",".vs"))
        # vs Image 읽기 (strFileName)
        with open(strFileName,'rb') as vsImage:
            self.strVSImageFile = strFileName
            if self.__type == ImageType.GRAY:
                ## VSIMAGE_HEADER
                s = vsImage.read(4) #ImageNum
                self.ImageNum = int.from_bytes(s,"little")
                s = vsImage.read(1) #temp
                temp = int.from_bytes(s,"little")
                s = vsImage.read(1) #temp
                temp = int.from_bytes(s,"little")
                s = vsImage.read(4)
                self.ImageWidth = int.from_bytes(s,"little")
                s = vsImage.read(4)
                self.ImageHeight = int.from_bytes(s,"little")

                self.VSIMAGE_HEADERSIZE = 14 #(4+1+1+4+4, 3int, 2byte)
                self.VSIMAGE_BLOCKSIZE = 28 #(4*7, 4float, 3int)

                self.StartOffset = self.VSIMAGE_HEADERSIZE \
                                    + (self.VSIMAGE_BLOCKSIZE * self.ImageNum)
                self.ImageOffset = self.ImageWidth*self.ImageHeight

            elif self.__type == ImageType.COLOR:
                ## VSIMAGE_HEADER
                s = vsImage.read(1) #ImageNum
                m_nBitCountPsr = int.from_bytes(s,"little")
                s = vsImage.read(1) #ImageNum
                m_nPadCountPsr = int.from_bytes(s,"little")
                s = vsImage.read(1) #ImageNum
                m_nAxsCountPsr = int.from_bytes(s,"little")

                s = vsImage.read(4) #ImageNum
                self.ImageNum = int.from_bytes(s,"little")

                s = vsImage.read(4)
                self.ImageWidth = int.from_bytes(s,"little")
                s = vsImage.read(4)
                self.ImageHeight = int.from_bytes(s,"little")

                self.VSIMAGE_HEADERSIZE = 15 #(1+1+1+4+4+4, 3int, 3byte)
                self.VSIMAGE_BLOCKSIZE = 40 #(4+4+4+4+8+8+8, 4float, 3(int*2))

                self.StartOffset = self.VSIMAGE_HEADERSIZE \
                                    + (self.VSIMAGE_BLOCKSIZE * self.ImageNum)
                self.ImageOffset = self.ImageWidth*self.ImageHeight

        self.PickAllVSImage()
        self.bInProcess=True
        self.readFrom = 0


    def PickAllVSImage(self):
        # VS의 모든 디펙을 읽어서 메모리 Dictionary에 저장
        with open(self.strVSImageFile,'rb') as vsImage:
            if self.__type == ImageType.GRAY:
                ## Read VSIMAGE_ImageBuffer
                VSIMAGE_HEADERSIZE = 14 #(4+1+1+4+4, 3int, 2byte)
                VSIMAGE_BLOCKSIZE = 28 #(4*7, 4float, 3int)

                self.ImgAddressVSList.clear()
                #Header 건너뛰고 읽기 시작해서
                vsImage.seek(self.VSIMAGE_HEADERSIZE)
                ImageCnt = 0
                self.StartOffset = self.VSIMAGE_HEADERSIZE \
                                   + (self.VSIMAGE_BLOCKSIZE * self.ImageNum)

                for ImageCnt in range(self.ImageNum):
                    ## Read VSIMAGE_ImageBuffer
                    self.ImageStartOffset = self.StartOffset \
                                            + (self.ImageOffset * ImageCnt)

                    self.ImgAddressVS = {"Index":ImageCnt,
                                         "ImgOffset":self.ImageStartOffset}

                    self.ImgAddressVSList.insert(ImageCnt,self.ImgAddressVS)

            elif self.__type == ImageType.COLOR:
                ## Read VSIMAGE_ImageBuffer
                self.VSIMAGE_HEADERSIZE = 15 #(1+1+1+4+4+4, 3int, 3byte)
                self.VSIMAGE_BLOCKSIZE = 40 #(4+4+4+4+8+8+8, 4float, 3(int*2))

                self.ImgAddressVSList.clear()
                #Header 건너뛰고 읽기 시작해서
                vsImage.seek(self.VSIMAGE_HEADERSIZE)
                #해당 위치 PSR,PAD,AXS 값 읽고 시작 좌표 찾아야 함
                ImageCnt = 0
                ImageStartOffset = self.VSIMAGE_HEADERSIZE \
                                   + (self.VSIMAGE_BLOCKSIZE * self.ImageNum)

                for ImageCnt in range(self.ImageNum):
                    #PSR,PAD,AXS 값 읽고
                    s = vsImage.read(4)
                    fLTPointX = struct.unpack('f',s)
                    s = vsImage.read(4)
                    fLTPointY = struct.unpack('f',s)
                    s = vsImage.read(4)
                    fRBPointX = struct.unpack('f',s)
                    s = vsImage.read(4)
                    fRBPointY = struct.unpack('f',s)

                    s = vsImage.read(8)
                    nPsrLength = int.from_bytes(s,"little")
                    s = vsImage.read(8)
                    nPadLength = int.from_bytes(s,"little")
                    s = vsImage.read(8)
                    nAxsLength = int.from_bytes(s,"little")

                    self.ImgAddressVS = {"Index":ImageCnt,
                                       "LTX":fLTPointX,
                                       "LTY":fLTPointY,
                                       "RBX":fRBPointX,
                                       "RBY":fRBPointY,
                                       "PSRLength":nPsrLength,
                                       "PADLength":nPadLength,
                                       "AXSLength":nAxsLength,
                                       "PSROffset":ImageStartOffset,
                                       "PADOffset":ImageStartOffset + nPsrLength,
                                       "AXSOffset":ImageStartOffset + nPsrLength
                                                   + nPadLength
                                        }

                    ImageStartOffset+=(nPsrLength+nPadLength+nAxsLength)
                    self.ImgAddressVSList.insert(ImageCnt,self.ImgAddressVS)

    def PickVSImageFromMemory(self,Index, outSize=None, normalize=True, centercrop_size=0):
        def Byte2Img(byte,outSize,normalize,centercrop_size):
            IMGMemory = io.BytesIO(byte)
            PILIMAGE = pilimg.open(IMGMemory)
            PILIMAGE = PILIMAGE.rotate(90)
            img =  np.array(PILIMAGE)
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            img = get_centercrop_img(img,centercrop_size)
            if outSize is not None:
                img = cv2.resize(img,(outSize,outSize)) 
            if np.max(img) > 1.0:
                img = img.astype(np.float32)
                img = img / 255.0

            return img
        if Index > self.ImageNum :
            return None,None,None
        # vs Image 읽기 (strFileName)
        with open(self.strVSImageFile, 'rb') as vsi:
            vsi.seek(0)
            if self.__type == ImageType.GRAY:
                vsi.seek(self.ImgAddressVSList[Index]["ImgOffset"])
                RawImage = vsi.read(int(self.ImageOffset))
                self.ImgFromVS = {"Index":Index,"Defect":RawImage }

                data = np.frombuffer(self.ImgFromVS["Defect"], dtype='uint8')
                ImageArray = np.reshape(data,(int(self.ImageHeight),-1))
                CurrentImage = pilimg.fromarray(ImageArray)
                img =  np.array(CurrentImage)
                img = get_centercrop_img(img,centercrop_size)
                if outSize is not None:
                    img = cv2.resize(img,(outSize,outSize))
                if normalize and np.max(img) > 1.0:
                    img = img.astype(np.float32)
                    img = img / 255.0
                return img

            elif self.__type == ImageType.COLOR:
                vsi.seek(self.ImgAddressVSList[Index]["PSROffset"])
                RawImagePSR = vsi.read(self.ImgAddressVSList[Index]["PSRLength"])
                vsi.seek(self.ImgAddressVSList[Index]["PADOffset"])
                RawImagePAD = vsi.read(self.ImgAddressVSList[Index]["PADLength"])
                vsi.seek(self.ImgAddressVSList[Index]["AXSOffset"])
                RawImageAXS = vsi.read(self.ImgAddressVSList[Index]["AXSLength"])


                psr = Byte2Img(RawImagePSR,outSize,normalize,centercrop_size)
                pad = Byte2Img(RawImagePAD,outSize,normalize,centercrop_size)
                axs = Byte2Img(RawImageAXS,outSize,normalize,centercrop_size)

                # ImgFromVS Dictionary에 각각 Byte 메모리로 저장함. numpy로 변환하면 됨
                self.ImgFromVS = {"Index":Index, "PSR":RawImagePSR,
                                  "PAD":RawImagePAD, "AXS":RawImageAXS }
                return   psr,pad,axs

    def SaveVSImageFromMemory(self,Index, savePath, saveName):
        def Byte2Save(byte,savePath,channelName):
            IMGMemory = io.BytesIO(byte)
            PILIMAGE = pilimg.open(IMGMemory)
            PILIMAGE = PILIMAGE.rotate(90)
            PILIMAGE.save(os.path.join(savePath,saveName+"_"+channelName+".jpg"))
           
        with open(self.strVSImageFile, 'rb') as vsi:

            vsi.seek(0)
            if self.__type == ImageType.GRAY:
                vsi.seek(self.ImgAddressVSList[Index]["ImgOffset"])
                RawImage = vsi.read(int(self.ImageOffset))
                self.ImgFromVS = {"Index":Index,"Defect":RawImage }

                data = np.frombuffer(self.ImgFromVS["Defect"], dtype='uint8')
                ImageArray = np.reshape(data,(int(self.ImageHeight),-1))
                CurrentImage = pilimg.fromarray(ImageArray)
                CurrentImage.save(savePath+".jpg")

            elif self.__type == ImageType.COLOR:
                vsi.seek(self.ImgAddressVSList[Index]["PSROffset"])
                RawImagePSR = vsi.read(self.ImgAddressVSList[Index]["PSRLength"])
                vsi.seek(self.ImgAddressVSList[Index]["PADOffset"])
                RawImagePAD = vsi.read(self.ImgAddressVSList[Index]["PADLength"])
                vsi.seek(self.ImgAddressVSList[Index]["AXSOffset"])
                RawImageAXS = vsi.read(self.ImgAddressVSList[Index]["AXSLength"])

                Byte2Save(RawImagePSR,savePath,"Psr")
                Byte2Save(RawImagePAD,savePath,"Pad")
                Byte2Save(RawImageAXS,savePath,"Axs")

    def setDefect(self,index,newDefectCode=None):
        if len(self.defectInfo) ==0:
            return
        if newDefectCode is None:
            newDefectCode =  self.defectInfo[index][4]
        self.defectInfo[index][-1] = self.defectInfo[index][-1].replace("\n","")
        self.defectInfo[index].append("A"+str(newDefectCode))
        self.defectInfo[index].append("C1")
        self.defectInfo[index].append("P0\n")

    def setOverkill(self,index,newDefectCode=None):
        if len(self.defectInfo) ==0:
            return
        if newDefectCode is None:
            newDefectCode =  self.defectInfo[index][4]
        self.defectInfo[index][-1] = self.defectInfo[index][-1].replace("\n","")
        self.defectInfo[index].append("A"+str(newDefectCode))
        self.defectInfo[index].append("C0")
        self.defectInfo[index].append("P1\n")

    def GetTensorALL(self, outSize=224):
        self.readFrom = 0
        #print("self.readFrom ",self.readFrom)
        self.res=np.zeros(shape=[self.ImageNum, outSize, outSize, 9])
        self.readyALL=np.zeros(shape=[self.ImageNum],dtype=np.bool)
        self.indexAll=np.zeros(shape=[self.ImageNum],dtype=np.int)
        self.countIndex=0
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            result = {executor.submit(self.get_image_by_index, idx, 9, outSize): idx for idx in range(self.ImageNum)}        
    
    def GetReadyTensor(self,readFrom,batchNum):
        if readFrom+batchNum > self.ImageNum:
            batchNum = self.ImageNum - readFrom
        if self.countIndex>batchNum:
            img2Send = self.res[readFrom:readFrom+batchNum,:,:,:]
            self.res[readFrom:readFrom+batchNum,:,:,:]=0
            return True, img2Send
        else:
            return False,None

    def GetTensor(self,readFrom,batchNum,outSize,classNum, channel, centercrop_size=0):
        if readFrom+batchNum > self.ImageNum:
            batchNum = self.ImageNum - readFrom
        self.res=np.zeros(shape=[batchNum, outSize, outSize, channel])
         
        self.readFrom = readFrom
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            result = {executor.submit(self.get_image_by_index, idx, channel, outSize, centercrop_size): idx for idx in range(batchNum)}

            #if defectCode == 19022042:
            #    pass
            #    ## 여기서 critical defect 처리
        self.readFrom = readFrom + batchNum
        return self.res

    def get_image_by_index(self,idx, channel, outSize=224, centercrop_size=0):  ## 
        if channel == 9:
            psr,pad,axs = self.PickVSImageFromMemory(Index = self.readFrom + idx, 
                                                     outSize = outSize, 
                                                     centercrop_size = centercrop_size)
            resImg = np.dstack((axs,pad,psr)).reshape([1, outSize, outSize,9])
        elif channel ==3:
            resImg = self.PickVSImageFromMemory(self.readFrom + idx, outSize, centercrop_size=centercrop_size)
            if len(resImg.shape) == 2 or resImg.shape[2] == 1:
                resImg = cv2.cvtColor(resImg,cv2.COLOR_GRAY2RGB)
        if self.readyALL is not None:
            self.readyALL[idx]=True
            #print("Ready : ",idx)
        if self.res is not None:
            self.res[idx,:,:,:]= resImg

        return resImg

    def SaveCurrentImg(self):
        if self.__type == ImageType.GRAY:
            #BMP
            data = np.frombuffer(self.ImgFromVS["Defect"], dtype='uint8')
            ImageArray = np.reshape(data,(int(self.ImageHeight),-1))
            ImgFileName = "{0:06d}_Defect.bmp".format(self.ImgFromVS["Index"])
            CurrentImage = pilimg.fromarray(ImageArray)
            CurrentImage.save(ImgFileName)


        elif self.__type == ImageType.COLOR:
            #jpeg(PNG)
            IMGMemory = io.BytesIO(self.ImgFromVS["PSR"])
            PILIMAGE = pilimg.open(IMGMemory)
            PILIMAGE = PILIMAGE.rotate(90)
            #Arr = np.array(PILIMAGE)
            ImgFileName = "1_{0:06d}_PSR.jpeg".format(self.ImgFromVS["Index"])
            PILIMAGE.save(ImgFileName, "PNG")
            PILIMAGE.close()

            IMGMemory = io.BytesIO(self.ImgFromVS["PAD"])
            PILIMAGE = pilimg.open(IMGMemory)
            PILIMAGE = PILIMAGE.rotate(90)
            ImgFileName = "2_{0:06d}_PAD.jpeg".format(self.ImgFromVS["Index"])
            PILIMAGE.save(ImgFileName, "PNG")
            PILIMAGE.close()
            
            IMGMemory = io.BytesIO(self.ImgFromVS["AXS"])
            PILIMAGE = pilimg.open(IMGMemory)
            PILIMAGE = PILIMAGE.rotate(90)
            ImgFileName = "3_{0:06d}_AXS.jpeg".format(self.ImgFromVS["Index"])
            PILIMAGE.save(ImgFileName, "PNG")
            PILIMAGE.close()

    def stack_defect_images(self, defect_indexlist, center_crop_ratio = 1, resize_ratio = 1):
        ''' stack image into ndarray and return 
        :param defect_indexlist: indeces of defects of interest.
        :return: ndarray (defect_num, width, height, depth)
        ''' 
        if len(defect_indexlist) == 0:
            return None
        
        if len(defect_indexlist) > self.ImageNum:
            defect_indexlist = [i for i in range(self.ImageNum)]
        nw = w = self.ImageWidth
        nh = h = self.ImageHeight
        d = 3
        if len(self.PickVSImageFromMemory(0).shape) == 2:
            d = 1
        if (center_crop_ratio > 1 or center_crop_ratio <= 0):
            center_crop_ratio = 1
        if (resize_ratio > 1 or resize_ratio <= 0):
            resize_ratio = 1

 
        nh = int(nh * resize_ratio * center_crop_ratio)
        nw = int(nw * resize_ratio * center_crop_ratio)
        #print(len(defect_indexlist),nh,nw,d)
        #print("h",h,"w",w)
        img = np.zeros((len(defect_indexlist),nh,nw,d)).astype(np.uint8)
        for i in defect_indexlist:
            temp_img =  (self.PickVSImageFromMemory(i,normalize = False)).reshape(h,w,d)
            if center_crop_ratio is not None:
                temp_img = centercrop_by_ratio(temp_img, center_crop_ratio)
            if resize_ratio is not None:
                temp_img = cv2.resize(temp_img,(0,0),fx=resize_ratio,fy=resize_ratio)
                temp_img = temp_img.reshape(nh,nw,d)
            img[i,:,:,:] = temp_img

        return img
 
# VS 데이터 구조체
class VSDefectData():
    def __init__(self):
        self.__keylist = []
        self.__data = {"index":[],
                       "defect_code":[],
                       "defect_size":[],
                       "defect_len":[],
                       "unit_x":[],
                       "unit_y":[],
                       "pos_x":[],
                       "pos_y":[],
                       "ADCcode":[],
                       "defect_critical":[],
                       "defect_pass":[]
                       }
                
    def _can_assign_new_val(self, key, param):
        if key in self.__keylist and param is None:
            return False
        if key not in self.__keylist and param is not None:
            return False
        return True

    def _can_assign_all(self, defect_len, unit_x, unit_y, pos_x, pos_y, 
                        ADCcode, defect_critical, defect_pass):
        if len(self.__keylist) == 0:
            return True
        if not self._can_assign_new_val("defect_len", defect_len):
            return False
        if not self._can_assign_new_val("unit_x", unit_x):
            return False
        if not self._can_assign_new_val("unit_y", unit_y):
            return False
        if not self._can_assign_new_val("pos_x", pos_x):
            return False
        if not self._can_assign_new_val("pos_y", pos_y):
            return False
        if not self._can_assign_new_val("ADCcode", ADCcode):
            return False
        if not self._can_assign_new_val("defect_critical", defect_critical):
            return False                                                                                                                
        if not self._can_assign_new_val("defect_pass", defect_pass):
            return False     
        return True      


    def _check_key_validity(self, index, defect_code, defect_size, 
                            defect_len, unit_x, unit_y, pos_x, pos_y, 
                            ADCcode, defect_critical, defect_pass):

        if not self._can_assign_all(defect_len, unit_x, unit_y, pos_x, pos_y, 
                                     ADCcode, defect_critical, defect_pass):
            print("Error, clear buffer if wish to push other values")
            return False

        if len(self.__keylist) == 0:
            self.__keylist.append("index")
            self.__keylist.append("defect_code")
            self.__keylist.append("defect_size")
            if defect_len is not None:
                self.__keylist.append("defect_len")
            if unit_x is not None:
                self.__keylist.append("unit_x")
            if unit_y is not None:
                self.__keylist.append("unit_y")
            if pos_x is not None:
                self.__keylist.append("pos_x")
            if pos_y is not None:
                self.__keylist.append("pos_y")
            if ADCcode is not None:
                self.__keylist.append("ADCcode")
            if defect_critical is not None:
                self.__keylist.append("defect_critical")
            if defect_pass is not None:
                self.__keylist.append("defect_pass")
        return True

    def push(self, index, defect_code, defect_size, defect_len = None, 
             unit_x = None, unit_y = None, pos_x = None, pos_y = None,
             ADCcode=None, defect_critical=None, defect_pass=None):

        def cast_float(val):
            if val is None:
                return val
            return float(val)

        def cast_int(val):
            if val is None:
                return val
            return int(val)

        if not self._check_key_validity(index, defect_code, defect_size,
                                 defect_len, unit_x, unit_y, pos_x, pos_y, 
                                 ADCcode, defect_critical, defect_pass):
            return False

        self.__data["index"].append(int(index))
        self.__data["defect_code"].append(int(defect_code))
        self.__data["defect_size"].append(float(defect_size))
        self.__data["defect_len"].append(cast_float(defect_len))
        self.__data["unit_x"].append(cast_int(unit_x))
        self.__data["unit_y"].append(cast_int(unit_y))
        self.__data["pos_x"].append(cast_float(pos_x))
        self.__data["pos_y"].append(cast_float(pos_y))
        self.__data["ADCcode"].append(ADCcode)
        self.__data["defect_critical"].append(defect_critical)
        self.__data["defect_pass"].append(defect_pass)

    def pop(self):
        if len(self.__data["index"]) == 0:
            return
        for key in self.__data.keys():
            self.__data[key].pop()
 
    def length(self):
        return len(self.__data["index"])

    def clear(self):
        self.__data = {key: [] for key in self.__data.keys()}

    def _check_index_validity(self,idx):
        if len(self.__data["index"]) < idx:
            raise Exception("Invalid Index") 
        return True

    def modify_ADCcode(self,idx,val):
        self._check_index_validity(idx)
        self.__data["ADCcode"][idx] = val

    def get_ADCcode(self, idx):
        self._check_index_validity(idx)
        return self.__data["ADCcode"][idx]

    def get_defect_info(self, idx):
        self._check_index_validity(idx)
        res=[]
        for key in self.__keylist:
            res.append(self.__data[key][idx])
        return (res)
   

if __name__ =='__main':
    from VSExctract import *
    vsPath = r"C:\Users\chan\Desktop\tt\autodir\J9K8-PASS1-ALL__S943KJ61J__00-01.vs"
    VSRGB = VSImage(ImageType.GRAY)
    # VSRGB.ImageWidth = 1280
    # VSRGB.ImageHeight = 960
    # VSRGB.ReadVSImageInfo(vsPath.replace(".vs",".vs_image"))
 
    # vsdata = VSData()
    # vsdata.ReadVSData(vsPath)
    
    # for i in range(vsdata.VSStack.length()):
    #     vsdata.VSStack.get_defect_info(i)

    VSRGB.ReadVSInfo(vsPath)

    VSRGB.defectInfo
    VSRGB.GetDefectCode(0)

    VSRGB.InspType
    VSRGB.Barcode
    #VSRGB.restInfo
    import numpy as np
    # res = np.zeros((8,h,w,1))
    # res.shape

    # res[0,:,:,:] = psr
    #VSRGB.WriteVSFile(r"C:\Users\chan\Downloads\temp.vs")
    psr = VSRGB.PickVSImageFromMemory(0)
    psr = cv2.cvtColor(psr,cv2.COLOR_GRAY2RGB)
    h,w = psr.shape
    psr = psr.reshape((h,w,1))
    psr.shape
    cv2.imshow("psr",psr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    VSRGB.ImageNum
    tensor = VSRGB.GetTensor(15,8,224,2,"psr,pad,axs")
    tensor.shape[0]
    h,v,c = psr.shape
    psr2 = psr.reshape([1,h,v,c])
    psr.shape
    psr2 = np.vstack((psr2,psr.reshape([1,h,v,c])))
    psr2.shape

    VSRGB.WriteVSFile(vsPath)

    # psr2 = cv2.imread(r"M:\TEST_DATA\ADC_STABILITY_TEST\PostProcessTest\1.TEST_DATA\TEST_image\KOR08MI081(R2)_1910080-95-0009-S02-C24_0_0\015_KOR08MI081(R2)__1910080-95-0009-S02-C24_Psr.jpeg")
    # axs2 = cv2.imread(r"M:\TEST_DATA\ADC_STABILITY_TEST\PostProcessTest\1.TEST_DATA\TEST_image\KOR08MI081(R2)_1910080-95-0009-S02-C24_0_0\015_KOR08MI081(R2)__1910080-95-0009-S02-C24_Axs.jpeg")
    # pad2 = cv2.imread(r"M:\TEST_DATA\ADC_STABILITY_TEST\PostProcessTest\1.TEST_DATA\TEST_image\KOR08MI081(R2)_1910080-95-0009-S02-C24_0_0\015_KOR08MI081(R2)__1910080-95-0009-S02-C24_Pad.jpeg")
    # psr2 = cv2.resize(psr2,(224,224)).astype(np.float)
    # axs2 = cv2.resize(psr2,(224,224)).astype(np.float)
    # pad2 = cv2.resize(psr2,(224,224)).astype(np.float)
    # psr2 /=255.0
    # axs2 /=255.0
    # pad2 /=255.0

    
    # VSRGB.SaveVSImageFromMemory(15,r"D:\WISVision\ADC\InspDB/tt")

    # psr3 = cv2.imread(r"D:\WISVision\ADC\InspDB\tt_Psr.jpg")
    # pad3 = cv2.imread(r"D:\WISVision\ADC\InspDB\tt_Pad.jpg")
    # axs3 = cv2.imread(r"D:\WISVision\ADC\InspDB\tt_Axs.jpg")
    # psr3 = cv2.resize(psr3,(224,224)).astype(np.float)
    # axs3 = cv2.resize(psr3,(224,224)).astype(np.float)
    # pad3 = cv2.resize(psr3,(224,224)).astype(np.float)
    # psr3 /=255.0
    # axs3 /=255.0
    # pad3 /=255.0

    # np.max(psr - psr3)*255
    # np.max(axs - axs3)*255
    # np.max(pad - pad3)*255
    # np.array_equal(psr,psr3)

 

    # for i in range(8):
    #     cv2.imshow("psr",tensor[i,:,:,0:3])
    #     cv2.imshow("pad",tensor[i,:,:,3:6])
    #     cv2.imshow("axs",tensor[i,:,:,6:9])
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

 
 

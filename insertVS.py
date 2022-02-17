import pandas as pd
from pandas.io import sql
import sqlalchemy as db
import pyodbc
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine,text
from VSExctract import *



class InsertVSData :

    def __init__(self,dbname,fpath) :

        # self.engine = self.pg_connect('root','1234',dbname,'localhost')

        self.vsimg = VSImage(ImageType.GRAY)
        self.vsimg.ReadVSInfo(fpath)        
        # print(VSRGB.defectInfo)
        # print(VSRGB.defectNum)
                
        # self.conn = self.engine.raw_connection()
        # self.df.to_sql('vs_table',self.engine,if_exists='replace')
        # self.strip_lv
        # self.unitY
        # self.unitX
        # self.posX
        # self.posY
        
        



    def excuteProcedure(self) :
        # self.cursor.callproc('pro_test','pine1-1')
        # self.conn.cursor().execute(text('call pro_test(:pine1-1)') )
        params = ['pine1-1']        
        self.conn.cursor().callproc('pro_test',params)        
        self.conn.commit()
        # results = list(cursor.fetchall())

        self.conn.close()            
            
            

    def pg_connect(self,user, password, db, host, port=3306):
        url = 'mysql://{}:{}@{}/{}'.format(user, password, host, db)
        return create_engine(url)
        




if __name__== '__main__' : 
    
    path = r'C:\Users\yhsong\Documents\pgm\pgm_db\data\VS\VS_M1V2_4AS0087B_J8283640101\4AS0087B_J8283640101-S02-C28\4AS0087B__J8283640101-0001-S02-C28.vs'
    dbtest = InsertVSData('dbtest',path)
    
        

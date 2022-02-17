import pandas as pd
from pandas.io import sql
import sqlalchemy as db
import pyodbc
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine,text
from VSExctract import *



class InsertVSData :

    def __init__(self,dbname,vsinfo_path) :

        self.engine = self.pg_connect('root','1234',dbname,'localhost')
        self.facility_name = {
            'M1V2' : 'pine1-1',
            'M1V4' : 'pine1-1',
            'M2V2' : 'pine1-2',
            'M2V4' : 'pine1-2',
            'M3V2' : 'pine2-1',
            'M3V4' : 'pine2-1',
            'M4V2' : 'pine2-2',
            'M4V4' : 'pine2-2',
            'M5V2' : 'unknown',
            'M5V4' : 'unknown',   
            'M6V2' : 'unknown',
            'M6V4' : 'unknown',
                            }

        # self.vsimg = VSImage(ImageType.GRAY)
        # self.vsimg.ReadVSInfo(vsinfo_path)        
        # print(VSRGB.defectInfo)
        # print(VSRGB.defectNum)
                
                
        # self.strip_lv
        # self.unitY
        # self.unitX
        # self.posX
        # self.posY
        
        self.df = pd.read_csv(vsinfo_path)
        # self.conn = self.engine.connect()
        self.machine=  self.facility_name[self.df['machine_name'].unique()[0]] if len(self.df['machine_name'].unique()) ==1 else 'unknown'
                    
        # self.conn = self.engine.raw_connection()
        # self.df.to_sql('test_table',self.engine,if_exists='replace')
        
        # self.excuteProcedure()


    def excuteProcedure(self) :
        # self.cursor.callproc('pro_test','pine1-1')
        # self.conn.cursor().execute(text('call pro_test(:pine1-1)') )
        
        params = [self.machine]        
        self.conn.cursor().callproc('pro_test',params)
        self.conn.commit()
        # results = list(cursor.fetchall())

        self.conn.close()            
            
            

    def pg_connect(self,user, password, db, host, port=3306):
        url = 'mysql://{}:{}@{}/{}'.format(user, password, host, db)
        return create_engine(url)
        


if __name__== '__main__' : 
    
    # path = r'C:\Users\yhsong\Documents\pgm\pgm_db\data\VS\VS_M1V2_4AS0087B_J8283640101\4AS0087B_J8283640101-S02-C28\4AS0087B__J8283640101-0001-S02-C28.vs'
    path = r'C:\Users\yhsong\Documents\pgm\pgm_db\data\VS\VS_M1V2_4AS0087B_J8283640101\4AS0087B_J8283640101-S02-C28\4AS0087B__J8283640101-0001-S02-C28.vs_info'
    dbtest = InsertVSData('adcdb',path)
    
        

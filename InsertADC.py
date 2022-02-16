import pandas as pd
from pandas.io import sql
from sqlalchemy import create_engine,text
import sqlalchemy as db
import pyodbc
import mysql.connector
from mysql.connector import Error

path =r'C:\Users\yhsong\Documents\pgm\pgm_db\data\VRS\VRS_M1V2_4AS0087B_J8283640101\4AS0087B_J8283640101-S02-C28\4AS0087B__J8283640101-0001-S02-C28.csv'


# print(df.head())
# # print(df['insp_light_r'][0])
# a= (df[['defect_code','detect_light_r','detect_light_g' ]].groupby('defect_code').sum())
# print(a['detect_light_g']) 

class DBTest() :
    def __init__(self,dbname,fpath) :    
        # self.engine = create_engine('mysql://root:1234@localhost/{}'.format(dbname))
        # df.to_sql('test_table',engine)        
        # conn = mysql.connector.connect(host = 'localhost',
        #  database= '{}'.format(dbname),
        #  user = 'root',
        #  password = '1234')
        self.engine = self.pg_connect('root','1234',dbname,'localhost')


        # self.cursor = conn.cursor()
        self.df = pd.read_csv(fpath)
        # self.conn = self.engine.connect()
        self.conn = self.engine.raw_connection()
        self.df.to_sql('test_table',self.engine,if_exists='replace')
        
        self.excuteProcedure()


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
        

    # def insertpoints(self):
    #     dbcol = ['defect_index','unit_x','unit_y','pos_x','pos_y','bump_size','new_size','defect_code','adc_id','strips_id','defect_size','defect_length','defect_width','defect_height']
    #     csvcol = ['defect_index','unit_x','unit_y','pos_x','pos_y','new_size','defect_code','defect_size','defect_length','defect_width','defect_height']
    #     tmp = self.df[csvcol]
    #     tmp['strips_ID'] = 0
    #     tmp['ADC_ID'] = 0
    #     tmp['defect_code_ID']= 0
    #     tmp['bump_size'] = 1000
    #     tmp.rename({'defect_length':'defect_len'},axis='columns',inplace=True)
    #     meta = db.MetaData()
    #     table = db.Table('points',meta,autoload=True,autoload_with=self.engine)
                
    #     print('table',table.columns.keys())
    #     tmp = tmp[['defect_index','unit_x','unit_y','pos_x','pos_y','bump_size','new_size','defect_code_ID','ADC_ID','strips_ID','defect_size','defect_len','defect_width','defect_height']]
    #     # print(tmp.head())
    #     # tmp.to_sql('test_table',)
    #     # q=db.insert(table).values(tmp)
    #     # self.conn.execute(q)
    #     # self.conn.close()
    #     print('col',tmp.columns)
        
        

if __name__== '__main__' : 
    dbtest = DBTest('dbtest',path)
    # dbtest.insertpoints()
        
        

        
        


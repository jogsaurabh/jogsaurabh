#from email import message
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

def create_dataset(df,table_name,comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        df.to_sql(table_name,sqliteConnection,if_exists='replace', index=True)
        message=("Data Set created Successfully")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO DSName
                          (DataSetName,company) 
                          VALUES (?,?);"""
        data_tuple = (table_name,comp_name)
        cursor.execute(sqlite_insert_with_param,data_tuple)
        sqliteConnection.commit()
        cursor.close()
        message=("Data Set Added Successfully")
        # Alter table to add  audit status
        cursor = sqliteConnection.cursor()
        cursor.execute(f"ALTER TABLE '{table_name}' ADD Status TEXT")
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message

def add_verification_criteria (Criteria,DsName,comp_name):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO DSCriteria
                          (Verification_Criteria,DSName,CompanyName) 
                          VALUES (?,?,?);"""
        data_tuple = (Criteria,DsName,comp_name)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        #st.info("Done3")
        query=f"SELECT Verification_Criteria from DSCriteria where DsName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
        message_verify=(df)
    except sqlite3.Error as error:
        message_verify=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_dsname(comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT DataSetName from DSName where company='{comp_name}'")
        DSNames = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        DSNames=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return DSNames

def get_dataset(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}' where Status Is NULL"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_verification(DSname,comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT Verification_Criteria from DSCriteria where DsName='{DSname}' AND CompanyName='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_analytical_review (review,DsName,comp_name):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        #table_name="AR_"+DsName
        sqlite_insert_with_param = f"""INSERT INTO Audit_AR
                          (Review,DataSetName,CompanyName,Created_on) 
                          VALUES (?,?,?,?);"""
        
        currentime=datetime.now()
        data_tuple = (review,DsName,comp_name,currentime)
        #st.info("Done2")
        
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        st.info("Review inserted")
        #get list of reviews
        query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
        reviews=(df)
    except sqlite3.Error as error:
        reviews=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return reviews

def insert_vouching(data_id,field,audit_value,remarks,DsName,comp_name):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        
        sqlite_insert_with_param = f"""INSERT INTO Audit_Queries
                          (Data_Id,Field,Audit_Value,Remarks,Audited_on,DataSetName,CompanyName) 
                          VALUES (?,?,?,?,?,?,?);"""
        currentime=datetime.now()
        data_tuple = (data_id,field,audit_value,remarks,currentime,DsName,comp_name)
        #st.info("Done2")
        
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        st.info("Vouching saved")
        cursor.close()
        vouching=("Vouching Data Saved....")
        #update DS table status
        #update_status=update_audit_status(data_id,DsName)
    except sqlite3.Error as error:
        vouching=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching


def update_audit_status(data_id,DsName):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE '{DsName}' SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Audit Status updated....")
    except sqlite3.Error as error:
        auditstatus=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

  
def get_queries(comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_Queries where CompanyName='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Queries", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df


def get_entire_dataset(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_verification(df):
    try:
            sqliteConnection = sqlite3.connect('autoaudit.db')
            cursor = sqliteConnection.cursor()
            df.to_sql("Audit_Queries",sqliteConnection,if_exists='append', index=False)
            message=("Data Set created Successfully")
            sqliteConnection.commit()
            cursor.close()
            message=("Data Set Added Successfully")
            sqliteConnection.commit()
            cursor.close()
    except sqlite3.Error as error:
            message=("Error while creating Data Set to sqlite", error)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return message

def get_ar(comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_AR where CompanyName='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
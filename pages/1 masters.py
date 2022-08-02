import streamlit as st
import pandas as pd
#from main import show_login_page
from functions import create_dataset,add_verification_criteria,get_dsname
import sqlite3
#from st_aggrid import AgGrid
comp_name="ABC"
        
st.title("Masters")
with st.sidebar.markdown("# Masters "):
    master_options = st.radio(
     'Masters- Dataset',
     ('Add New Data Set', 'Add Check List'))
    
    
if master_options=='Add New Data Set':
    st.title("Add New Data Set")
    st.info("Check that First Row contains colum Headings..")
    table_name=st.text_input("Enter Name of Data Set")
    uploaded_file = st.file_uploader("Upload a xlsx file",type='xlsx')
    
    if uploaded_file is not None:
        st.write(uploaded_file.name)
        filename=uploaded_file.name
        dataframe = pd.read_excel(uploaded_file)
        st.dataframe(dataframe)
        if st.button("Create Data Set"):
            if table_name:
                message=create_dataset(dataframe,table_name,comp_name)
                st.success(message)             
            else:
                st.error("Please enter Data Set Name")
else:
    st.title("Add Verification Check List for Data Set")
    #get list of ds_name for current company
    ds_names=get_dsname(comp_name)
    ds=st.selectbox("Select Data Set Name...",ds_names)
    ds_name=ds[0]
    st.write(ds_name)
    Chek_List=pd.DataFrame()
    with st.form("Verification Criteria",clear_on_submit=True):
        Crtiteria=st.text_area("Enter Verification Criteria")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            #add above to database
            Chek_List=add_verification_criteria(Crtiteria,ds_name,comp_name)
            
                        
    st.header("Verification Criteria")
    st.dataframe(Chek_List,width=1000)
    
    

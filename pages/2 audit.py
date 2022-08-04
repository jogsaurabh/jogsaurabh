#from cgitb import enable
#from distutils.command.build import build
#from sys import audit
from matplotlib.cbook import report_memory
import streamlit as st
from datetime import datetime
from functions import add_audit_verification, get_entire_dataset
from functions import get_dsname,get_dataset,get_verification,add_analytical_review,insert_vouching,update_audit_status
import pandas as pd
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
#from pandas_profiling import ProfileReport
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
import sqlite3
#st.write(f"User:-{st.session_state['username']}")
comp_name="ABC"
st.title("Audit")
with st.sidebar.markdown("# Audit"):
    dsname=st.selectbox("Select Data Set to Audit",get_dsname(comp_name))
    ds_name=dsname[0]
    #select dataset 
    df=get_dataset(ds_name)
    
tab1,tab2 =st.tabs(["   Vouching & Verification  ","   Analytical Review   "])
with tab1:
    st.header(ds_name)
    #st.dataframe(df)
    #builds a gridOptions dictionary using a GridOptionsBuilder instance.
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_pagination(enabled=True)
    builder.configure_selection(selection_mode="single",use_checkbox=True)
    #builder.configure_default_column(editable=True)
    go = builder.build()
    #uses the gridOptions dictionary to configure AgGrid behavior.
    grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
    #selelcted row to show in audit AGGrid
    selected = grid_response['selected_rows']
    #selected = grid_response['data']
    selected_df = pd.DataFrame(selected)
    #show Vouching AGGrid
    builder_Audit=GridOptionsBuilder.from_dataframe(selected_df)
    builder_Audit.configure_default_column(editable=True)
    go_audit = builder_Audit.build()
    st.subheader("Vouching...Double click to change & record if values are wrong.")
    audited=AgGrid(selected_df, gridOptions=go_audit,update_mode= GridUpdateMode.VALUE_CHANGED,height = 80,theme="blue")
    #st.text(audited["data"])
    audited_data=audited['data']
    aud_df=pd.DataFrame(audited_data)
    #Verification
    st.subheader("Verification...Check Verification if YES else keep Unchecked.")
    df_verif=get_verification(ds_name,comp_name)
    df_verif["Remarks"]=''
    builder_verif=GridOptionsBuilder.from_dataframe(df_verif)
    builder_verif.configure_selection(selection_mode="multiple",use_checkbox=True)
    builder_verif.configure_columns((['Remarks']),editable=True)
    go_verif=builder_verif.build()
    verif=AgGrid(df_verif, gridOptions=go_verif,update_mode=(GridUpdateMode.VALUE_CHANGED|GridUpdateMode.SELECTION_CHANGED),theme="blue")
    #st.write(verif["data"])
    all_verif=verif["data"]
    df_all_verif=pd.DataFrame(all_verif)
    #get DF for selected
    selected_verif=verif["selected_rows"]
    df_selected_ver=pd.DataFrame(selected_verif)
    #st.dataframe(df_selected_ver)
    #get df for not selected
    df_unselected_ver=pd.concat([df_all_verif,df_selected_ver]).drop_duplicates(keep=False)
    #st.dataframe(df_unselected_ver)
    #add colums to selected    
    df_selected_ver.rename(columns={'Verification_Criteria':'Verification'},inplace=True)
    df_selected_ver['DataSetName']=ds_name
    df_selected_ver['CompanyName']=comp_name
    df_selected_ver['Audit_Verification']="Yes"
    
     #add colums to Unselected    
    df_unselected_ver.rename(columns={'Verification_Criteria':'Verification'},inplace=True)
    df_unselected_ver['DataSetName']=ds_name
    df_unselected_ver['CompanyName']=comp_name
    df_unselected_ver['Audit_Verification']="No"  
            
    Submit_audit= st.button("Submit")
    if Submit_audit:
        #add  in database
        data_id=int(audited_data.iloc[0,0])
        for col in audited_data.columns:
            if audited_data[col].iloc[0] != selected_df[col].iloc[0]:
                #st.write(audited_data[col].iloc[0],col)
                audit_value=audited_data[col].iloc[0]
                accountin_value=selected_df[col].iloc[0]
                remarks=f"{col} as per Records is-{accountin_value};but as per Audit is-{audit_value}."
                #st.write(data_id,col,str(audit_value),ds_name,comp_name)
                vouching=insert_vouching(data_id,col,str(audit_value),remarks,ds_name,comp_name)
                st.info(vouching)
                
        currentime=datetime.now()
        #for verification =yes insert in Audit_queries
        df_selected_ver['Data_Id']=data_id
        df_selected_ver['Audit_Verification']="Yes"
        df_selected_ver['Audited_on']=currentime
        very=add_audit_verification(df_selected_ver)
        
        
        #for verification =No insert in Audit_queries
        df_unselected_ver['Data_Id']=data_id
        df_unselected_ver['Audit_Verification']="No"
        df_unselected_ver['Audited_on']=currentime
        very=add_audit_verification(df_unselected_ver)
        #st.dataframe(df_unselected_ver)
        #update audit status
        update_audit=update_audit_status(data_id,ds_name)
        #refresh AGGrid-update_mode=GridUpdateMode.MODEL_CHANGED also added with OR
        df = df.drop([0],inplace=True)
        st.info(update_audit)
        

with tab2:
    st.header(ds_name)
    #add Reveiew Remark
    #show in DF
    st.title("Add Review Comments for  Data Set...")
    # add verification list
    Reveiew=pd.DataFrame()
    cl1,cl2 =st.columns(2)
    with cl1:
        with st.form("Analytical Review Comments",clear_on_submit=True):
            Areview=st.text_area("Enter Comments")
            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                #add above to database
                Reveiew=add_analytical_review(Areview,ds_name,comp_name)
    
    with cl2:
        st.header("Analytical Review Comments")
        st.table(Reveiew)
        
    st.markdown("""---""")   
    col1,col2 =st.columns(2)
    ds=get_entire_dataset(ds_name)
    with col1:
        st.header("Data Set")
        st.dataframe(ds)
        
    with col2:
        ds=get_entire_dataset(ds_name)
        st.header("Stats Summary")
        st.dataframe(ds.describe())
   
    st.markdown("""---""")
    st.header("Generate Detailed Statistical Analysis Report")
    #Click to generate pandas profiling report
    if st.button("Generate Analytical Report"):
        with st.expander("Report on Data Set"):
            #profile = ProfileReport(df, title="Data Profiling Report")
            #ProfileReport(profile)
            pr = df.profile_report()
            st_profile_report(pr)
            
    
        
    
    
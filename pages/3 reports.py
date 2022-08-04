#from turtle import color

import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
from functions import get_queries,get_dsname,get_entire_dataset,get_ar
st.set_page_config(page_title="Audit Dashboard", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Audiit Dashboard")
st.markdown("##")
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

comp_name="ABC"
#Get entire audit data set including Verification= yes
df_queries=get_queries(comp_name)
#Remove verification= Yes & keep only No
df_queries=df_queries[(df_queries['Audit_Verification']=='No') | (df_queries['Audit_Value'].notnull() )]
ds_names=get_dsname(comp_name)

tab1,tab2 =st.tabs(["Queries by Data Set ","   All Queries  "])
with tab1:
    
    # ---- SIDEBAR ----
    st.sidebar.header("Please Selec Data Set:")
    ds=st.sidebar.selectbox("Get Queries for..",ds_names)
    ds_name=ds[0]
    st.title(ds_name)

    #get queries for selected Dataset
    df_selection = df_queries.query(
        "DataSetName == @ds_name"
    )
    df_DS=get_entire_dataset(ds_name)
    #get only Audited DS
    df_DS_Audited=df_DS.query("Status=='Audited'")
    #merge DS with Queries to get Querysheet
    df_DS_querysheet=pd.merge(df_DS_Audited,df_selection,how="left",left_on="index",right_on="Data_Id")
    #QuerySheet for Vouching
    df_DS_querysheet_Vouching=df_DS_querysheet.drop(['Verification','Audit_Verification'],axis=1)
    df_DS_querysheet_Vouching=df_DS_querysheet_Vouching.dropna(subset=['Field'])
    #QuerySheet for Verification
    df_DS_querysheet_Verification=df_DS_querysheet.drop(['Field','Audit_Value'],axis=1)
    df_DS_querysheet_Verification=df_DS_querysheet_Verification.dropna(subset=['Verification'])
    # TOP KPI's
    total_transactions = int(df_DS[df_DS.columns[0]].count())
    audited_transactions = int(df_DS["Status"].count())
    total_queries = int(df_selection[df_selection.columns[0]].count())
    #show KPIs
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Total Transactions:",)
        st.subheader(f"{total_transactions}")
    with middle_column:
        st.subheader("Transactions Audited:")
        st.subheader(f"{audited_transactions}")
    with right_column:
        st.subheader("Total Queries:")
        st.subheader(f"{total_queries}")

    st.markdown("""---""")
    #Chart for Vouching Queries by Type

    vouching_queries = (
        df_selection.groupby(by=["Field"]).count()
    )

    fig_vouching_queries = px.bar(
        vouching_queries,
        x="Audit_Value",
        y=vouching_queries.index,
        orientation="h",
        title="<b>Vouching Queries by Mismatch Type</b>",
        #color_discrete_sequence=["#0083B8"] * len(vouching_queries),
        template="plotly_white",text_auto=True
    )
    fig_vouching_queries.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    #Chart for Verification Queries by Type

    verification_queries = (
        df_selection.groupby(by=["Verification"]).count()
    )

    fig_verification_queries = px.bar(
        verification_queries,
        x="Audit_Verification",
        y=verification_queries.index,
        orientation="h",
        title="<b>Verification Queries by Mismatch Type</b>",
        color_discrete_sequence=["#0083B8"] * len(verification_queries),
        template="plotly_white",text_auto=True
    )
    fig_verification_queries.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    #show charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_vouching_queries,use_container_width=True)
        st.markdown("""---""")
        st.subheader("List of Vouching Queries")
        
        #st.dataframe(df_DS_querysheet_Vouching.style.set_properties(**{'color':'red'},subset=['Field','Audit_Value'])
        #)
        csv=df_DS_querysheet_Vouching.to_csv().encode('utf-8')
        
        builder = GridOptionsBuilder.from_dataframe(df_DS_querysheet_Vouching)
        builder.configure_column('Field',cellStyle={'color': 'red'})
        builder.configure_column('Audit_Value',cellStyle={'color': 'red'})
        builder.configure_column('Verification',cellStyle={'color': 'red'})
        builder.configure_column('Audit_Verification',cellStyle={'color': 'red'})
        builder.configure_column('Remarks',cellStyle={'color': 'red'})
        go = builder.build()
        #uses the gridOptions dictionary to configure AgGrid behavior.
        grid_response=AgGrid(df_DS_querysheet_Vouching, gridOptions=go,theme="blue")
        st.download_button("Download csv file",csv,f"{ds_name}.csv")
        
    with col2:
        st.plotly_chart(fig_verification_queries,use_container_width=True)
        st.markdown("""---""")
        st.subheader("List of Verification Queries")
    
        #st.dataframe(df_DS_querysheet_Verification.style.set_properties(**{'color':'red'},subset=['Verification','Audit_Verification'])
        #)
        csv=df_DS_querysheet_Verification.to_csv().encode('utf-8')
        builder = GridOptionsBuilder.from_dataframe(df_DS_querysheet_Verification)
        builder.configure_column('Field',cellStyle={'color': 'red'})
        builder.configure_column('Audit_Value',cellStyle={'color': 'red'})
        builder.configure_column('Verification',cellStyle={'color': 'red'})
        builder.configure_column('Audit_Verification',cellStyle={'color': 'red'})
        builder.configure_column('Remarks',cellStyle={'color': 'red'})
        go = builder.build()
        #uses the gridOptions dictionary to configure AgGrid behavior.
        grid_response=AgGrid(df_DS_querysheet_Verification, gridOptions=go,theme="blue")
        st.download_button("Download csv file",csv,f"{ds_name}.csv")
        
    #left_column.plotly_chart(fig_vouching_queries,use_container_width=True)
    #right_column.plotly_chart(fig_verification_queries,use_container_width=True)
    #st.dataframe(df_queries)
    #st.dataframe(df_selection)
    #st.dataframe(df_DS_Audited)
    #st.dataframe(df_DS_querysheet)


with tab2:
    st.header(comp_name)
    df_queries.rename(columns={'Field':'Vouching'},inplace=True)
    df_queries_groupby=df_queries.groupby(['DataSetName'])['Vouching','Verification'].count()
    st.header("Summary of Audit Queries")
    st.dataframe(df_queries_groupby.style.set_properties(**{'color':'red'},subset=['Vouching','Verification']))
    
    
    st.header('Query List by Transaction')
    
    #df_queries=pd.merge(df_queries,df_selection,how="left",left_on="Data_Id",right_on="index")
    builder = GridOptionsBuilder.from_dataframe(df_DS_querysheet)
    builder.configure_column('Field',cellStyle={'color': 'red'})
    builder.configure_column('Audit_Value',cellStyle={'color': 'red'})
    builder.configure_column('Verification',cellStyle={'color': 'red'})
    builder.configure_column('Audit_Verification',cellStyle={'color': 'red'})
    builder.configure_column('Remarks',cellStyle={'color': 'red'})
    go = builder.build()
    #uses the gridOptions dictionary to configure AgGrid behavior.
    grid_response=AgGrid(df_DS_querysheet, gridOptions=go,theme="blue")
    csv=df_DS_querysheet.to_csv().encode('utf-8')
    st.download_button("Download csv file",csv,f"{ds_name}.csv")
    #list of AReview
    st.header('Analytical Review- Comments')
    ds_ar=get_ar(comp_name)
    builder = GridOptionsBuilder.from_dataframe(ds_ar)
    
    builder.configure_column('Review',cellStyle={'color': 'red'})
    go = builder.build()
    #uses the gridOptions dictionary to configure AgGrid behavior.
    grid_response=AgGrid(ds_ar, gridOptions=go,theme="blue")
    csv=ds_ar.to_csv().encode('utf-8')
    st.download_button("Download csv file",csv,f"{ds_name}.csv")
    
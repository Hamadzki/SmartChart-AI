import pandas as pd
from pandasai import SmartDataframe
# from pandasai import PandasAI
from pandasai.llm import GooglePalm
import os
import streamlit as st 
from dotenv import load_dotenv
import google.generativeai as genai
import plotly.express as px
import regex as re
from langchain_community.llms import Ollama

# upload the file
load_dotenv()

#page steup
# st.set_page_config(layout='wide')

# setting up the llm for identifying the query is for analyzing or for transformation
prompts = ["""you are a pytohn expert developer for data manipulation and for each question you return the python code only nothing other than that dont even write python keyword
        to solve that question for example if the question is 'rename the column name ctaegory to classes ' then your answer should be 
          'df.rename(columns = {'category':'classes'},inplace=True)' """,
        
         """you are the expert to categorize the type of query. you will be given a query you have to identify the query is for transformation, analysing, visualisation or for the 'Others'
        for example if a query is related to modify the data like renaming,filling,changing etc these will be categorise as 'processing' and if the query is informational like asking for'the counts
          max, min , average or any kind of information about the data frame or table or column' then this will be cateogrize as 'analysing' and if the query is related to data visualisation 
          like plot charts,visualise etc then this category will be 'visualising' and if the query is not among these three then categorize that as 'others' you have to return only 'processing, analysing, visualising , others'
           in small letters. the others should be the last priority""",
          
           """you will be given a string in which there will be a task task you just have to capture the intention and return a single line text
          that the task is completed,successfully changed, etc into a text. or if you will not be able to catch then simply write Succefully executed""",
# analyse fast for you          
          """you are a chatbot and your name is 'affy' you are developed by 'Hammad Zaki' and you can clean and analys the data, 
          understand the users question and reply shortly as per your convinient and ask the user shortly how can I help
          and don't use 'surely' and 'sure' keyword just reply normally""",
          
           """write the python code only for creating new dataframe name as temp_df as per the requirmetn of visualisatin then for ploting use plotly.express as px and don't save in any variable
          ,take the column name as per the query if in the query it is small letters then take the column name in small letters if its capital then take capital, all packages are already import so dont import any package just write the two lines of code first is 
          for manipulating data second is for plotting. apart from this strictly dont include any extra text and comments I need 
          the reponse only codes dont even write python at beginning""",
          
          """write the python code only for visualisatin and for ploting use plotly.express as px and don't save in any variable and wrap it inside st.plotly_chart().
          by default your data or dataframe will be chart_df. take the column name in lower case, all packages are already import so dont import any package just write the one lines of code and 
          strictly dont include any extra text like comments.Example:'plot a kde plot for adults column' then your result will be like:'st.plotly_chart(px.histogram(df, x='adults', marginal='kde', title='KDE Plot for Adults Column'))'. I need the reponse only code dont even write python at beginning"""]

question = ""

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='generative-ai-creds.json'
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# llm = GooglePalm(api_key=os.getenv("GOOGLE_API_KEY"))
llm = Ollama(model="llama3.1")

def identify_query_type(prompt):
    response = model.generate_content([prompts[1],prompt])
    return response.text

#setting up the pandas ai for the response for analyzing the data
def chat_with_csv(df,prompt):

    smart_df = SmartDataframe(df, config={"llm": llm})
    result = smart_df.chat(prompt)
    print(result)
    return result

#setting up the pandas ai for transofrming the data
def transform_csv(prompt):
    response = model.generate_content([prompts[0],prompt])
    resp = response.text
    exec(resp)
    chart_df = df.copy()
    csv_file = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="Download Preprocessed Data", data=csv_file, file_name='preprocessed_data.csv', key="download_button")

def resp_message(prompt):
    response = model.generate_content([prompts[2],prompt])
    resp = response.text
    return resp

# setting the page
# st.set_page_config(layout='wide')
st.title("Chat with Affy")
# input_csv = st.file_uploader("Upload your CSV file", type=['csv'])

input_csv = st.file_uploader("Upload your CSV file")

#converting csv to the df and displaying it
if input_csv:
    st.success("CSV Uploaded Successfully")
    df = pd.read_csv(input_csv)
    chart_df = df.copy()
    st.dataframe(df, use_container_width=True)
    # chart = "st.line_chart(data=df, x='hotel', y='lead_time')"
    # chart = "st.bar_chart(df.set_index('hotel')['lead_time'])"
    # fig = "px.box(df, x='hotel', y='lead_time', title='Lead Time Distribution by Hotel')"
    # chart = f"st.plotly_chart({fig})"
    # exec(chart)
    # csv_file = df.to_csv(index=False).encode('utf-8')
    # st.sidebar.download_button(label="Download Preprocessed Data", data=csv_file, file_name='preprocessed_data.csv', key="download_button")

# intinalizing the session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# print all the message as per user and assistant
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

table_status = st.sidebar.radio('Do you want to see the table in between chats', ['Yes', 'No'])
# append the content and the user 
# with col2:
prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message('user'):
        st.markdown(f"{prompt}")
    st.session_state.messages.append({"role":"user","content":prompt})

    query_type = identify_query_type(prompt)
    # st.markdown(query_type)
    if query_type == 'analysing':
        resp = chat_with_csv(df,prompt)
        with st.chat_message('assistant'):
            st.markdown(resp)
        st.session_state.messages.append({"role":"assistant","content":resp})
    elif query_type == 'processing':
        transform_csv(prompt)
        resp = resp_message(prompt)
        with st.chat_message('assistant'):
            st.markdown(resp)
        st.session_state.messages.append({"role":"assistant","content":resp})
        if table_status == "Yes":
            st.dataframe(df, use_container_width=True)
    elif query_type == 'visualising':
        # resp = model.generate_content([prompts[4],prompt]).text
        # b = re.sub("`","",resp)
        # b = re.sub("python","",b)
        # t_df = str(b.split('\n')[0])
        # exec(t_df)
        # st.dataframe(temp_df, use_container_width=True)
        # fig = b.split('\n')[1]
        # chart = f"st.plotly_chart({fig})"
        resp = model.generate_content([prompts[5],prompt]).text
        exec(resp)
    elif query_type == 'others':
        resp = model.generate_content([prompts[3],prompt]).text
        with st.chat_message('assistant'):
            st.markdown(resp)
        st.session_state.messages.append({"role":"assistant","content":resp})
        # st.write("Not able to understand your query, please re-write it")
        # st.write(query_type)



# if table_status=='No':
#     st.info('we will not show you the table between the chat')
# elif table_status=='Yes':
#     st.info('we will show you the table between the chat')


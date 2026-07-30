import streamlit as st
# lets import the chatbot object form the langgraph here
from Langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
# for automating the threadid
import uuid

# *************************************************utility_function***********************************
# thread_id_generating_function
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

# we will create a new chat with new threadid
def reset_chat():
    thread_id = generate_thread_id() # generating new thread
    st.session_state['thread_id'] = thread_id   #stroing thread in session state
    add_thread(st.session_state['thread_id'])  # thread is also getting reset
    st.session_state['message_history'] = [] # initialing message history as new
    
# adding the chat threads innto the chat_thread_list
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)
        
# for getting the conversation 
def load_conversation(thread_id):
    return chatbot.get_state(config={"configurable": {"thread_id": thread_id}}).values['messages']

# ***************************************************SESSION MEMORY***********************************
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]  # session state a dictionary  

# adding thread_id in session
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# list to store the thread ids
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = []

# calling with thread id
add_thread(st.session_state['thread_id'])


# ***************************************************slidebar UI*************************************

st.sidebar.title("Langgraph-Chatbot")

if st.sidebar.button("New-chat"):
    reset_chat()

st.sidebar.header("My conversation")

for thread_id in st.session_state['chat_thread'][::-1]:
    if st.sidebar.button(str(thread_id)): # loading a thread inside a button
        st.session_state['thread_id'] = thread_id  #current thread id in the session
        messages = load_conversation(thread_id) #we will get list of messages
        
        # now the problem is that we extracted is bigger and not in the form that can be stored by message_history
        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            
            temp_messages.append({'role': role, 'content': msg.content}) 
            
        st.session_state["message_history"] = temp_messages # saving it into the session history

#***************************************************Main UI*******************************************
# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("type here")

if user_input:
    # first append in history
    st.session_state['message_history'].append({'role':'user', 'content': user_input})
    with st.chat_message("user"):
        st.text(user_input)
        
    # configure:
    config1 = {"configurable": {"thread_id": st.session_state['thread_id']}} 
    
    # invkoing the chatbot object
    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    
    # ai_message = response['messages'][-1].content
    
    # first append in history
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config = config1,
                stream_mode="messages"
            )
        )
    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
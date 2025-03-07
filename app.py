import streamlit as st
import preprocessor,helper
import sentiment as s
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image
import math
st.set_page_config(page_title="WhatsApp Chat Analyzer",layout="wide",initial_sidebar_state="expanded")
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

mobile="Android"
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor.preprocess(data,mobile)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    # user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        progress_num=0
        num_messages, words, num_media_messages, num_links,df = helper.fetch_stats(selected_user,df)
        st.title("Overall Statistics")

        # divide_equally for progress bar
        def divide_equally(num):
            if num <= 0:
                return np.array([])
            else:
                arr = np.linspace(0, num, 100, dtype=int)
                return arr


        result = divide_equally(num_messages)
        if num_messages>500:
            progress_text = "This may take a While"
        else:
            progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        try:
            df.drop(["sentiment"],axis=1)
        except:
            pass
        df['sentiment'] = None
        df['sentiment_word']=None
        def sentiment_word(nm):
            if nm==1:
                return "Very negative"
            if nm==2:
                return "Negative"
            if nm==3:
                return "Netural"
            if nm==4:
                return "Positive"
            else:
                return "Very positive"
        df.index = range(0, df.shape[0])
        # st.text(df.shape)
        for i in df.index:
            if i in result:
                progress_num+=1
                my_bar.progress(progress_num, text=progress_text)
            df['sentiment'][i]=s.sentiment_score(df['message'][i][:512])
            df['sentiment_word'][i]=sentiment_word(df['sentiment'][i])
        my_bar.progress(100,text=progress_text)
        b = 0
        for sent in list(df['sentiment']):
            b += sent
        sentiment_total=0
        if len(list(df['sentiment']))>0:
            if b/(len(list(df['sentiment'])))%1>0.5:
                sentiment_total = math.ceil(b/(len(list(df['sentiment']))))
            else:
                sentiment_total = math.floor(b / (len(list(df['sentiment']))))


        col1, col2, col3, col4,col5 = st.columns(5)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)
        with col5:
            st.header("Sentiment of chat")
            st.title(sentiment_word(sentiment_total))
        #Sentiment Analysis
        st.header("Sentiment Analysis")
        senti = helper.sentiment_analytics(selected_user, df)
        fig, ax = plt.subplots()
        labels=list(senti.index)
        color_dict = {'Negative': 'crimson', 'Netural': 'blue', 'Very positive': 'green', 'Positive': 'yellow', 'Very negative': 'red'}

        # Define a list of colors for each bar based on the label
        colors = [color_dict[label] if label in color_dict else 'gray' for label in labels]

        ax.bar(labels, senti.values, color=colors,edgecolor='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        try:
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user,df)
            fig,ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)
        except:
            pass
        # most common words
        try:
            most_common_df = helper.most_common_words(selected_user,df)

            fig,ax = plt.subplots()

            ax.barh(most_common_df[0],most_common_df[1])
            plt.xticks(rotation='vertical')

            st.title('Most commmon words')
            st.pyplot(fig)
        except:
            pass

        # emoji analysis
        try:
            emoji_df = helper.emoji_helper(selected_user,df)
            st.title("Emoji Analysis")

            col1,col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                import warnings
                warnings.filterwarnings("ignore", category=UserWarning)
                fig,ax = plt.subplots()
                ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
                st.pyplot(fig)
        except:
            pass
#images
st.sidebar.title("How to download the chat")
if st.sidebar.button("Know about it"):
    image = Image.open('step1.jpeg')
    st.title("Step - 1")
    st.image(image)
    image = Image.open('step2.jpeg')
    st.title("Step - 2")
    st.image(image)
    image = Image.open('step3.jpeg')
    st.title("Step - 3")
    st.image(image)
    image = Image.open('step4.jpeg')
    st.title("Step - 4")
    st.image(image)
    image = Image.open('step5.jpeg')
    st.title("Step - 5")
    st.image(image)
    image = Image.open('step6.jpeg')
    st.title("Step - 6")
    st.image(image)












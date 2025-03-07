import streamlit as st
import re
import pandas as pd
from datetime import datetime


def preprocess(data,mobile="Android"):
    if ("AM" in data[7:21])or("PM" in data[7:21])or("pm" in data[7:21])or("am" in data[7:21]):
        gh=12
        print("12")
        if mobile=="Android":
            mb="android"
            if ("AM" in data[7:21])or("PM" in data[7:21]):
                pattern = '\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s(?:AM|PM)\s-\s'
            else:
                pattern = '\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s(?:am|pm)\s-\s'
        if mobile=="Iphone":
            mb="iphone"
            pattern='[\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}:\d{1,2}\s(?:AM|PM)]\s'
    else:
        gh=24
        print("24")
        if mobile == "Android":
            mb = "android"
            pattern = '\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{2}\s-\s'
        if mobile == "Iphone":
            mb = "iphone"
            pattern = '[\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}:\d{1,2}]\s'
    print(pattern)
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    print(messages,dates)
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert message_date type
    def convert24(time,mb="android"):
        time = time.split(",")
        # Parse the time string into a datetime object
        if mb=="iphone":
            t = datetime.strptime(time[1].strip(" -"), '%I:%M:%S %p')
        else:
            t = datetime.strptime(time[1].strip(" -"), '%I:%M %p')

        # Format the datetime object into a 24-hour time string
        ta = time[0] + "," + t.strftime('%H:%M')
        # st.text(ta)#17/04/23,19:20
        # print(ta)
        return ta
    if gh==12:
        if mb=="android":
            df['message_date'] = df['message_date'].apply(lambda x: convert24(x))
            try:
                df["message_date"] = pd.to_datetime(df["message_date"], format="%d/%m/%y,%H:%M")
            except:
                df["message_date"] = pd.to_datetime(df["message_date"], format="%m/%d/%y,%H:%M")

        if mb=="iphone":
            df['message_date'] = df['message_date'].apply(lambda x: convert24(x,mb))
            df["message_date"] = pd.to_datetime(df["message_date"], format="%d/%m/%y,%H:%M")
    else:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    df.drop(columns=['user_message'], inplace=True)
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
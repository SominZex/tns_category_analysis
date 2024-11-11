import pandas as pd
import streamlit as st

def load_data(uploaded_file):
    data = pd.read_csv(uploaded_file)
    data['orderDate'] = pd.to_datetime(data['orderDate'], errors='coerce', dayfirst=True)
    data['time'] = data['time'].apply(parse_time_dynamic)
    return data

def parse_time_dynamic(time_str):
    try:
        return pd.to_datetime(time_str, format='%H:%M:%S.%fZ').time()
    except ValueError:
        try:
            return pd.to_datetime(time_str, format='%H:%M:%S').time()
        except ValueError:
            try:
                return pd.to_datetime(time_str, format='%H:%M').time()
            except ValueError:
                return None

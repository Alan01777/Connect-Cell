import streamlit as st
import pandas as pd 
from dateutil.relativedelta import relativedelta

class DateFilter:
    def __init__(self, df, date_column):
        self.df = df
        self.date_column = date_column

    def filter_by_date(self):
        self.df[self.date_column] = pd.to_datetime(self.df[self.date_column], format="%d/%m/%Y")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Selecione a data inicial",
                min_value=self.df[self.date_column].min().date() - relativedelta(years=1),
                max_value=self.df[self.date_column].max().date() + relativedelta(years=1),
                value=self.df[self.date_column].min().date(), 
                format="DD/MM/YYYY",
            )
        with col2:
            end_date = st.date_input(
                "Selecione a data final",
                min_value=self.df[self.date_column].min().date() - relativedelta(years=1),
                max_value=self.df[self.date_column].max().date() + relativedelta(years=1),
                value=self.df[self.date_column].max().date(),
                format="DD/MM/YYYY",
            )

        df_filtered = self.df[
            (self.df[self.date_column].dt.date >= start_date) & (self.df[self.date_column].dt.date <= end_date)
        ]

        return df_filtered
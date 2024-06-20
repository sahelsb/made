import pandas as pd
from sqlalchemy import create_engine
import logging as log
import requests
from io import BytesIO
from zipfile import ZipFile
import os


class DataPipeline:
    
    def __init__(self, air_url, temperature_url):
        self.air_url = air_url
        self.temperature_url = temperature_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)+\
            Chrome/58.0.3029.110 Safari/537.3'}
        
    def extract_temperature_data(self):
        try:
            # Extract temperature data
            response = requests.get(self.temperature_url, headers=self.headers)
            data = BytesIO(response.content)

            with ZipFile(data) as zip_file:
                zip_file_list = zip_file.namelist()
                # Extract first csv file in the ZIP file
                first_file = zip_file_list[0]
                with zip_file.open(first_file) as first_file:
                    df = pd.read_csv(first_file, encoding="latin1")
            return df
        except Exception as e:
            log.error(f"Error extracting data: {e}")


    def extract_air_data(self):
        try:
            # Extract air_quality data
            response = requests.get(self.air_url, headers=self.headers)
            data = BytesIO(response.content)
            usecols = ['iso3', 'country_name', 'city', 'year', 'version',
                    'pm10_concentration', 'pm25_concentration', 'no2_concentration',
                    'type_of_stations', 'population']
            df = pd.read_excel(data, engine="openpyxl",
                            usecols=usecols, sheet_name="Update 2024 (V6.1)")
            return df
        except Exception as e:
            log.error(f"Error extracting data: {e}")

    def transform_air_data(self, df):
        # Rename column to representatiove names
        df = df.rename(columns={"iso3": "Code", "country_name": "Country", "city": "City", "year": "Year",
                       "pm10_concentration": "PM10", "pm25_concentration": "PM25", "no2_concentration": "NO2"})
        # Drop not in scope countries
        selected_countries = ['Spain', 'Germany', 'Switzerland', 'Denmark', 'Norway', 'Belgium', 
                              'Italy', 'France', 'Sweden', 'Netherlands (Kingdom of the)', 'Luxembourg']
        df = df.loc[df["Country"].isin(selected_countries)]
        df.loc[df["Country"] == "Netherlands (Kingdom of the)", "Country"] = "Netherlands"
        df["Year"] = df["Year"].astype(int)
        df[["PM10", "PM25", "NO2"]].astype(float)
        df[["PM10", "PM25", "NO2"]] = df[["PM10", "PM25", "NO2"]].round(2)
        #Calculate Mean pollutant concentartions per country
        df = df.groupby(["Code", "Country", "Year"]).agg(
             {"PM10": "mean", "PM25": "mean", "NO2": "mean"}).reset_index()
        df = df.dropna()
        return df

    def transform_temperature_data(self, df):
        # Rename columns to representative names
        df = df.rename(columns={"Area": "Country", "Months": "Month"})
        # Select only the required Element = Teperature change
        df = df.loc[df["Element"] == "Temperature change"]
        # Get the list of duplicated year columns
        drop_Y_columns = df.filter(regex=r'^Y\d{4}F$').columns.tolist()
        drop_columns = drop_Y_columns + \
            ['Area Code', 'Area Code (M49)', 'Element Code',
             'Element', 'Months Code', 'Unit']
        # Drop unrequired columns
        df = df.drop(drop_columns, axis=1)
        selected_countries = ['Spain', 'Germany', 'Switzerland', 'Denmark', 'Norway',
                              'Belgium', 'Italy', 'France', 'Sweden', 'Netherlands (Kingdom of the)', 'Luxembourg']
        df = df.loc[df["Country"].isin(selected_countries)]
        df = df.loc[df["Month"].isin(['January', 'February', 'March', 'April', 'May',
                                     'June', 'July', 'August', 'Sepetember', 'October', 'November', 'December'])]
        df = pd.melt(df, id_vars=["Country", "Month",],
                     var_name="Year", value_name="Temperature Change")
        # Remove Y from values in column Year
        df["Year"] = df["Year"].str[1:]
        df["Year"] = df["Year"].astype(int)
        # Select only required years (2013 - 2022()
        df = df.loc[df["Year"].between(2010, 2022)]
        # Calculate Mean temperature Change for year
        # df = df.groupby(["Country", "Year"]).agg(
        #     {"Temperature Change": "mean"}).reset_index()
        df["Temperature Change"] = df["Temperature Change"].round(2)
        df = df.dropna()
        return df

    def save_to_sql(self, df_air, df_temp):
        try:
            conn = create_engine(f'sqlite:///data/data.sqlite')
            df_air.to_sql(name='air_pollution', con=conn,
                                if_exists='replace',  index=False)
            df_temp.to_sql(name="temperature", con=conn,
                                if_exists='replace',  index=False)
        except Exception as e:
            log.error(f"Error connecting to database:{e}")
    
    # def read_from_sql(self):
    #     print("Reading from sql")
    #     try:
    #         conn = create_engine(f'sqlite:///data/data.sqlite')
    #     except Exception as e:
    #         print(f"Error connecting to database:{e}")
    #     df_temp = pd.read_sql('SELECT * FROM air_pollution', conn)
    #     print(df_temp)

    def run_pipeline(self):
        # Extract data
        print("Downloading data...")
        df_temp = self.extract_temperature_data()
        df_air = self.extract_air_data()

        # Transform data
        print("Transforming data...")
        df_temp = self.transform_temperature_data(df_temp)
        df_air = self.transform_air_data(df_air)

        # Save to database
        self.save_to_sql(df_air, df_temp)
        print("Successfully saved to database!")
        
        # Read from database
        # self.read_from_sql()
    
if __name__ == "__main__":

    air_url = "https://cdn.who.int/media/docs/default-source/air-pollution-documents/air-quality-and-health/who_ambient_air_quality_database_version_2024_(v6.1).xlsx?sfvrsn=c504c0cd_3&download=true"
    temperature_url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/Environment_Temperature_change_E_All_Data.zip"

    pipeline = DataPipeline(air_url, temperature_url)
    print("Running pipeline...")
    pipeline.run_pipeline()

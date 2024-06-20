import os
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from sqlalchemy import create_engine
from unittest.mock import patch
from pipeline import DataPipeline

# Define mock data for testing
mock_temperature_data = {
    'Area': ['Spain', 'Germany', 'France', 'United States'],
    'Area Code': [1, 2, 3, 4],
    'Area Code (M49)': [101, 102, 103, 104],
    'Months': ['January', 'February', 'March','May'],
    'Months Code': [101, 102, 103, 105],
    'Element': ['Temperature change', 'Temperature change', 'Temperature change', 'Temperature change'],
    'Element Code': [1001, 1001, 1001, 1001],
    'Unit': ['Celsius', 'Celsius', 'Celsius', 'Celsius'],
    'Y1991': [1.1, 0.9, 1.2, 2.1],
    'Y1992': [1.2, 1.0, 1.3, 2.2],
    'Y1993': [1.3, 1.1, 1.4, 2.3],
    'Y2021': [1.4, 1.2, 1.5, 2.4],
    'Y2022': [1.5, 1.3, 1.6, 2.5]
}

mock_air_data = {
    'iso3': ['ESP', 'DEU', 'USA'],
    'country_name': ['Spain', 'Germany', 'United States'],
    'city': ['Madrid', 'Berlin', 'New York'],
    'year': [2020, 2020, 2020],
    'pm10_concentration': [20.5, 30.0, 25.0],
    'pm25_concentration': [10.5, 20.0, 15.0],
    'no2_concentration': [15.0, 25.0, 18.0],
    'type_of_stations': ['urban', 'urban', 'urban'],
    'population': [3000000, 3500000, 9000000]
}

@pytest.fixture(scope='class')
def setup_pipeline():
    return DataPipeline(air_url="", temperature_url="")

@pytest.fixture(scope='function')
def setup_db():
    db_path = 'data/data.sqlite'
    if os.path.exists(db_path):
        os.remove(db_path)
    yield
    if os.path.exists(db_path):
        os.remove(db_path)

class TestDataPipeline:

    @patch.object(DataPipeline, 'extract_temperature_data', return_value=pd.DataFrame(mock_temperature_data))
    def test_transform_temperature_data(self, mock_extract_temperature_data, setup_pipeline):
        pipeline = setup_pipeline
        
        # Mock data for transform_temperature_data
        transformed_df = pipeline.transform_temperature_data(mock_extract_temperature_data.return_value)
        
        assert isinstance(transformed_df, pd.DataFrame)
        
        # Check columns and types in temp_df
        expected_columns_temp = ['Country', 'Month', 'Year', 'Temperature Change']
        assert all(col in transformed_df.columns for col in expected_columns_temp), f"Missing columns in temp_df: {expected_columns_temp}"
        assert transformed_df['Country'].isin(['Spain', 'Germany', 'France']).all(), "Unexpected countries in temp_df"
        assert transformed_df['Temperature Change'].dtype == float, "Unexpected data type for Temperature Change column in temp_df"
        assert transformed_df['Year'].dtype == int, "Unexpected data type for Year column in temp_df"

    @patch.object(DataPipeline, 'extract_air_data', return_value=pd.DataFrame(mock_air_data))
    def test_transform_air_data(self, mock_extract_air_data, setup_pipeline):
        pipeline = setup_pipeline
        
        # Mock data for transform_air_data
        transformed_df = pipeline.transform_air_data(mock_extract_air_data.return_value)
        
        assert isinstance(transformed_df, pd.DataFrame)

        # Check columns and types in air_df
        expected_columns_air = ['Code', 'Country', 'Year', 'PM10', 'PM25', 'NO2']
        assert all(col in transformed_df.columns for col in expected_columns_air), f"Missing columns in air_df: {expected_columns_air}"
        assert transformed_df['Country'].isin(['Spain', 'Germany']).all(), "Unexpected countries in air_df"
        assert transformed_df['PM10'].dtype == float, "Unexpected data type for PM10 column in air_df"

    @patch.object(DataPipeline, 'extract_temperature_data', return_value=pd.DataFrame(mock_temperature_data))
    @patch.object(DataPipeline, 'extract_air_data', return_value=pd.DataFrame(mock_air_data))
    def test_run_pipeline(self, mock_extract_air_data, mock_extract_temperature_data, setup_pipeline, setup_db):
        pipeline = setup_pipeline
        
        pipeline.run_pipeline()
        
        db_path = 'data/data.sqlite'
        assert os.path.exists(db_path)
        
        engine = create_engine(f'sqlite:///{db_path}')
        air_df = pd.read_sql_table('air_pollution', engine)
        temp_df = pd.read_sql_table('temperature', engine)
        
        assert not air_df.empty
        assert not temp_df.empty

if __name__ == '__main__':
    pytest.main()
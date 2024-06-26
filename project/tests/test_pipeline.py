import os
import pytest
import pandas as pd
from sqlalchemy import create_engine, inspect
from unittest.mock import patch
from pipeline import DataPipeline

# Define mock data for testing
mock_temperature_data = {
    'Area': ['Spain', 'Germany', 'France', 'United States'],
    'Area Code': [1, 2, 3, 4],
    'Area Code (M49)': [101, 102, 103, 104],
    'Months': ['January', 'February', 'March','May'],
    'Months Code': [101, 102, 103, 105],
    'Element': ['Temperature change', 'Temperature change', 'Standard Deviation', 'Temperature change'],
    'Element Code': [1001, 1001, 1002, 1001],
    'Unit': ['Celsius', 'Celsius', 'Celsius', 'Celsius'],
    'Y1991': [1.187, 0.9, 1.2, 2.1],
    'Y1992': [1.2, 1.0, 1.398, 2.2],
    'Y2020': [1.3, 1.1, 1.4, 2.3],
    'Y2021': [1.4, 1.2, 1.598, 2.4],
    'Y2022': [1.5, 1.344, 1.6, 2.5]
}

mock_air_data = {
    'iso3': ['ESP', 'DEU', 'USA'],
    'country_name': ['Spain', 'Germany', 'United States'],
    'city': ['Madrid', 'Berlin', 'New York'],
    'year': [2020.0, 2020.0, 2020],
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

        assert transformed_df['Country'].isin(['Spain', 'Germany', 'France']).all(), "Unexpected countries in temp_df"
        assert transformed_df['Year'].between(2010, 2022).all(), "Unexpected years in temp_df"

    @patch.object(DataPipeline, 'extract_air_data', return_value=pd.DataFrame(mock_air_data))
    def test_transform_air_data(self, mock_extract_air_data, setup_pipeline):
        pipeline = setup_pipeline
        
        # Mock data for transform_air_data
        transformed_df = pipeline.transform_air_data(mock_extract_air_data.return_value)
        
        assert isinstance(transformed_df, pd.DataFrame)

        assert transformed_df['Country'].isin(['Spain', 'Germany']).all(), "Unexpected countries in air_df"

    @patch.object(DataPipeline, 'extract_temperature_data', return_value=pd.DataFrame(mock_temperature_data))
    @patch.object(DataPipeline, 'extract_air_data', return_value=pd.DataFrame(mock_air_data))
    def test_run_pipeline(self, mock_extract_air_data, mock_extract_temperature_data, setup_pipeline, setup_db):
        pipeline = setup_pipeline
        
        pipeline.run_pipeline()
        
        # check if database file and tables exist
        db_path = 'data/data.sqlite'
        assert os.path.exists(db_path), "Database file does not exist"
        
        engine = create_engine(f'sqlite:///{db_path}')
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'air_pollution' in tables, "air_pollution table does not exist"
        assert 'temperature' in tables, "temperature table does not exist"

        # check expected columns and types
        expected_columns = {
            'air_pollution': {'Code': 'TEXT', 'Country': 'TEXT', 'Year': 'BIGINT', 'PM10': 'FLOAT', 'PM25': 'FLOAT', 'NO2': 'FLOAT'},
            'temperature': {'Country': 'TEXT', 'Month': 'TEXT', 'Year': 'BIGINT', 'Temperature Change': 'FLOAT'}
        }
        
        for table_name, expected_columns in expected_columns.items():
            columns = {c['name']: c['type'] for c in inspector.get_columns(table_name)}
            for col, col_type in expected_columns.items():
                assert col in columns, f"Missing column in {table_name}: {col}"
                assert str(columns[col]) == col_type, f"Incorrect type for column {col} in {table_name}. Expected: {col_type}, Found: {columns[col]}"
        
        # check if tables are not empty
        air_df = pd.read_sql_table('air_pollution', engine)
        temp_df = pd.read_sql_table('temperature', engine)

        assert not air_df.empty, "air_pollution table is empty"
        assert not temp_df.empty, "temperature table is empty"

if __name__ == '__main__':
    pytest.main()
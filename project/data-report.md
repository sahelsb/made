### Exploring the Association Between Climate Change Indicators and Air Pollution Levels in selected European countries during the Years 2013-2022

#### 1.&nbsp;&nbsp; Introduction

Climate change and air pollution are critical environmental issues, both driven by human activity and significantly impacting public health and ecosystems. This project investigates the correlation between these two factors specifically in European countries, where industrial activities and dense urban areas contribute to notable pollution levels and climate variations.

#### Main Questions:
1. How have temperature and air pollution levels (PM10, PM2.5, NO2) changed over the years in European countries?
2 .Is there a correlation between key air pollutant levels (PM10, PM2.5, NO2) and temperature changes in these countries?

#### 2.&nbsp;&nbsp; Data Sources

1. FAOSTAT Climate Change Data
- Metadata URL: [FAO Climate Metadata](https://www.fao.org/faostat/en/#data/ET/metadata)
- Data URL: [FAO Temperature Data](https://fenixservices.fao.org/faostat/static/bulkdownloads/Environment_Temperature_change_E_All_Data.zip)
- Data Type: CSV
- Licensing: CC BY-NC-SA 3.0 IGO

This dataset provides historical records of temperature changes, structured as a CSV file with columns for country names, months, years, and temperature changes. The data, sourced from the reputable Food and Agriculture Organization (FAO), is of high quality and covers an extensive temporal range. However, the dataset may include missing values and duplicated columns for years, which require preprocessing.

The dataset is licensed under "CC BY-NC-SA 3.0 IGO," allowing for use, sharing, and adaptation for non-commercial purposes with appropriate credit. To comply with this license, the project will include proper citations and links to the original data source, and the data will be used solely for educational purposes.


1. WHO Ambient Air Quality Data
- Metadata URL: [WHO Air Quality Metadata](https://cdn.who.int/media/docs/default-source/air-pollution-documents/air-quality-and-health/who_ambient_air_quality_database_version_2024_(v6.1).xlsx?sfvrsn=c504c0cd_3&download=true)
- Data URL: [WHO Air Quality Data](https://cdn.who.int/media/docs/default-source/air-pollution-documents/air-quality-and-health/who_ambient_air_quality_database_version_2024_(v6.1).xlsx?sfvrsn=c504c0cd_3&download=true)
- Data Type: Excel
- Licensing: [Open Data](https://www.who.int/about/policies/publishing/copyright)
  
This dataset contains information on air pollution indicators, including particulate matter (PM10, PM2.5) and nitrogen dioxide (NO2). Structured as an Excel file with multiple sheets including metadat as well, with columns for country codes, country names, city names, years, pollutant concentrations, and types of measurement stations. The data, provided by the reputable World Health Organization (WHO), is of high quality. However, it may contain missing values for some countires and lacks data for years before 2013, which may limit the temporal scope of the analysis.

WHO data can be used for research and educational purposes, provided proper attribution is given and the data is not used for commercial purposes. To comply, the project include proper citations and links to the original data source, ensuring that the data is used solely for educational purposes, in line with WHO’s licensing terms.


#### 3.&nbsp;&nbsp; Data Pipeline

The data pipeline, implemented in Python, automates the process of data extraction, transformation, and loading (ETL).It consists of several functions:

- Data Extraction: Download datasets from FAO and WHO using the requests library. FAOSTAT Climate Change dataset is downloaded as a ZIP file, which is extracted using the zipfile library, where the first CSV file inside the ZIP archive is loaded into a pandas DataFrame. WHO Air Quality dataset is obtained as an Excel file. The relevant sheet and columns are directly read into a pandas DataFrame using the pandas library with the openpyxl engine.<br>
- Data Transformation: Cleans and processes the data to align formats and performs necessary calculations.<br>
- Data Storage: Saves the processed data into an SQLite database for further analysis.

##### Transformation steps

| Dataset                                 | Transformations                                                                                                           |
|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| FAOSTAT Climate Change/WHO Air Quality | - Rename columns to ensure consistency across datasets.<br>- Drop unnecessary columns from the datasets.<br>- Round numeric columns (pollutant concentrations and temperature changes) to ensure readability.<br>- Drop missing values. |
| FAOSTAT Climate Change                 | - Filter temperature dataset to include only data related to temperature change.<br>- Reshape temperature dataset to store years as a single column.<br>|
| WHO Air Quality                        | - Filter air quality dataset to include data for only selected European countries.<br>- Aggregate air quality data on country level <br>- Drop missing values from the air quality dataset to ensure data integrity. |


-Since both datasets has missing values that could skew the analysis, the missing values are dropped to ensure data integrity.<br><br>
-FAOSTAT Climate Change dataset includes years as separate columns, so it is reshaped to store years as one column.<br><br>
-WHO Air Quality dataset includes pollutant concentrations for different cities within each country. The data is aggregated by calculating the mean pollutant concentrations for each country to ensure consistency.

                  
##### Error Handling and Dynamic Input

The pipeline includes basic error handling mechanisms using try-except blocks to manage potential issues, such as network problems during data download or errors while connecting to the database which ensures the pipeline can provide informative error messages.

However, the pipeline currently does not fully support automatic adaptation to changes in the data source structure. Adjustments to the pipeline code would be required if there are significant changes in the structure of the input data, such as new columns or different formats. 

#### 4.&nbsp;&nbsp;  Result and Limitations 

#### 4.1 Output

The output data of the pipeline is stored as two tables in a SQLite database. Storing the data in a relational database facilitates efficient data retrieval and manipulation for subsequent analysis.

#### 4.2 Limitations

-Temporal Inconsistency: While the temperature dataset offers a long-term perspective, the air quality data is limited to recent years. The differing ranges of years between the two datasets may pose challenges in interpreting trends and limit the comprehensiveness of the analysis.

-Data Accuracy and Reporting: Despite the reputability of the data sources, the accuracy of measurements and reporting can vary between countries and over time. These potential inaccuracies and variations must be acknowledged when comparing data between different countries and periods.







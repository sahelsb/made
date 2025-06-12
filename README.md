## Project - Analyzing the correaltion Between Temperature change and key Air Pollutant levels

### Project Description 

Climate change presents profound challenges to global ecosystems and human health, with air quality becoming a critical concern. This project aims to analyze the trends in temperature change and air pollution levels, focusing on particulate matter (PM10 and PM2.5) and nitrogen dioxide (NO2), across selected European countries. These pollutants were chosen due to their significant health impacts and their influential role in climate dynamics.

The primary objective of this analysis is to address the following key questions:

  - How have temperature and air pollution levels (PM10, PM2.5, NO2) changed over the years?
  
  - Is there a correlation between key air pollutant levels and temperature changes?

For the analysis, two datasets from open data sources FAOSTAT and WHO are used. Detailed information on data sources, the data pipeline, and analysis results can be found in the project folder.

#### Project Overview

This project includes an ETL pipeline that performs data transformation and loading tasks. The resulting datasets are saved in the `/data` directory and are used for further analysis.

#### Run the Pipeline

To execute the ETL pipeline, run the following bash script:

```
bash project/pipeline.sh
```

#### Test the Pipeline

A test environment is provided to validate the ETL pipeline. To run the tests:

```
bash project/tests.sh
```

Additionally, a GitHub Action has been configured under [CI](.github/workflows/test.yml). This action automatically runs the tests on every push to the main branch.

#### Project Resources

[Data Report](project/data-report.pdf)
Detailed documentation on the data sources and the implemented ETL pipeline.

[Analysis Report](project/analysis-report.pdf)
A comprehensive summary of the analysis results.

[Jupyter Notebook](project/analysis-report.ipynb)
Interactive notebook exploring the main research questions of the project.







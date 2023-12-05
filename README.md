# 2023-fall-clinic-climate-cabinet

## Project Summary

1. Collect state's political campaign finance report data which should include
recipient information, donor information, and transaction information.
2. Preprocess, clean, and standardize the collected raw data across 4 states
by implementing state cleaner abstract class
3. Conduct Exploratory Data Analysis, facilitate the examination of
the conribution made by green energy company versus that by fossil
fuel company in terms of state's political campaign activity


## Usage

### Docker

### Docker & Make

We use `docker` and `make` to run our code. There are three built-in `make` commands:

* `make build-only`: This will build the image only. It is useful for testing and making changes to the Dockerfile.
* `make run-notebooks`: This will run a jupyter server which also mounts the current directory into `\program`.
* `make run-interactive`: This will create a container (with the current directory mounted as `\program`) and loads an interactive session. 

The file `Makefile` contains information about about the specific commands that are run using when calling each `make` statement.

### Developing inside a container with VS Code

If you prefer to develop inside a container with VS Code then do the following steps. Note that this works with both regular scripts as well as jupyter notebooks.

1. Open the repository in VS Code
2. At the bottom right a window may appear that says `Folder contains a Dev Container configuration file...`. If it does, select, `Reopen in Container` and you are done. Otherwise proceed to next step. 
3. Click the blue or green rectangle in the bottom left of VS code (should say something like `><` or `>< WSL`). Options should appear in the top center of your screen. Select `Reopen in Container`.


## Repository Structure

### utils

Files:
- arizona.py: python code to implement Arizona's state cleaner abstract class
- michigan.py: python code to implement Michigan's state cleaner abstract class
- minnesota.py: python code to implement Minnesota's state cleaner abstract class
- pennsylvania.py: python code to implement Pennsylvania's state cleaner abstract class
- constants.py: the python script file to store any necessary constants used for state campaign finance data preprocess, clean, and stardandization
- clean.py: python code for the state cleaner parent class implementation
- pipeline.py: python code for running the state cleaner for 4 states. It generates the final database (DataFrame) through steps of preprocess, clean, standardize, and create table


### notebooks

Contains short, clean notebooks to demonstrate analysis, including information such as:
1. Raw dataset format (file format, relational?)
2. Raw dataset column information (type, content)
3. Top 10 contributors and top 10 recipients in each state per year
4. Bar charts to compare contributions by donor type (PAC, individual, etc) and to compare recipients by the office type they are running for
5. Additional analysis: Yearly trend and possible explanation

Files:
- AZ_EDA
- mi_campaign_eda
- MN_EDA
- PA_EDA

### data

Contains details of acquiring all raw data used in repository. If data is small (<50MB) then it is okay to save it to the repo, making sure to clearly document how to the data is obtained.

If the data is larger than 50MB than you should not add it to the repo and instead document how to get the data in the README.md file in the data directory. 

This [README.md file](/data/README.md) should be kept up to date.

### output

Creating a searchable, relational database of Arizona, Michigan, Minnesota, and Pennsylvania campaign finance data to chart money flows from 2018 to 2023
- individual table: include nidividual recipient and donor information of id, first name, last name, full name, entity type (Individual, Lobbyist), state, party, company
- organization table: include organizational recipient and donor information of id, name, state, entity type (party, committee, corporation, etc.)
- transaction table: include contribution and expenditure transaction information of transaction id, donor id, recipient id, year, amount, recipient office sought, purpose, and transaction type


### Project Pipeline

1. Collect state's finance campaign data either from web scraping (AZ, MI, PA) or direct download (MN)
2. User can go to [the shared Google Drive]('https://drive.google.com/drive/u/2/folders/1HUbOU0KRZy85mep2SHMU48qUQ1ZOSNce') to download each state's data to their local repo following this format: repo_root / "data" / "raw" / "file"
3. Install all the necessary python packages listed in requirements.txt
4. Use utils/pipeline.py to preprocess, clean, standardize, and create tables for each state and ultimately concatinate tables across 4 states into a comprehensive database
5. The final result should be an individual DataFrame, an organization DataFrame, and a transaction DataFrame. They each contain all data in AZ, MI, MN, PA datasets
6. For future reference, the above pipeline also stores the information mapping given id to our database id (generated via uuid) in a csv file in the format of (state)IDMap.csv

## Team Member

Student Name: April Wang
Student Email: yuzhouw@uchicago.edu

Student Name: Nicolas Posner
Student Email: nrposner@uchicago.edu

Student Name: Aïcha Camara
Student Email: aichacamara@uchicago.edu

Student Name: Alan Kagiri
Student Email: alankagiri@uchicago.edu. 

# 2024-winter-clinic-climate-cabinet

## Data Science Clinic Project Goals

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


### Data Collection and Standardization Pipeline
1. Collect the data through **<span style="color: red;">one</span>** of the steps below
    a. Collect state's finance campaign data either from web scraping (AZ, MI, PA) or direct download (MN) OR
    b. Go to the [Project's Google Drive]('https://drive.google.com/drive/u/2/folders/1HUbOU0KRZy85mep2SHMU48qUQ1ZOSNce') to download each state's data to their local repo following this format: repo_root / "data" / "raw" / state acronym / "file"
2. Open in development container which installs all necessary packages.
3. Run the project by running ```python utils/pipeline.py``` or ```python3 utils/pipeline.py``` run the processing pipeline that cleans, standardizes, and creates the individuals, organizations, and transactions concatenated into one comprehensive database.
5. Running ```pipeline.py``` returns the tables to the output folder as csv files containing the complete individuals, organizations, and transactions DataFrames combining the AZ, MI, MN, and PA datasets.
6. For future reference, the above pipeline also stores the information mapping given id to our database id (generated via uuid) in a csv file in the format of (state)IDMap.csv (example: ArizonaIDMap.csv) in the output folder

### Record Linkage and Network Pipeline
1. Save the standardized tables "complete_individuals_table.csv", "complete_organizations_table.csv", and "complete_transactions_table.csv" (collected from the above pipeline or data from the project's Google Drive) in the following format: repo_root / "output" / "file"
2. **UPDATE:** Run the pipeline by calling ```make run-linkage-and-networkpipeline```. This pipeline will perform conservative record linkage, attempt to classify entities as neutral, fossil fuels, or clean energy, convert the standardized tables into a NetworkX Graph, and show an interactive network visual.
3. The pipeline will output the deduplicated tables saved as "cleaned_individuals_table.csv", "cleaned_organizations_table.csv", and "cleaned_transactions_table.csv". A mapping file, "deduplicated_UUIDs" tracks the UUIDs designated as duplicates. The pipeline will also output "Network Graph Node Data", 
  which is the NetworkX Graph object converted into an adjecency list. Finally the pipeline will create a file called 'network_metrics.txt' which holds the summary statistics we extrapolated from the network including measures of centrality, connectedness, and communites.

## Repository Structure

### utils
Project python code

### notebooks
Contains short, clean notebooks to demonstrate analysis.

### data

Contains details of acquiring all raw data used in repository. If data is small (<50MB) then it is okay to save it to the repo, making sure to clearly document how to the data is obtained.

If the data is larger than 50MB than you should not add it to the repo and instead document how to get the data in the README.md file in the data directory. 

This [README.md file](/data/README.md) should be kept up to date.

### output
This folder is empty by default. The final outputs of the Makefile will be placed here, consisting of a NetworkX Graph object and a txt file containing graph metrics. 



## Team Member

Student Name: Nicolas Posner
Student Email: nrposner@uchicago.edu

Student Name: Alan Kagiri
Student Email: alankagiri@uchicago.edu. 

Student Name: Adil Kassim
Student Email: adilk@uchicago.edu

Student Name: Nayna Pashilkar
Student Email: npashilkar@uchicago.edu

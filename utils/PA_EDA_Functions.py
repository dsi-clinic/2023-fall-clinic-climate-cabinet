import pandas as pd
import plotly.express as px

from utils import constants as const


def assign_col_names(filepath: str, year: int) -> list:
    """Assigns the right column names to the right datasets.

    Args:
        filepath: the path in which the data is stored/located.

        year: to make parsing through the data more manageable, the year from
        which the data originates is also taken.

    Returns:
        a list of the appropriate column names for the dataset.
    """
    dir = filepath.split("/")
    file_type = dir[len(dir) - 1]

    if "contrib" in file_type:
        # in 2022 PA changed its data storage format by adding an extra variable
        # making the number and names of columns different from preceding years.
        # The following if statements account for this by referencing the
        # appropriate column list in  constants.py
        if year < 2022:
            return const.PA_CONT_COLS_NAMES_PRE2022
        else:
            return const.PA_CONT_COLS_NAMES_POST2022
    elif "filer" in file_type:
        if year < 2022:
            return const.PA_FILER_COLS_NAMES_PRE2022
        else:
            return const.PA_FILER_COLS_NAMES_POST2022
    elif "expense" in file_type:
        if year < 2022:
            return const.PA_EXPENSE_COLS_NAMES_PRE2022
        else:
            return const.PA_EXPENSE_COLS_NAMES_POST2022


def classify_contributor(contributor: str) -> str:
    """Takes a string input and compares it against a list of identifiers most
    commonly associated with organizations/corporations/PACs, and classifies the
    string input as belong to an individual or organization

    Args:
        contributor: a string
    Returns:
        string "ORGANIZATION" or "INDIVIDUAL" depending on the classification of
        the parameter
    """
    split = contributor.split()
    loc = 0
    while loc < len(split):
        if split[loc].upper() in const.PA_ORGANIZATION_IDENTIFIERS:
            return "ORGANIZATION"
        loc += 1
    return "INDIVIDUAL"


def pre_process_contributor_dataset(df: pd.DataFrame):
    """pre-processes a contributor dataset by sifting through the columns and
    keeping the relevant columns for EDA and AbstractStateCleaner purposes

    Args:
        df: the contributor dataset

    Returns:
        a pandas dataframe whose columns are appropriately formatted.
    """
    df["TOTAL_CONT_AMT"] = df["CONT_AMT_1"] + df["CONT_AMT_2"] + df["CONT_AMT_3"]
    df["DONOR"] = df["DONOR"].astype("str")
    df["DONOR"] = df["DONOR"].str.upper()
    df["DONOR_TYPE"] = df["DONOR"].apply(classify_contributor)
    df.drop(
        columns={
            "ADDRESS_1",
            "ADDRESS_2",
            "CITY",
            "STATE",
            "ZIPCODE",
            "OCCUPATION",
            "E_NAME",
            "E_ADDRESS_1",
            "E_ADDRESS_2",
            "E_CITY",
            "E_STATE",
            "E_ZIPCODE",
            "SECTION",
            "CYCLE",
            "PURPOSE",
            "CONT_DATE_1",
            "CONT_AMT_1",
            "CONT_DATE_2",
            "CONT_AMT_2",
            "CONT_DATE_3",
            "CONT_AMT_3",
        },
        inplace=True,
    )

    if "TIMESTAMP" in df.columns:
        df.drop(columns={"TIMESTAMP", "REPORTER_ID"}, inplace=True)
        df["DONOR"] = df["DONOR"].apply(lambda x: str(x).upper())

    return df


def pre_process_filer_dataset(df: pd.DataFrame):
    """pre-processes a filer dataset by sifting through the columns and
    keeping the relevant columns for EDA and AbstractStateCleaner purposes

    Args:
        df: the filer dataset

    Returns:
        a pandas dataframe whose columns are appropriately formatted.
    """
    df.drop(
        columns={
            "YEAR",
            "CYCLE",
            "AMEND",
            "TERMINATE",
            "DISTRICT",
            "ADDRESS_1",
            "ADDRESS_2",
            "CITY",
            "STATE",
            "ZIPCODE",
            "COUNTY",
            "PHONE",
            "BEGINNING",
            "MONETARY",
            "INKIND",
        },
        inplace=True,
    )
    if "TIMESTAMP" in df.columns:
        df.drop(columns={"TIMESTAMP", "REPORTER_ID"}, inplace=True)

    df.drop_duplicates(subset=["RECIPIENT_ID"], inplace=True)
    df["RECIPIENT_TYPE"] = df.RECIPIENT_TYPE.map(const.PA_FILER_ABBREV_DICT)
    df["RECIPIENT"] = df["RECIPIENT"].apply(lambda x: str(x).upper())
    return df


def pre_process_expense_dataset(df: pd.DataFrame):
    """pre-processes an expenditure dataset by sifting through the columns and
    keeping the relevant columns for EDA and AbstractStateCleaner purposes

    Args:
        df: the expenditure dataset

    Returns:
        a pandas dataframe whose columns are appropriately formatted.
    """
    df.drop(
        columns={
            "EXPENSE_CYCLE",
            "EXPENSE_ADDRESS_1",
            "EXPENSE_ADDRESS_2",
            "EXPENSE_CITY",
            "EXPENSE_STATE",
            "EXPENSE_ZIPCODE",
            "EXPENSE_DATE",
        },
        inplace=True,
    )
    if "EXPENSE_REPORTER_ID" in df.columns:
        df.drop(columns={"EXPENSE_TIMESTAMP", "EXPENSE_REPORTER_ID"}, inplace=True)
    df["PURPOSE"] = df["PURPOSE"].apply(lambda x: str(x).upper())
    df["RECIPIENT"] = df["RECIPIENT"].apply(lambda x: str(x).upper())

    return df


def initialize_PA_dataset(data_filepath: str, year: int) -> pd.DataFrame:
    """Initializes the PA data appropriately based on whether the data contains
    filer, contributor, or expense information

    Args:
        data_filepath: the path in which the data is stored/located.

        year: the year from which the data originates

    Returns:
        a pandas dataframe whose columns are appropriately formatted, and
        any dirty rows with inconsistent columns names dropped.
    """
    df = pd.read_csv(
        data_filepath,
        names=assign_col_names(data_filepath, year),
        sep=",",
        encoding="latin-1",
        on_bad_lines="warn",
    )

    df["YEAR"] = year
    if "RECIPIENT_ID" in df.columns:
        df["RECIPIENT_ID"] = df["RECIPIENT_ID"].astype("str")
    else:
        df["DONOR_ID"] = df["DONOR_ID"].astype("str")
    dir = data_filepath.split("/")
    file_type = dir[len(dir) - 1]

    if "contrib" in file_type:
        return pre_process_contributor_dataset(df)

    elif "filer" in file_type:
        return pre_process_filer_dataset(df)

    elif "expense" in file_type:
        return pre_process_expense_dataset(df)

    else:
        raise ValueError(
            "This function is currently formatted for filer, \
            expense, and contributor datasets. Make sure your data \
            is from these sources."
        )


def top_n_recipients(df: pd.DataFrame, num_recipients: int) -> object:
    """Given a dataframe, retrieves the top n recipients of that year based on
    contributions and returns a table
    Args:
        df: a pandas DataFrame with a contributions column

        num_recipients: an integer specifying how many recipients are desired.
        If this value is larger than the possible amount of recipients, then all
        recipients are returned instead.

    Returns:
    A pandas table (object)
    """
    recipients = (
        df.groupby(["RECIPIENT"])
        .agg({"TOTAL_CONT_AMT": sum})
        .sort_values(by="TOTAL_CONT_AMT", ascending=False)
    )
    pd.set_option("display.float_format", "{:.2f}".format)

    if num_recipients > len(recipients):
        return recipients
    else:
        return recipients.head(num_recipients)


def top_n_contributors(df: pd.DataFrame, num_contributors: int) -> object:
    """Given a dataframe, retrieves the top n contributors of that year based on
    contributions and returns a table

    Args:
        df: a pandas DataFrame with a contributions column

        num_contributors: an integer specifying how many contributors are
        desired. If this value is larger than the possible amount of
        contributors, then all contributors are returned instead.

    Returns:
    a pandas table (object)
    """
    contributors = (
        df.groupby(["DONOR"])
        .agg({"TOTAL_CONT_AMT": sum})
        .sort_values(by="TOTAL_CONT_AMT", ascending=False)
    )
    pd.set_option("display.float_format", "{:.2f}".format)
    if num_contributors > len(contributors):
        return contributors
    else:
        return contributors.head(num_contributors)


def merge_same_year_datasets(
    cont_file: pd.DataFrame, filer_file: pd.DataFrame
) -> pd.DataFrame:
    """Merges the contributor and filer datasets from the same year using the
    unique filerID
    Args:
        cont_file: The contributor dataset

        filer_file: the filer dataset from the same year as the cont_file.

    Returns:
        The merged pandas dataframe
    """
    merged_df = pd.merge(cont_file, filer_file, how="left", on="RECIPIENT_ID")
    return merged_df


def merge_all_datasets(datasets: list) -> pd.DataFrame:
    """Concatenates datasets from different years into one super dataset
    Args:
        datasets: a list of datasets

    Returns:
        The merged pandas dataframe
    """
    return pd.concat(datasets)


def group_filerType_Party(dataset: pd.DataFrame) -> object:
    """Takes a dataset and returns a grouped table highlighting the kinds
    of people who file the campaign reports (FilerType Key -> 1:Candidate,
    2:Committee, 3:Lobbyist.) and their political party affiliation

    Args:
        dataset: a pandas DataFrame containing columns and values from the filer
        dataset.

    Returns:
    A table object
    """
    return dataset.groupby(["RECIPIENT_TYPE", "PARTY"]).agg({"TOTAL_CONT_AMT": sum})


def plot_recipients_by_office(merged_dataset: pd.DataFrame) -> object:
    """Returns a table and plots a bargraph of data highlighting the amount of
    contributions each statewide race received over the years

    Args:
        merged_dataset: A (merged) pandas DataFrame containing columns and
        values from the contributor and filer datasets.

    Return:
    A table object
    """
    recep_per_office = merged_dataset.replace(
        {"RECIPIENT_OFFICE": const.PA_OFFICE_ABBREV_DICT}
    )

    recep_per_office = (
        recep_per_office.groupby(["RECIPIENT_OFFICE"])
        .agg({"TOTAL_CONT_AMT": sum})
        .reset_index()
    )

    fig = px.bar(
        data_frame=recep_per_office,
        x="RECIPIENT_OFFICE",
        y="TOTAL_CONT_AMT",
        title="Pennsylvania Contributions Received by Office-Type From 2018-2023",
        labels={"TOTAL_CONT_AMT": "Total Contribution Amount"},
    )
    fig.show()

    return recep_per_office


def compare_cont_by_donorType(merged_dataset: pd.DataFrame) -> object:
    """Returns a table and plots a barplot highlighting the annual contributions
    campaign finance report-filers received based on whether they are candidates
    , committees, or lobbyists.

    Args:
        merged_dataset: A (merged) pandas DataFrame containing columns from both
        the filer and contributor datasets.

    Return:
        A pandas DataFrame
    """
    pd.set_option("display.float_format", "{:.2f}".format)
    cont_by_donor = (
        merged_dataset.groupby(["YEAR", "RECIPIENT_TYPE"])
        .agg({"TOTAL_CONT_AMT": sum})
        .reset_index()
    )

    fig = px.bar(
        data_frame=cont_by_donor,
        x="YEAR",
        y="TOTAL_CONT_AMT",
        color="FILER_TYPE",
        title="Pennsylvania Recipients of Annual Contributions (2018 - 2023)",
        labels={
            "TOTAL_CONT_AMT": "Total Contribution Amount",
            "RECIPIENT_TYPE": "Type of Filer",
        },
    )
    fig.show()
    return cont_by_donor

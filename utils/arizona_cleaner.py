import pandas as pd
from clean import StateCleaner
from cleaner_utils import (
    az_employment_checker,
    az_individuals_convert,
    az_name_clean,
    az_organizations_convert,
    az_transactions_convert,
    convert_date,
    transactor_sorter,
)


class ArizonaCleaner(StateCleaner):
    """This class is based on the StateCleaner abstract class,
    and cleans Arizona data"""

    def preprocess(filepaths_list: list[str]) -> list[pd.DataFrame]:
        """Turns filepaths into dataframes

        The input must be a list of valid filepaths which lead
        to pandas dataframes. Typically, these should be just two
        files: a transactions file and a details file, as
        harvested by az_curl_crawler. If these conditions are not
        met, the rest of the pipeline will not work

        args: list of two filepaths for dataframes,
        transactions and details, in that order

        returns: a list of two dataframes, transactions and details,
        in that order

        """

        df_list = []

        for filepath in filepaths_list:
            df_list.append(pd.read_csv(filepath))

        return df_list

    def clean_state(filepaths: list[str]) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        """Calls the other methods in order

        This is the master function of the ArizonaCleaner
        class, and calling it will activate the cleaning
        pipeline which takes in filenames and outputs cleaned,
        standardized, and schema-compliant tables

        args: list of two filepaths which lead to dataframes

        returns: three schema-compliant tables for
        transactions, individuals, and organizations

        """

        transactions, details = ArizonaCleaner.preprocess(filepaths)

        cleaned_transactions, cleaned_details = ArizonaCleaner.clean(
            [transactions, details]
        )

        standardized_transactions, standardized_details = ArizonaCleaner.standardize(
            [cleaned_transactions, cleaned_details]
        )

        (
            az_transactions,
            az_individuals,
            az_organizations,
        ) = ArizonaCleaner.create_tables(
            [standardized_transactions, standardized_details]
        )

        return (az_transactions, az_individuals, az_organizations)

    def create_tables(
        data: list[pd.DataFrame],
    ) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        """split up cleaned and standardized tables to undergo final formatting

        We split up the details tables into individuals (individual contributors
        and donors) and organizations (everything else), which then undergo
        conversion into fully schema-compatible transactions, individual details
        and organization details tables.

        args: cleaned and standardized transactions and details tables

        returns: three tables for transactions,
        individual details, and organization details

        """

        transactions, details = data[0], data[1]

        individual_details = details[
            (details["entity_type"] == "Individual")
            | (details["entity_type"] == "Candidate")
        ]
        organization_details = details[
            (details["entity_type"] != "Individual")
            & (details["entity_type"] != "Candidate")
        ]

        az_transactions = az_transactions_convert(transactions)

        if len(individual_details) > 0:
            az_individuals = az_individuals_convert(individual_details)
        else:
            az_individuals = None

        if len(organization_details) > 0:
            az_organizations = az_organizations_convert(organization_details)
        else:
            az_organizations = None

        return (az_transactions, az_individuals, az_organizations)

    def standardize(details_df_list: list[pd.DataFrame]) -> list[pd.DataFrame]:
        """standardize names of entities

        takes in details dataframe and replaces the names of
        organization types to fit into the schema when appropriate

        args: details dataframe

        returns: details dataframe with relevant entity type
        names replaced by those for the regular schema
        """

        transactions_df, details_df = details_df_list[0], details_df_list[1]

        az_entity_name_dictionary = {
            "Organizations": "Company",
            "PACs": "Committee",
            "Parties": "Party",
            "Vendors": "Vendor",
            "Individual Contributors": "Individual",
            "Candidates": "Candidate",
        }
        details_df.replace({"entity_type": az_entity_name_dictionary}, inplace=True)

        return transactions_df, details_df

    def clean(data: list[pd.DataFrame]) -> pd.DataFrame:
        """clean the contents of the columns

        INCOMPLETE

        transactions and details dataframes undergo cleaning of
        transaction dates, names are imputed to the right column,
        and employer information is retrieved,

        args: transactions and details dataframes

        returns: cleaned transactions and details dataframes

        NOTE: TO DO: coerce correct dtypes and make text lowercase

        """

        transactions, details = data[0], data[1]

        merged_df = pd.merge(details, transactions, on="retrieved_id", how="inner")

        # Filter rows in the first dataframe based on the common 'ids'
        details = details[details["retrieved_id"].isin(merged_df["retrieved_id"])]

        try:
            transactions["TransactionDate"] = transactions["TransactionDate"].apply(
                convert_date
            )
        except TypeError:
            transactions["TransactionDate"] = transactions["TransactionDate"]

        details = az_name_clean(details)

        details = details.apply(az_employment_checker, args=(transactions,), axis=1)

        transactions = transactions.apply(transactor_sorter, axis=1)

        merged_df = pd.merge(
            transactions["base_transactor_id"],
            details[["retrieved_id", "office_name"]],
            how="left",
            left_on="base_transactor_id",
            right_on="retrieved_id",
        )

        office_sought = merged_df.where(pd.notnull(merged_df), None)["office_name"]

        transactions["office_sought"] = office_sought

        return [transactions, details]

import pandas as pd
import requests
from constants import AZ_base_data, AZ_head, AZ_pages_dict, AZ_valid_detailed_pages


def az_wrapper(
    page: str, start_year=2023, end_year=2023, *args, **kwargs: int
) -> pd.DataFrame:
    """Scrape data from arizona database at https://seethemoney.az.gov/

    This function retrieves and compiles the data from a given table
    from the arizona database, whether aggregate or detailed,
    within the given time period
    NOTE: Empty returns are to be expected for some inputs,
    as some tables are empty or near empty even for long spans of time.

    Args: page: the name of a basic or detailed page in the
    Arizona dataset, excluding the Name page.
    start_year: earliest year to include scraped data, inclusive
    end_year: last year to include scraped data, inclusive

    Returns: a pandas dataframe of the
    """

    page = AZ_pages_dict[page]

    if page < 10:
        return scrape_wrapper(page, start_year, end_year)

    else:
        det = detailed_wrapper_director(page)
        agg_df = scrape_wrapper(det, start_year, end_year)
        entities = entities = agg_df["EntityID"]

        return detailed_scrape_wrapper(entities, page, start_year, end_year)


def detailed_wrapper_director(page: int) -> int:
    """Direct az_wrapper to base page from detailed page

    This function takes as input the number of the page input to
    scrape_wrapper in the course of az_wrapper, and derives the
    number of the parent page which must be scraped for
    entities first

    Args: page: the two-digit page number belonging to a
    detailed page as shown in AZ_pages_dict.

    Returns: an integer representing the parent page
    """
    if page not in AZ_valid_detailed_pages:
        raise ValueError("not a valid detailed page number")

    return int(str(page)[0]) - 1


def scrape_wrapper(page, start_year, end_year, *args: int) -> pd.DataFrame:
    """Create parameters and scrape an aggregate table

    This function is called by az_wrapper() to create the parameters and
    call the basic scraper for a certain basic page. To scrape the detailed
    pages, use detailed_scrape_wrapper() instead.

    Args: page: the one-digit number representing one of the eight
    basic pages in the arizona dataset, such as Candidates, PAC,
    Individual Contributions, etc. Refer to AZ_pages_dict
    start_year: earliest year to include scraped data, inclusive
    end_year: last year to include scraped data, inclusive

    Returns: a pandas dataframe containing the table data for
    the selected timeframe
    """
    params = parametrize(page, start_year, end_year)
    res = scrape(params, AZ_head, AZ_base_data)
    results = res.json()
    df = pd.DataFrame(data=results["data"])
    df = df.reset_index().drop(columns={"index"})
    return df


def detailed_scrape_wrapper(
    entities: pd.core.series.Series, page: int, start_year: int, end_year: int
) -> pd.DataFrame:
    """Create parameters and scrape an aggregate table

    This function is called by az_wrapper() to create the parameters and
    call the detailed scraper for a certain detailed page. To scrape the
    basic pages, use scrape_wrapper() instead.

    Args: page: the two-digit number representing a sub-page of
    one of the eight basic pages, such as Candidates/Income,
    PAC/All Transactions, etc. Refer to AZ_pages_dict
    start_year: earliest year to include scraped data, inclusive
    end_year: last year to include scraped data, inclusive

    Returns: a pandas dataframe containing the table data for
    the selected timeframe
    """

    d_params = []

    for entity in entities:
        ent = detailed_parametrize(entity, page, start_year, end_year)
        d_params.append(ent)

    dfs = []

    for d_param in d_params:
        res = detailed_scrape(d_param, start_year, end_year)
        results = res.json()
        dfs.append(pd.DataFrame(data=results["data"]))

    return pd.concat(dfs).reset_index().drop(columns={"index"})


def scrape(params: dict, headers: dict, data: dict) -> requests.models.Response:
    """Scrape a table from the main arizona site

    This function takes in the header and base provided
    elsewhere, and parameters generated by parametrize(),
    to locate and scrape data from one of the eight
    aggregate tables on the Arizona database.

    Args: params: created from parametrize(), containing
    the page, start and end years, table page, and table length.
    Note that 'page' encodes the page to be scraped, such as
    Candidates, IndividualContributions, etc. Refer to the
    attached Pages dictionary for details.
    headers: necessary for calling the response, provided above
    data: necessary for calling the response, provided above
    """

    return requests.post(
        "https://seethemoney.az.gov/Reporting/GetNEWTableData/",
        params=params,
        # cookies=cookies,
        headers=AZ_head,
        data=AZ_base_data,
    )


def detailed_scrape(
    detailed_params: dict, headers: dict, data: dict
) -> requests.models.Response:
    """Scrape a sub-table from the arizona database

    This function takes an entity number, which can be
    gathered from an aggregate table using scrape() or
    inputted manually, and gathers that entity's detailed
    information within the specified time frame from
    one of the sub-tables.

    Args: detailed_params: created from detailed_parametrize(),
    containing the entity_id, page, start and end years, table page,
    and table length.
    Note that 'page' encodes the page to be scraped, such as
    Candidates, IndividualContributions, etc. Refer to the
    AZ_pages_dict dictionary for details.
    headers: necessary for calling the response, provided above
    data: necessary for calling the response, provided above
    """

    return requests.post(
        "https://seethemoney.az.gov/Reporting/GetNEWDetailedTableData/",
        params=detailed_params,
        # cookies=cookies,
        headers=AZ_head,
        data=AZ_base_data,
    )


def parametrize(
    page=1,
    start_year=2023,
    end_year=2025,
    table_page=1,
    table_length=500000,
    **kwargs: int
) -> dict:
    """Input parameters for scrape and return as dict

    This function takes in parameters to scrape a
    given section of the arizona database, and turns
    them into a dictionary to be fed into scrape() as params

    Kwargs: page: encodes the page to be scraped, such as
    Candidates, Individual Contributions, etc. Refer to the
    AZ_pages_dict dictionary for details.
    start_year: earliest year to include scraped data, inclusive
    end_year: last year to include scraped data, inclusive
    table_page: the numbered page to be accessed. Only necessary
    to iterate on this if accessing large quantities of Individual
    Contributions data, as all other data will be captured whole by
    the default table_length
    table_length: the length of the table to be scraped. The default
    setting should scrape the entirety of the desired data unless
    looking at Individual Contributions

    Returns: a dictionary of the parameters, to be fed into scrape()
    """
    return {
        "Page": str(page),  # refers to the overall page, like candidates
        # or individual expenditures
        "startYear": str(start_year),
        "endYear": str(end_year),
        "JurisdictionId": "0|Page",  # we keep this in here,
        # but don't use it, not sure what it does?
        "TablePage": str(table_page),
        "TableLength": str(table_length),
        "ChartName": str(page),
        "IsLessActive": "false",  # have yet to experiment with these
        "ShowOfficeHolder": "false",  # have yet to experiment with these
    }


def detailed_parametrize(
    entity_id,
    page=1,
    start_year=2023,
    end_year=2025,
    table_page=1,
    table_length=500000,
    *args: int,
    **kwargs: int
) -> dict:
    """ """
    return {
        "Page": str(page),  # refers to the overall page, like candidates
        # or individual expenditures
        "startYear": str(start_year),
        "endYear": str(end_year),
        "JurisdictionId": "0|Page",  # we keep this in here,
        # but don't use it, not sure what it does?
        "TablePage": str(table_page),
        "TableLength": str(table_length),
        "Name": "1~" + str(entity_id),  # these two get used
        # when scraping detailed data
        "entityId": str(entity_id),
        "ChartName": str(page),
        "IsLessActive": "false",  # have yet to experiment with these
        "ShowOfficeHolder": "false",  # have yet to experiment with these
    }

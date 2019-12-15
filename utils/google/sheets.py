import pandas as pd
from loguru import logger

from utils.google import GoogleClient

client = GoogleClient()


def get_df_from_google_sheets(
    spreadsheet_id: str, sheet_range_name: str
) -> pd.DataFrame:

    # TODO: Add permissions, NOT FOR ALL
    # client.set_permissions_for_spreadsheet(spreadsheet_id=spreadsheet_id)

    sheet = (
        client.service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_range_name)
        .execute()
    )
    df = pd.DataFrame(list(sheet.values())[2])
    df.columns = df.iloc[0]
    df = df.drop([0])
    return df


def add_row_to_google_sheets(spreadsheet_id: str, input_data: list, range_name: str):
    body = {"values": [input_data]}

    result = (
        client.service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body=body,
            valueInputOption="RAW",
        )
        .execute()
    )
    logger.debug(f"{result['updates']['updatedCells']} cells updated")
    return result


def get_cell_value(spreadsheet_id: str, sheet_name: str, row: int, column: str):
    range_name = f"{sheet_name}!{column}{row}"

    result = (
        client.service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )["values"]
    return result


def write_to_cell(
    spreadsheet_id: str, sheet_name: str, row: int, column: str, input_text: str
):
    range_name = f"{sheet_name}!{column}{row}"
    body = {"values": [[input_text]]}

    result = (
        client.service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body=body,
            valueInputOption="RAW",
        )
        .execute()
    )
    return result


def get_by_data_filter(spreadsheet_id: str, sheet_range_name: str, input_value: str):
    data_filter = {"range": {sheet_range_name}, "criteria": {"value": input_value}}

    get_spreadsheet_by_data_filter_request_body = {
        "data_filters": [data_filter],
        "include_grid_data": False,
    }

    result = (
        client.service.spreadsheets()
        .getByDataFilter(
            spreadsheetId=spreadsheet_id,
            body=get_spreadsheet_by_data_filter_request_body,
        )
        .execute()
    )
    return result

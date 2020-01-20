from typing import Any

import apiclient
import attr
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

from definitions import CONFIG_DIR
from settings import SCOPES

CRED_FILE = CONFIG_DIR / "bot-for-orders-google-cred.json"  # TODO: from AWS S3


@attr.s(auto_attribs=True)
class GoogleClient:
    service: Any = attr.ib(init=False)
    httpAuth: Any = attr.ib(init=False)

    _type: str = attr.ib(default="sheets")
    _version: str = attr.ib(default="v4")

    def __attrs_post_init__(self):
        self.service = self._make_service(self._type, self._version)

    def _make_service(self, service_type: str, version: str):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CRED_FILE, SCOPES
        )
        if not credentials or credentials.invalid:
            raise RuntimeError("Need new Google API credentials")

        self.httpAuth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build(service_type, version, http=self.httpAuth)
        return service

    def set_permissions_for_spreadsheet(self, spreadsheet_id: str):  # TODO: FIX
        driveService = apiclient.discovery.build("drive", "v3", http=self.httpAuth)
        shareRes = (
            driveService.permissions()
            .create(
                fileId=spreadsheet_id,
                body={"type": "anyone", "role": "reader"},
                fields="id",
            )
            .execute()
        )
        return shareRes

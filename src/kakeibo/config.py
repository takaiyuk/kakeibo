from pydantic import BaseModel


class GoogleAPIClientSecret(BaseModel):
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str


GOOGLE_API_KEYS = [k for k in GoogleAPIClientSecret.model_fields.keys()]


class Config(BaseModel):
    slack_token: str
    slack_channel_id: str
    slack_user1: str | None
    slack_user2: str | None
    google_sheet_worksheet_name: str
    google_api_client_secret: GoogleAPIClientSecret

    @classmethod
    def build(cls, envs: dict[str, str], google_api_client_secret: GoogleAPIClientSecret) -> "Config":
        return cls(
            slack_token=envs["SLACK_TOKEN"],
            slack_channel_id=envs["SLACK_CHANNEL_ID"],
            slack_user1=envs["SLACK_USER1"],
            slack_user2=envs["SLACK_USER2"],
            google_sheet_worksheet_name=envs["GOOGLE_SHEET_WORKSHEET_NAME"],
            google_api_client_secret=google_api_client_secret,
        )

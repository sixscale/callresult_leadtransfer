from datetime import datetime


from pydantic import BaseModel, field_validator, Field, AliasPath


def get_current_date():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


class ContactCreationData(BaseModel):
    phone: str = Field(validation_alias=AliasPath("phones", 0), default="")
    email: str = Field(validation_alias=AliasPath("mails", 0), default="")
    date: str = Field(default_factory=get_current_date)
    site: str = Field(validation_alias=AliasPath("site"), default="")
    city: str = Field(validation_alias=AliasPath("city"), default="")
    page: str = Field(validation_alias=AliasPath("page"), default="")

    @field_validator("phone")
    def phone_validator(cls, value):
        remove_symbols = "+_-() "
        for symbol in remove_symbols:
            value = value.replace(symbol, "")
        if value[0] == 8:
            value[0] = 7
        return value


class LeadCreationData(BaseModel):
    utm_source: str = Field(validation_alias=AliasPath("utm", "utm_source"), default="")
    utm_medium: str = Field(validation_alias=AliasPath("utm", "utm_medium"), default="")
    utm_campaign: str = Field(validation_alias=AliasPath("utm", "utm_campaign"), default="")
    utm_content: str = Field(validation_alias=AliasPath("utm", "utm_content"), default="")
    utm_term: str = Field(validation_alias=AliasPath("utm", "utm_term"), default="")
    roistat_visit: str = Field(validation_alias=AliasPath("roistat_visit"), default="")

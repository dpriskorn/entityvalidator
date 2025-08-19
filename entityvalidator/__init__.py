import asyncio
import logging
import re
from re import Pattern
from typing import Any

import aiohttp
import requests
from aiohttp import ClientSession
from pydantic import BaseModel, Field
from rich.console import Console

import config
from entityvalidator.exceptions import (
    ApiError,
    EidError,
    EntityIdError,
    NoEntitySchemaDataError,
    WikibaseEntitySchemaDownloadError,
)
from entityvalidator.models.entity import Entity

console = Console()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class EntityValidator(BaseModel):
    """Downloads and validates Wikidata entities"""

    entity_ids: list[str] = Field(
        ..., min_length=1, description="List of entity IDs, at least one required"
    )
    eid: str = Field(
        ..., min_length=2, description="EntitySchema ID in a Wikibase"
    )  # entityshape
    eid_regex: Pattern = re.compile(r"E\d+")
    wikibase_url: str = "http://www.wikidata.org"
    mediawiki_api_url: str = "https://www.wikidata.org/w/api.php"
    user_agent: str = config.user_agent
    entities: list[Entity] = []
    entity_schema_data: dict[str, Any] = {}

    def __check_inputs__(self) -> None:
        if not re.match(self.eid_regex, self.eid):
            raise EidError("EID has to be E followed by only numbers like this: E100")
        # if not re.match(self.entity_id_regex, self.entity_id):
        #     raise QidError("QID has to be Q followed by only numbers like this: Q100")

    def __download_and_validate__(self) -> None:
        self.__check_inputs__()  # Check if inputs are valid
        self.__download_schema__()
        if not self.entity_schema_data:
            raise NoEntitySchemaDataError("Got no entity schema data from Wikidata")
        with console.status("Downloading entity json"):
            asyncio.run(
                self.__download_json__()
            )  # safely run async without nest_asyncio
        print(f"Downloaded {len(self.entities)} entities")
        if self.entities:
            with console.status("Validating entities"):
                for entity in self.entities:
                    entity.check_and_validate()
            print("Validation finished")
        else:
            print("No entities to validate")

    async def __download_json__(self) -> None:
        """Get all the JSON data we need asynchronously"""
        logger.debug("__download_json__: running")
        async with aiohttp.ClientSession() as session:
            # Create tasks for downloading JSON data for each entity_id
            tasks = [
                self._get_entity_json(entity_id, session)
                for entity_id in self.entity_ids
            ]

            # Gather and wait for all tasks to complete
            await asyncio.gather(*tasks)
            # self.json_responses = await asyncio.gather(*tasks)
            # Handle results as needed
            # We don't handle the results for now.

    async def _get_entity_json(self, entity_id: str, session: ClientSession) -> None:
        """
        Downloads the entity from Wikidata asynchronously
        """
        logger.debug("_get_entity_json: running")
        url = f"{self.wikibase_url}/wiki/Special:EntityData/{entity_id}.json"
        headers = {"User-Agent": config.user_agent}

        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                entity_data = await response.json()
                self.entities.append(
                    Entity(
                        entity_id=entity_id,
                        entity_data=entity_data,
                        eid=self.eid,
                        entity_schema_data=self.entity_schema_data,
                    )
                )
            else:
                raise WikibaseEntitySchemaDownloadError(
                    f"Got {response.status} from {url}. "
                    f"Please check that the configuration is correct"
                )

    def __download_schema__(self) -> None:
        """
        Downloads the schema from wikidata
        """
        url: str = f"https://www.wikidata.org/wiki/EntitySchema:{self.eid}?action=raw"
        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            raise WikibaseEntitySchemaDownloadError()
        self.entity_schema_data: dict = response.json()

    @property
    def get_results(self) -> list[dict[str, Any]]:
        self.__download_and_validate__()
        return [e.to_dict() for e in self.entities]

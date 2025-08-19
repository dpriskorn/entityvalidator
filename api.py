import logging
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Query
from starlette.responses import RedirectResponse

import config
from entityvalidator import (
    ApiError,
    EidError,
    EntityIdError,
    EntityValidator,
    WikibaseEntitySchemaDownloadError,
)
from entityvalidator.exceptions import (
    MissingInformationError,
    NoEntitySchemaDataError,
    WikibasePropertiesDownloadError,
)

app = FastAPI()
logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)
router = APIRouter()


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")


@router.get("/validate")
def validate_entities(
    # mandatory
    eid: str = Query(..., description="EntitySchema ID, ex. E100"),
    entity_ids: str = Query(
        ..., description="Comma-separated list of entity IDs, e.g. Q42,Q43"
    ),
) -> dict[str, Any]:
    """
    Validate a list of entity IDs against a specific Wikibase entity schema.

    Args:
        eid (str): The EntitySchema ID to validate against (e.g., "E100").
        entity_ids (str): A comma-separated list of entity IDs to validate (max 100 IDs).

    Returns:
        dict: A dictionary containing the validation results:
            - results (list): Details of the validation.

    Raises:
        HTTPException: Raised in case of validation failure, missing data, API errors,
                       or unexpected exceptions.
    """
    # Split by comma and strip whitespace
    entity_list = [e.strip() for e in entity_ids.split(",") if e.strip()]

    # Validate at least 1 entity
    if not entity_list:
        raise HTTPException(
            status_code=400, detail="At least one entity ID must be provided."
        )

    # Optional: validate max length
    if len(entity_list) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 entity IDs allowed.")
    try:
        entity_shape = EntityValidator(
            entity_ids=entity_list,
            eid=eid,
        )
        entity_shape.download_and_validate()

        return {
            "results": [e.to_dict() for e in entity_shape.entities],
        }

    except (EntityIdError, EidError) as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "Invalid entity id", "message": str(e)},
        ) from e
    except ApiError as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "Upstream API failed", "message": str(e)},
        ) from e
    except (WikibaseEntitySchemaDownloadError, WikibasePropertiesDownloadError) as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "Wikibase download failed", "message": str(e)},
        ) from e
    except (NoEntitySchemaDataError, MissingInformationError) as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "Missing data", "message": str(e)},
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during validation")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


app.include_router(router, prefix="/v1")

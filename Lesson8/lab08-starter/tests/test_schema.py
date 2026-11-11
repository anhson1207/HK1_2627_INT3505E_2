
import pytest
from jsonschema import validate, ValidationError


def test_response_extra_field_blocked(
    client, sample_book
):
    response = client.get(
        f"/books/{sample_book}"
    )

    assert response.status_code == 200
    book = response.get_json()

    schema = {
        "type": "object",
        "properties": {
            "id": {},
            "title": {},
            "author": {},
            "year": {},
            "isbn": {}
        },
        "additionalProperties": False
    }


    validate(instance=book, schema=schema)


    invalid_book = {
        **book,
        "password_hash": "secret123"
    }


    with pytest.raises(ValidationError):
        validate(
            instance=invalid_book,
            schema=schema
        )

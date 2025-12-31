import io
import pandas as pd
import pytest
from fastapi import UploadFile, HTTPException
from app.utils.functions import (
    get_client_from_context,
    convert_to_json,
    sort_object,
    object_to_sha,
    client_context,
)

def test_get_client_from_context():
    client_context.set("client_123")
    result = get_client_from_context()
    assert result == "client_123"
    client_context.set(None)


@pytest.mark.asyncio
async def test_convert_to_json_csv_success(sample_csv_content):
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(sample_csv_content)
    )

    response = await convert_to_json(file)

    assert response["status"] == "200"
    assert len(response["data"]) == 2
    assert response["data"][0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_convert_to_json_xlsx_success(tmp_path):
    df = pd.DataFrame([{"name": "John", "age": 40}])
    file_path = tmp_path / "data.xlsx"
    df.to_excel(file_path, index=False)

    with open(file_path, "rb") as f:
        file = UploadFile(
            filename="data.xlsx",
            file=io.BytesIO(f.read())
        )

        response = await convert_to_json(file)

    assert response["status"] == "200"
    assert response["data"][0]["name"] == "John"


@pytest.mark.asyncio
async def test_convert_to_json_invalid_extension():
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"data")
    )

    with pytest.raises(HTTPException) as exc:
        await convert_to_json(file)

    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_convert_to_json_no_filename():
    file = UploadFile(
        filename=None,
        file=io.BytesIO(b"data")
    )

    with pytest.raises(HTTPException) as exc:
        await convert_to_json(file)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_convert_to_json_processing_error(invalid_file_content):
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(invalid_file_content)
    )

    with pytest.raises(HTTPException) as exc:
        await convert_to_json(file)

    assert exc.value.status_code == 500


def test_sort_object_dict():
    obj = {"b": 2, "a": 1}
    result = sort_object(obj)

    assert list(result.keys()) == ["a", "b"]

def test_sort_object_list_of_strings():
    obj = ["Banana", "apple", "cherry"]
    result = sort_object(obj)

    assert result == ["apple", "Banana", "cherry"]

def test_sort_object_list_of_dicts_by_name():
    obj = [
        {"NAME": "Charlie"},
        {"NAME": "alice"},
        {"NAME": "Bob"},
    ]

    result = sort_object(obj)
    names = [i["NAME"] for i in result]

    assert names == ["alice", "Bob", "Charlie"]


def test_object_to_sha_same_data_same_hash():
    obj1 = {"b": 2, "a": 1}
    obj2 = {"a": 1, "b": 2}

    assert object_to_sha(obj1) == object_to_sha(obj2)


def test_object_to_sha_different_data():
    assert object_to_sha({"a": 1}) != object_to_sha({"a": 2})


def test_object_to_sha_name_sorting():
    obj1 = [{"NAME": "Bob"}, {"NAME": "Alice"}]
    obj2 = [{"NAME": "Alice"}, {"NAME": "Bob"}]

    assert object_to_sha(obj1) == object_to_sha(obj2)

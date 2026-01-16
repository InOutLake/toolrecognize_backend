import pytest

# Test data for storage
STORAGE_DATA = {"name": "Main Warehouse", "address": "123 Main St, City, State"}

UPDATED_STORAGE_DATA = {
    "name": "Updated Warehouse",
    "address": "456 Updated St, City, State",
}


@pytest.mark.asyncio
async def test_create_storage(async_client):
    """Test creating a new storage location."""
    response = await async_client.post("/storage", json=[STORAGE_DATA])
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == STORAGE_DATA["name"]
    assert data[0]["address"] == STORAGE_DATA["address"]

    return data[0]["id"]


@pytest.mark.asyncio
async def test_list_storages(async_client):
    """Test listing all storage locations."""
    create_response = await async_client.post("/storage", json=[STORAGE_DATA])
    assert create_response.status_code == 200

    response = await async_client.get("/storage")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page_number" in data
    assert "page_size" in data

    # At least one storage should be present
    assert len(data["items"]) >= 1
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_storages_with_filters(async_client):
    """Test listing storage locations with filters."""
    # Create a storage to ensure there's at least one
    create_response = await async_client.post("/storage", json=[STORAGE_DATA])
    assert create_response.status_code == 200

    # Test filtering by name
    response = await async_client.get(f"/storage?name={STORAGE_DATA['name']}")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    filtered_items = data["items"]
    for item in filtered_items:
        assert STORAGE_DATA["name"] in item["name"]

    # Test filtering by address
    response = await async_client.get(f"/storage/?address={STORAGE_DATA['address']}")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    filtered_items = data["items"]
    for item in filtered_items:
        assert STORAGE_DATA["address"] in item["address"]


@pytest.mark.asyncio
async def test_update_storage(async_client):
    """Test updating an existing storage location."""
    # First create a storage
    create_response = await async_client.post("/storage", json=[STORAGE_DATA])
    assert create_response.status_code == 200

    created_data = create_response.json()
    assert len(created_data) == 1
    storage_id = created_data[0]["id"]

    # Update the storage
    response = await async_client.put(
        f"/storage/{storage_id}", json=UPDATED_STORAGE_DATA
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == storage_id["id"]
    assert data["name"] == UPDATED_STORAGE_DATA["name"]
    assert data["address"] == UPDATED_STORAGE_DATA["address"]


@pytest.mark.asyncio
async def test_get_storage_details_after_creation_and_update(async_client):
    """Test getting storage details after creation and update."""
    # First create a storage
    create_response = await async_client.post("/storage", json=[STORAGE_DATA])
    assert create_response.status_code == 200

    created_data = create_response.json()
    assert len(created_data) == 1
    storage_data = created_data[0]

    update_data = {"name": "NewName"}

    response = await async_client.put(
        f"/storage/{storage_data['id']}", json=update_data
    )
    print(response)
    assert response == 200

    # Get the storage details
    response = await async_client.get(f"/storage/{storage_data['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == storage_data["id"]
    assert data["name"] == update_data["name"]
    assert data["address"] == STORAGE_DATA["address"]


@pytest.mark.asyncio
async def test_delete_storage(async_client):
    """Test deleting a storage location."""
    # First create a storage
    create_response = await async_client.post("/storage", json=[STORAGE_DATA])
    assert create_response.status_code == 200

    created_data = create_response.json()
    assert len(created_data) == 1
    storage_id = created_data[0]["id"]

    # Delete the storage
    response = await async_client.delete(f"/storage/{storage_id}")
    assert response.status_code == 200

    # Verify the storage is gone by trying to get it
    get_response = await async_client.get(f"/storage/{storage_id}")
    assert get_response == 404


@pytest.mark.asyncio
async def test_bulk_create_storages(async_client):
    """Test creating multiple storages at once."""
    multiple_storages = [
        {"name": "Warehouse A", "address": "Address A"},
        {"name": "Warehouse B", "address": "Address B"},
        {"name": "Warehouse C", "address": "Address C"},
    ]

    response = await async_client.post("/storage", json=multiple_storages)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    for i, storage in enumerate(data):
        assert storage["name"] == multiple_storages[i]["name"]
        assert storage["address"] == multiple_storages[i]["address"]


@pytest.mark.asyncio
async def test_invalid_storage_data(async_client):
    """Test creating storage with invalid data."""
    invalid_data = [{"name": "", "address": ""}]

    response = await async_client.post("/storage", json=invalid_data)
    assert response.status_code in [200, 422]  # 422 for validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import pytest
from googlemaps import Client, exceptions
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_client():
    client = MagicMock(spec=Client)
    client._request = MagicMock()
    return client

def test_addressvalidation_success(mock_client):
    mock_client._request.return_value = {"result": "valid_address"}
    from googlemaps.addressvalidation import addressvalidation

    response = addressvalidation(mock_client, ["1600 Amphitheatre Parkway", "Mountain View", "CA"])
    assert response == {"result": "valid_address"}
    mock_client._request.assert_called_once()

def test_addressvalidation_with_region(mock_client):
    mock_client._request.return_value = {"result": "valid_address"}
    from googlemaps.addressvalidation import addressvalidation

    response = addressvalidation(mock_client, ["1600 Amphitheatre Parkway", "Mountain View", "CA"], regionCode="US")
    assert response == {"result": "valid_address"}
    mock_client._request.assert_called_once()

def test_addressvalidation_with_locality(mock_client):
    mock_client._request.return_value = {"result": "valid_address"}
    from googlemaps.addressvalidation import addressvalidation

    response = addressvalidation(mock_client, ["1600 Amphitheatre Parkway"], locality="Mountain View")
    assert response == {"result": "valid_address"}
    mock_client._request.assert_called_once()

def test_addressvalidation_with_usps_cass(mock_client):
    mock_client._request.return_value = {"result": "valid_address"}
    from googlemaps.addressvalidation import addressvalidation

    response = addressvalidation(mock_client, ["1600 Amphitheatre Parkway"], enableUspsCass=True)
    assert response == {"result": "valid_address"}
    mock_client._request.assert_called_once()

def test_addressvalidation_invalid_address(mock_client):
    mock_client._request.side_effect = exceptions.ApiError(400, "Invalid address")
    from googlemaps.addressvalidation import addressvalidation

    with pytest.raises(exceptions.ApiError):
        addressvalidation(mock_client, ["Invalid Address"])

def test_directions_success(mock_client):
    mock_client._request.return_value = {"routes": ["route1", "route2"]}
    from googlemaps.directions import directions

    response = directions(mock_client, "origin", "destination")
    assert response == ["route1", "route2"]
    mock_client._request.assert_called_once()

def test_directions_invalid_mode(mock_client):
    from googlemaps.directions import directions

    with pytest.raises(ValueError):
        directions(mock_client, "origin", "destination", mode="invalid_mode")

def test_distance_matrix_success(mock_client):
    mock_client._request.return_value = {"rows": ["row1", "row2"]}
    from googlemaps.distance_matrix import distance_matrix

    response = distance_matrix(mock_client, "origin", "destination")
    assert response == {"rows": ["row1", "row2"]}
    mock_client._request.assert_called_once()

def test_distance_matrix_invalid_mode(mock_client):
    from googlemaps.distance_matrix import distance_matrix

    with pytest.raises(ValueError):
        distance_matrix(mock_client, "origin", "destination", mode="invalid_mode")

def test_geocode_success(mock_client):
    mock_client._request.return_value = {"results": ["result1", "result2"]}
    from googlemaps.geocoding import geocode

    response = geocode(mock_client, address="1600 Amphitheatre Parkway")
    assert response == ["result1", "result2"]
    mock_client._request.assert_called_once()

def test_geocode_invalid_address(mock_client):
    mock_client._request.side_effect = exceptions.ApiError(400, "Invalid address")
    from googlemaps.geocoding import geocode

    with pytest.raises(exceptions.ApiError):
        geocode(mock_client, address="Invalid Address")

def test_reverse_geocode_success(mock_client):
    mock_client._request.return_value = {"results": ["result1", "result2"]}
    from googlemaps.geocoding import reverse_geocode

    response = reverse_geocode(mock_client, latlng="37.421999,-122.084057")
    assert response == ["result1", "result2"]
    mock_client._request.assert_called_once()

def test_reverse_geocode_invalid_latlng(mock_client):
    mock_client._request.side_effect = exceptions.ApiError(400, "Invalid latlng")
    from googlemaps.geocoding import reverse_geocode

    with pytest.raises(exceptions.ApiError):
        reverse_geocode(mock_client, latlng="Invalid LatLng")

def test_timezone_success(mock_client):
    mock_client._request.return_value = {"dstOffset": 3600, "rawOffset": -28800}
    from googlemaps.timezone import timezone

    response = timezone(mock_client, location=(37.421999, -122.084057))
    assert response == {"dstOffset": 3600, "rawOffset": -28800}
    mock_client._request.assert_called_once()

def test_timezone_invalid_location(mock_client):
    mock_client._request.side_effect = exceptions.ApiError(400, "Invalid location")
    from googlemaps.timezone import timezone

    with pytest.raises(exceptions.ApiError):
        timezone(mock_client, location="Invalid Location")

from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.utils.image_client import MODEL, generate_image


@patch("social_campaign.utils.image_client._get_client")
def test_generate_image_returns_pil_image(mock_get_client):
    mock_client = MagicMock()
    fake_image = Image.new("RGB", (1024, 1024), color="red")
    mock_client.text_to_image.return_value = fake_image
    mock_get_client.return_value = mock_client

    result = generate_image("A sparkling water bottle on a beach")

    assert isinstance(result, Image.Image)
    assert result.size == (1024, 1024)
    mock_client.text_to_image.assert_called_once()
    call_kwargs = mock_client.text_to_image.call_args
    assert call_kwargs.kwargs["model"] == MODEL

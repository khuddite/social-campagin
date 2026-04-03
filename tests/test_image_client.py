from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.utils.image_client import MODEL, generate_image


@patch("social_campaign.utils.image_client.InferenceClient")
def test_generate_image_returns_pil_image(mock_client_cls):
    mock_client = MagicMock()
    fake_image = Image.new("RGB", (1024, 1024), color="red")
    mock_client.text_to_image.return_value = fake_image
    mock_client_cls.return_value = mock_client

    result = generate_image("A sparkling water bottle on a beach")

    assert isinstance(result, Image.Image)
    assert result.size == (1024, 1024)
    mock_client.text_to_image.assert_called_once()
    call_kwargs = mock_client.text_to_image.call_args
    assert call_kwargs.kwargs["model"] == MODEL


@patch("social_campaign.utils.image_client.InferenceClient")
def test_generate_image_aspect_ratio_ignored_gracefully(mock_client_cls):
    """FLUX.1 only does square — aspect_ratio param is accepted but ignored."""
    mock_client = MagicMock()
    mock_client.text_to_image.return_value = Image.new("RGB", (1024, 1024))
    mock_client_cls.return_value = mock_client

    result = generate_image("wide background", aspect_ratio="16:9")

    assert result.size == (1024, 1024)

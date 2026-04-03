import base64
import io
from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.utils.image_client import generate_image, generate_transparent_image


def _fake_png_b64() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (1024, 1024), color="red").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@patch("social_campaign.utils.image_client._get_client")
def test_generate_image_returns_rgb(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(b64_json=_fake_png_b64())]
    mock_client.images.generate.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = generate_image("A background scene")

    assert isinstance(result, Image.Image)
    assert result.size == (1024, 1024)
    assert result.mode == "RGB"
    assert mock_client.images.generate.call_args.kwargs["model"] == "dall-e-3"


def _fake_rgba_b64() -> str:
    buf = io.BytesIO()
    Image.new("RGBA", (1024, 1024), (255, 0, 0, 200)).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@patch("social_campaign.utils.image_client._get_client")
def test_generate_transparent_image_returns_rgba(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(b64_json=_fake_rgba_b64())]
    mock_client.images.generate.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = generate_transparent_image("A product cutout")

    assert isinstance(result, Image.Image)
    assert result.size == (1024, 1024)
    assert result.mode == "RGBA"
    assert mock_client.images.generate.call_args.kwargs["model"] == "gpt-image-1.5"
    assert mock_client.images.generate.call_args.kwargs["background"] == "transparent"

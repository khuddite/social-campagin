import base64
import io
from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.utils.image_client import MODEL, generate_image


def _fake_png_b64() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (1024, 1024), color="red").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@patch("social_campaign.utils.image_client._get_client")
def test_generate_image_returns_pil_image(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(b64_json=_fake_png_b64())]
    mock_client.images.generate.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = generate_image("A sparkling water bottle on a beach")

    assert isinstance(result, Image.Image)
    assert result.size == (1024, 1024)
    mock_client.images.generate.assert_called_once()
    call_kwargs = mock_client.images.generate.call_args.kwargs
    assert call_kwargs["model"] == MODEL

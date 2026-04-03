import base64
import io
from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.utils.openai_image_client import MODEL, SIZE, generate_image


def _fake_png_b64() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (1024, 1024), color="red").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@patch("social_campaign.utils.openai_image_client.OpenAI")
def test_generate_image_returns_pil_image(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.data = [MagicMock(b64_json=_fake_png_b64())]
    mock_client.images.generate.return_value = mock_response

    result = generate_image("A sparkling water bottle on a beach")

    assert isinstance(result, Image.Image)
    assert result.size == (1024, 1024)
    mock_client.images.generate.assert_called_once()
    call_kwargs = mock_client.images.generate.call_args.kwargs
    assert call_kwargs["model"] == MODEL
    assert call_kwargs["size"] == SIZE
    assert call_kwargs["response_format"] == "b64_json"

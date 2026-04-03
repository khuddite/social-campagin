from unittest.mock import MagicMock, patch

from social_campaign.agents.copy_writer import write_copy
from social_campaign.models import CopyVariant


@patch("social_campaign.agents.copy_writer.ChatOpenAI")
def test_write_copy_generates_for_all_products(mock_chat_cls, campaign_state):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"headline": "Stay Fresh", "body": "Keep it cool all day."}'
    )
    mock_chat_cls.return_value = mock_llm

    result = write_copy(campaign_state)

    assert "copy_variants" in result
    assert "product-a" in result["copy_variants"]
    assert "product-b" in result["copy_variants"]
    assert isinstance(result["copy_variants"]["product-a"], CopyVariant)
    assert mock_llm.invoke.call_count == 2

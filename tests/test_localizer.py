from unittest.mock import MagicMock, patch

from social_campaign.agents.localizer import localize_copy
from social_campaign.models import LocalizedCopy


@patch("social_campaign.agents.localizer.ChatOpenAI")
def test_localize_copy_translates_and_adapts(mock_chat_cls, campaign_state):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"headline": "Fique Fresco", "body": "Mantenha a frescura."}'
    )
    mock_chat_cls.return_value = mock_llm

    result = localize_copy(campaign_state)

    assert "localized_copy" in result
    assert "product-a" in result["localized_copy"]
    lc = result["localized_copy"]["product-a"]
    assert isinstance(lc, LocalizedCopy)
    assert lc.language == "pt-BR"
    assert lc.headline == "Fique Fresco"

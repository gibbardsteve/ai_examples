import pytest

from typing import List
from ai_examples.example_one import get_openai_models

# ---- Constant Definitions ----
EXCEPTION_FAIL_MESSAGE = (
    "{test_id} : Expected no exception, but got {exception_type}: {exception_msg}"
)


class TestGetOpenAIModels:
    @pytest.mark.parametrize(
        "api_key_env_name, model, expected_result, test_id",
        [
            (
                "OPENAI_KEY",  # api_key_env_name
                "gpt-4",  # model
                True,  # expected_result
                "Example 1: Test 1 - List of models returned, gpt-4 found",  # test_id
            ),
            (
                "BADKEY",  # api_key_env_name
                "gpt-4",  # model
                None,  # expected_result
                "Example 1: Test 2 - API key not found",  # test_id
            ),
            (
                "OPENAI_KEY",  # api_key_env_name
                "gpt-5",  # model
                False,  # expected_result
                "Example 1: Test 3 - List returned, model not found",  # test_id
            ),
        ],
    )
    def test_get_openai_models(self, api_key_env_name, model, expected_result, test_id):
        try:
            model_list = get_openai_models(api_key_env_name)

            if model_list is not None:
                assert modelFound(model, model_list["data"]) is expected_result
            else:
                assert expected_result is None
        except Exception as e:
            pytest.fail(
                EXCEPTION_FAIL_MESSAGE.format(
                    test_id=test_id,
                    exception_type=type(e).__name__,
                    exception_msg=str(e.args),
                )
            )


def modelFound(model_name: str, model_data: List) -> bool:
    """_summary_

    :param model_name: _description_
    :type model_name: str
    :param model_data: _description_
    :type model_data: List
    :return: _description_
    :rtype: bool
    """
    found = False
    for model in model_data:
        if model["id"] == model_name:
            found = True
    return found

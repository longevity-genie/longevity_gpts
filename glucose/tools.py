"""
Here there should be a tool (function)
1)
"""
from pprint import pprint

from dotenv import load_dotenv
from litellm import completion


def predict_glucose_tool(url: str, model: str,
                         predict_future: bool = True) -> str:
    """
    :param url: of the csv file with glucose values
    :param model: model that is used to predict the glucose
    :param predict_future: predicts future values if true, otherwise evaluates last values and plots on ground truth
    :return:
    """
    """
    this function will be called by LLM
    """
    return "The answer which contains url to generated chart and textual explanation of the chart"


def explain_image(
    prompt: str = "Explain glucose predictions and possible health outcomes on the chat",
    url: str = "https://github.com/IrinaStatsLab/GlucoBench/blob/main/paper_results/plots/figure6.png?raw=true",
    model: str = "gpt-4o"):
    """
    function that explains the image
    :param prompt:
    :param url:
    :param model: model with vision support
    :return:
    """
    load_dotenv(override=True)
    # openai call
    response = completion(
        model = "gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url
                        }
                    }
                ]
            }
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    test = explain_image()
    pprint(test)
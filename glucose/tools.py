"""
Here there should be a tool (function)
1)
"""
from pprint import pprint

from dotenv import load_dotenv
from litellm import completion
from format_dexcom import *
from plot_predictions import *
from datetime import date
import typer


file_directory = Path("./glucose/files")

def predict_glucose_tool(url: str= typer.Argument('', help="url of the csv donwloaded in CGM original format (DEXCOM)"),
                        user_name:str= typer.Argument('', help="name/id under which to store data for processing."),
                        model: str= typer.Argument('', help="model with weights used for predicting."),
                        predict_future: bool = True) -> str:
    """
    :param url: of the csv file with glucose values
    :param user_name: the name the cvs and file will be stored later
    :param model: model that is used to predict the glucose
    :param predict_future: predicts future values if true, otherwise evaluates last values and plots on ground truth
    :return:
    """

    #get the file and convert it to normal processing format. saves it to server

    today = date.today()
    save_location_pdf=str(file_directory/f'{today}')
    save_location_csv=str(file_directory/f'{today}'/f'{user_name}')+".csv"
    process_csv(url,save_location_csv)
    plotting_graph(save_location_pdf, user_name,save_location_csv)
    #plotting(save_location_pdf, user_name, model)



    
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
    typer.run(predict_glucose_tool)
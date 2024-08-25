"""
Here there should be a tool (function)
1)
"""
import hashlib
import os
from urllib.parse import urlparse
import typer
from dotenv import load_dotenv
from just_agents.llm_session import LLMSession
from litellm import completion
from requests import session

from plot_predictions import *
import numpy as np

glucose = Path(os.path.abspath(__file__)).parent.resolve()
file_directory = glucose / "files"
models_directory = glucose / "models"

def filename_to_url(name: str):
    load_dotenv(override=True)
    host = os.getenv("HOST","http://0.0.0.0")
    port = os.getenv("CHAT_PORT",)
    return f"{host}:{port}/view/{name}"


def plot_forecast(forecasts: np.ndarray, scalers: Any, dataset_test_glufo: Any, filename: str):
    print(forecasts.shape)
    filename=filename
    forecasts = (forecasts - scalers['target'].min_) / scalers['target'].scale_

    trues = [dataset_test_glufo.evalsample(i) for i in range(len(dataset_test_glufo))]
    trues = scalers['target'].inverse_transform(trues)

    trues = [ts.values() for ts in trues]  # Convert TimeSeries to numpy arrays
    trues = np.array(trues)

    inputs = [dataset_test_glufo[i][0] for i in range(len(dataset_test_glufo))]
    inputs = (np.array(inputs) - scalers['target'].min_) / scalers['target'].scale_

    # Plot settings
    colors = ['#00264c', '#0a2c62', '#14437f', '#1f5a9d', '#2973bb', '#358ad9', '#4d9af4', '#7bb7ff', '#add5ff', '#e6f3ff']
    cmap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)
    sns.set_theme(style="whitegrid")

    # Generate the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Select a specific sample to plot
    ind = 30  # Example index

    samples = np.random.normal(
        loc=forecasts[ind, :],  # Mean (center) of the distribution
        scale=0.1,  # Standard deviation (spread) of the distribution
        size=(forecasts.shape[1], forecasts.shape[2])
    )
    #samples = samples.reshape(samples.shape[0], samples.shape[1], -1)
    print ("samples",samples.shape)

    # Plot predictive distribution
    for point in range(samples.shape[0]):
        kde = stats.gaussian_kde(samples[point,:])
        maxi, mini = 1.2 * np.max(samples[point, :]), 0.8 * np.min(samples[point, :])
        y_grid = np.linspace(mini, maxi, 200)
        x = kde(y_grid)
        ax.fill_betweenx(y_grid, x1=point, x2=point - x * 15,
                         alpha=0.7,
                         edgecolor='black',
                         color=cmap(point / samples.shape[0]))

    # Plot median
    forecast = samples[:, :]
    median = np.quantile(forecast, 0.5, axis=-1)
    ax.plot(np.arange(12), median, color='red', marker='o')

    # Plot true values
    ax.plot(np.arange(-12, 12), np.concatenate([inputs[ind, -12:], trues[ind, :]]), color='blue')

    # Add labels and title
    ax.set_xlabel('Time (in 5 minute intervals)')
    ax.set_ylabel('Glucose (mg/dL)')
    ax.set_title(f'Gluformer Prediction with Gradient for dateset')

    # Adjust font sizes
    ax.xaxis.label.set_fontsize(16)
    ax.yaxis.label.set_fontsize(16)
    ax.title.set_fontsize(18)
    for item in ax.get_xticklabels() + ax.get_yticklabels():
        item.set_fontsize(14)

    # Save figure
    plt.tight_layout()
    where = file_directory /filename
    plt.savefig(str(where), dpi=300, bbox_inches='tight')
    #plt.savefig(f'output/plots/gluformer_prediction_gradient_{dataset}_{ind}.png', dpi=300, bbox_inches='tight')
    #plt.show()
    return where

def generate_filename_from_url(url: str, extension: str = "png") -> str:
    """
    :param url:
    :param extension:
    :return:
    """
    # Extract the last segment of the URL
    last_segment = urlparse(url).path.split('/')[-1]

    # Compute the hash of the URL
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()

    # Create the filename
    filename = f"{last_segment.replace('.','_')}_{url_hash}.{extension}"

    return filename

def predict_glucose_tool(url: str= typer.Option("https://raw.githubusercontent.com/GlucoseDAO/GlucoBench/livia/raw_data/anton.csv", help="url of the csv donwloaded in CGM original format (DEXCOM)"),
                        model: str= typer.Option('gluformer_1samples_10000epochs_10heads_32batch_geluactivation_anton_weights.pth', help="model with weights used for predicting."),
                        explain: bool = False
                    ) -> str:
    """
    Function to predict future glucose of user. It receives URL with users csv. It will run an ML and will return URL with predictions that user can open on her own..
    :param url: of the csv file with glucose values
    :param user_name: the name the cvs and file will be stored later
    :param model: model that is used to predict the glucose
    :param predict_future: predicts future values if true, otherwise evaluates last values and plots on ground truth
    :return:
    """

    #get the file and convert it to normal processing format. saves it to server


    #plotting(save_location_pdf, user_name, model)
    #plotting_graph(save_location_pdf, user_name,save_location_csv)
    #df = pl.read_csv(url)
    #print (df)
    #predict()
    formatter, series, scalers = load_data(url, file_directory / "config.yaml", use_covs=True,
                                           cov_type='dual',
                                           use_static_covs=True)

    filename = generate_filename_from_url(url)

    formatter.params['gluformer'] = {
        'in_len': 96,  # example input length, adjust as necessary
        'd_model': 512,  # model dimension
        'n_heads': 10,  # number of attention heads##############################################################################
        'd_fcn': 1024,  # fully connected layer dimension
        'num_enc_layers': 2,  # number of encoder layers
        'num_dec_layers': 2,  # number of decoder layers
        'length_pred': 12  # prediction length, adjust as necessary
    }

    num_dynamic_features = series['train']['future'][-1].n_components
    num_static_features = series['train']['static'][-1].n_components
    #num_dynamic_features = 6
    #num_static_features = 1

    glufo = Gluformer(
        d_model=formatter.params['gluformer']['d_model'],
        n_heads=formatter.params['gluformer']['n_heads'],
        d_fcn=formatter.params['gluformer']['d_fcn'],
        r_drop=0.2,
        activ='gelu',
        num_enc_layers=formatter.params['gluformer']['num_enc_layers'],
        num_dec_layers=formatter.params['gluformer']['num_dec_layers'],
        distil=True,
        len_seq=formatter.params['gluformer']['in_len'],
        label_len=formatter.params['gluformer']['in_len'] // 3,
        len_pred=formatter.params['length_pred'],
        num_dynamic_features=num_dynamic_features,
        num_static_features=num_static_features
    )
    weights = models_directory / model
    assert f"weights for {model} should exist", weights.exists()
    glufo.load_state_dict(torch.load(str(weights), map_location=torch.device('cuda'), weights_only=False))

    # Define dataset for inference
    dataset_test_glufo = SamplingDatasetInferenceDual(
        target_series=series['test']['target'],
        covariates=series['test']['future'],
        input_chunk_length=formatter.params['gluformer']['in_len'],
        output_chunk_length=formatter.params['length_pred'],
        use_static_covariates=True,
        array_output_only=True
    )

    forecasts, _ = glufo.predict(
        dataset_test_glufo,
        batch_size=16,####################################################
        num_samples=10,
        device='cpu'
    )
    figure_path = plot_forecast(forecasts, scalers, dataset_test_glufo,filename)
    figure_url = filename_to_url(filename)
    print(figure_path, figure_url)
    return figure_url


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

def get_session(options_llm: dict) -> LLMSession:
    tools = [predict_glucose_tool]
    session: LLMSession = LLMSession(
        llm_options=options_llm,
        tools=tools
    )
    return session


if __name__ == "__main__":
    load_dotenv(override=True)
    gpt_4o_mini_glucose = {
        "model": "gpt-4o-mini",
        "temperature": 0
    }

    session = get_session(gpt_4o_mini_glucose)

    system = """
    You are a medical doctor with deep expertise in diabetes, personalized medicine, longevity and biohacking, you love checking latest research.
Your task is to advice people using CGMs both diabetic and non-diabetic, those who optimize diet, health and exercise.
You do your best to give the most comprehensive,  clear and easy to understand advice, you are open to new health optimization applications and you always search for the scientific studies that you can reference in your answers.
In your answers you try not only explaining the general terms but also understand users health situation.
You clarify if she is diabetic, pre-diabetic or healthy in case it is required for the answer and when it's not clear from the questions.
You try to follow instructions closely.
When you run glucose prediction tool it will return the url which you cannot open but you have to write it to the user as she will open it herself
    """


    session.instruct(system)
    question = """
    Here is my glucose values https://raw.githubusercontent.com/GlucoseDAO/GlucoBench/livia/raw_data/anton.csv please forecast glucose changes
    """
    results = session.query(question)
    pprint(results)
    #typer.run(predict_glucose_tool)
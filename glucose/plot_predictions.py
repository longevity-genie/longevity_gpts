import sys
import os
import pickle
import gzip
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import torch
from scipy import stats

from glucose.gluformer.model import Gluformer
#from lib.gluformer.model import *
from utils.darts_processing import *
from utils.darts_dataset import *
# can i just acces the files from git? https://github.com/GlucoseDAO/GlucoBench/tree/0f2c982acc774e5fab5ec8a7d8b9af3d15717df0/utils

def plotting_graph (save_location_pdf, user_name, save_location_csv):
    '''
    Just plots the csv- no prediction
    '''
    # Ensure directories for saving results exist
    os.makedirs(save_location_pdf, exist_ok=True)
    os.makedirs(f'{save_location_pdf}/plots', exist_ok=True)

    # Dataset Details
    dataset = user_name



    # Load the CSV file
    file_path = save_location_csv
    df = pd.read_csv(file_path, parse_dates=['time'])


    # Plot settings
    sns.set_theme(style="whitegrid")

    # Plot the data
    plt.figure(figsize=(10, 6))
    #plt.plot(df['time'], df['gl'],colour='blue,' marker='o', linestyle='-')

    
    # Add labels and title
    plt.xlabel('Time (in 5 minute intervals)', fontdict={'size':16})
    plt.ylabel('Glucose (mg/dL)', fontdict={'size':16})
    plt.title(f'Glucose graph for {dataset}', fontdict={'size':18})
    

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Display the plot
    plt.tight_layout()
    plt.savefig(f'{save_location_pdf}/plots/gluformer_prediction_gradient_{dataset}.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{save_location_pdf}/plots/gluformer_prediction_gradient_{dataset}..png', dpi=300, bbox_inches='tight')
    plt.show()



def plotting (save_location_pdf, user_name, model_path):

    # Ensure directories for saving results exist
    os.makedirs(save_location_pdf, exist_ok=True)
    os.makedirs(f'{save_location_pdf}/plots', exist_ok=True)

    # Dataset and Model Details
    dataset = user_name
    model_name = 'gluformer'



    # Load data and model parameters
    formatter, series, scalers = load_data(seed=0,
                                           study_file=None,
                                           dataset=dataset,
                                           use_covs=True,
                                           cov_type='dual',
                                           use_static_covs=True)


    formatter.params['gluformer'] = {
        'in_len': 96,  # example input length, adjust as necessary
        'd_model': 512,  # model dimension
        'n_heads': 10,  # number of attention heads##############################################################################
        'd_fcn': 1024,  # fully connected layer dimension
        'num_enc_layers': 2,  # number of encoder layers
        'num_dec_layers': 2,  # number of decoder layers
        'length_pred': 12  # prediction length, adjust as necessary
    }


    # Define dataset for inference
    dataset_test_glufo = SamplingDatasetInferenceDual(
        target_series=series['test']['target'],
        covariates=series['test']['future'],
        input_chunk_length=formatter.params['gluformer']['in_len'],
        output_chunk_length=formatter.params['length_pred'],
        use_static_covariates=True,
        array_output_only=True
    )

    # Load Gluformer model
    num_dynamic_features = series['train']['future'][-1].n_components
    num_static_features = series['train']['static'][-1].n_components
    glufo = Gluformer(
        d_model=formatter.params['gluformer']['d_model'],
        n_heads=formatter.params['gluformer']['n_heads'],
        d_fcn=formatter.params['gluformer']['d_fcn'],
        r_drop=0.2,
        activ='relu',
        num_enc_layers=formatter.params['gluformer']['num_enc_layers'],
        num_dec_layers=formatter.params['gluformer']['num_dec_layers'],
        distil=True,
        len_seq=formatter.params['gluformer']['in_len'],
        label_len=formatter.params['gluformer']['in_len'] // 3,
        len_pred=formatter.params['length_pred'],
        num_dynamic_features=num_dynamic_features,
        num_static_features=num_static_features
    )
    
    
    glufo.to('cuda')

    glufo.load_state_dict(torch.load(model_path, map_location=torch.device('cuda')))


    # Get predictions
    forecasts, _ = glufo.predict(
        dataset_test_glufo,
        batch_size=16,####################################################
        num_samples=10,
        device='cuda',
        use_tqdm=True
    )

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
    ind = 3  # Example index

    samples = np.random.normal(
        loc=forecasts[ind, :],  # Mean (center) of the distribution
        scale=0.1,  # Standard deviation (spread) of the distribution
        size=(forecasts.shape[1], forecasts.shape[2])
     )
    #samples = samples.reshape(samples.shape[0], samples.shape[1], -1)
    
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
    ax.set_title(f'Gluformer Prediction with Gradient for {dataset}')

    # Adjust font sizes
    ax.xaxis.label.set_fontsize(16)
    ax.yaxis.label.set_fontsize(16)
    ax.title.set_fontsize(18)
    for item in ax.get_xticklabels() + ax.get_yticklabels():
        item.set_fontsize(14)

    # Save figure
    plt.tight_layout()
    plt.savefig(f'output/plots/gluformer_prediction_gradient_{dataset}_{ind}.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'output/plots/gluformer_prediction_gradient_{dataset}_{ind}.png', dpi=300, bbox_inches='tight')
    plt.show()

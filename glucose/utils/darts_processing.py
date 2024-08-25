import sys
import os
import yaml
import random
from typing import Any, BinaryIO, Callable, Dict, List, Optional, Sequence, Tuple, Union
from pathlib import Path
import numpy as np 
from scipy import stats
import pandas as pd
import darts

from darts import models
from darts import metrics
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from pytorch_lightning.callbacks import Callback
from sympy import pprint

# import data formatter
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from glucose.data_formatter.base import *

pd.set_option('display.width', None)   # Set display width to None to avoid truncation
pd.set_option('display.max_columns', None)  # Display all columns

def make_series(data: Dict[str, pd.DataFrame],
                time_col: str,
                group_col: str,
                value_cols: Dict[str, List[str]],
                include_sid: bool = False,
                ) -> Dict[str, darts.TimeSeries]:
    """
    Makes the TimeSeries from the data.

    Parameters
    ----------
    data
        dict of train, val, test dataframes
    time_col
        name of time column
    group_col
        name of group column
    value_cols
        dict with key specifying the type of covariate and value specifying the list of columns.
    include_sid
        whether to include segment id as static covariate
    
    Returns
    -------
    series: Dict[str, Dict[str, darts.TimeSeries]]
        dict of train, val, test splits of target and covariates TimeSeries objects
    scalers: Dict[str, darts.preprocessing.Scaler]
        dict of scalers for target and covariates
    """
    series = {i: {j: None for j in value_cols} for i in data.keys()}
    scalers = {}
    for key, df in data.items():
        
        for name, cols in value_cols.items():
            # Adjust display settings
            print(f"DATAFRAME for key {key} in NAME {name} and COLS {cols} and GROUP_COL {group_col}")
            pprint(df.head(1))
            series[key][name] = TimeSeries.from_group_dataframe(df = df,
                                                                group_cols = group_col,
                                                                time_col = time_col,
                                                                value_cols = cols) if cols is not None else None
            if series[key][name] is not None and include_sid is False:
                for i in range(len(series[key][name])):
                    series[key][name][i] = series[key][name][i].with_static_covariates(None)
            if cols is not None: 
                if key == 'train':
                    scalers[name] = ScalerCustom()
                    series[key][name] = scalers[name].fit_transform(series[key][name])
                else:
                    series[key][name] = scalers[name].transform(series[key][name])
            else:
                scalers[name] = None
    return series, scalers

def load_data(url: str,
              config_path: Path,
              use_covs: bool = False,
              cov_type: str = 'past',
              use_static_covs: bool = False, seed = 0):
    """
    Load data according to the specified config file and covert to Darts TimeSeries objects.

    Parameters
    ----------
    seed: int
        Random seed for data splitting.
    study_file: str
        Path to the study file.
    dataset: str
        Name of the dataset.
    use_covs: bool
        Whether to use covariates.
    cov_type: str
        Type of covariates to use. Can be 'past' or 'mixed' or 'dual'.
    use_static_covs: bool
        Whether to use static covariates.
    
    Returns
    -------
    formatter: DataFormatter
        Data formatter object.
    series: Dict[str, Dict[str, TimeSeries]]
       First dictionary specified the split, second dictionary specifies the type of series (target or covariate).
    scalers: Dict[str, Scaler]
       Dictionary of scalers with key indicating the type of series (target or covariate).
    """


    """
    config={
        'data_csv_path':f'{url}',
        'drop': None,
        'ds_name': 'livia_mini',
        'index_col': -1,
        'observation_interval': '5min',
        'column_definition': {
            {'data_type': 'categorical',
             'input_type':'id',
             'name':'id'
             },
            {'date_type':'date',
             'input_type':'time',
             'name':'time'
             },
            {'date_type':'real_valued',
             'input_type':'target',
             'name':'gl'
             }
        },
        'encoding_params':{'date':['day','month','year','hour','minute','second']
                           },
        'nan_vals':None,
        'interpolation_params':{'gap_threshold': 45,
                                'min_drop_length': 240
                                },
        'scaling_params':{'scaler':None
                          },
        'split_params':{'length_segment': 13,
                        'random_state':seed,
                        'test_percent_subjects': 0.1
                        },
        'max_length_input': 192,
        'length_pred': 12,
        'params':{
            'gluformer':{'in_len': 96,
                         'd_model': 512,
                         'n_heads': 10,
                         'd_fcn': 1024,
                         'num_enc_layers': 2,
                         'num_dec_layers': 2,
                         'length_pred': 12
                         }
        }
    }
    """
    with config_path.open("r") as f:
        config = yaml.safe_load(f)
    config["data_csv_path"] = url

    formatter = DataFormatter(config)
    #assert dataset is not None, 'dataset must be specified in the load_data call'
    assert use_covs is not None, 'use_covs must be specified in the load_data call'

    # convert to series
    time_col = formatter.get_column('time')
    group_col = formatter.get_column('sid')
    target_col = formatter.get_column('target')
    static_cols = formatter.get_column('static_covs')
    static_cols = static_cols + [formatter.get_column('id')] if static_cols is not None else [formatter.get_column('id')]
    dynamic_cols = formatter.get_column('dynamic_covs')
    future_cols = formatter.get_column('future_covs')

    data = {'train': formatter.train_data,
            'val': formatter.val_data,
            'test': formatter.test_data.loc[~formatter.test_data.index.isin(formatter.test_idx_ood)],
            'test_ood': formatter.test_data.loc[formatter.test_data.index.isin(formatter.test_idx_ood)]}
    value_cols = {'target': target_col,
                  'static': static_cols,
                  'dynamic': dynamic_cols,
                  'future': future_cols}
    # build series
    series, scalers = make_series(data,
                                    time_col,
                                    group_col,
                                    value_cols)
    if not use_covs:
        # set dynamic and future covariates to None
        for split in ['train', 'val', 'test', 'test_ood']:
            for cov in ['dynamic', 'future']:
                series[split][cov] = None
    elif use_covs and cov_type == 'mixed':
        pass # this is the default for make_series()
    elif use_covs and cov_type == 'past':
        # use future covariates as dynamic (past) covariates
        if series['train']['dynamic'] is None:
            for split in ['train', 'val', 'test', 'test_ood']:
                series[split]['dynamic'] = series[split]['future']
        else:
            for split in ['train', 'val', 'test', 'test_ood']:
                for i in range(len(series[split]['future'])):
                    series[split]['dynamic'][i] = series[split]['dynamic'][i].concatenate(series[split]['future'][i], axis=1)
        # erase future covariates
        for split in ['train', 'val', 'test', 'test_ood']:
            series[split]['future'] = None
    elif use_covs and cov_type == 'dual':
        # erase dynamic (past) covariates
        for split in ['train', 'val', 'test', 'test_ood']:
            series[split]['dynamic'] = None
    
    if use_static_covs:
        # attach static covariates to series
        for split in ['train', 'val', 'test', 'test_ood']:
            for i in range(len(series[split]['target'])):
                static_covs = series[split]['static'][i][0].pd_dataframe()
                series[split]['target'][i] = series[split]['target'][i].with_static_covariates(static_covs)

    return formatter, series, scalers

def reshuffle_data(formatter: DataFormatter, 
                   seed: int = 0, 
                   use_covs: bool = None,
                   cov_type: str = 'past',
                   use_static_covs: bool = False,):
    """
    Reshuffle data according to the seed and covert to Darts TimeSeries objects.
    
    Parameters
    ----------
    formatter: DataFormatter
        Data formatter object containing the data
    seed: int
        Random seed for data splitting.
    use_covs: bool
        Whether to use covariates.
    cov_type: str
        Type of covariates to use. Can be 'past' or 'mixed' or 'dual'.
    use_static_covs: bool
        Whether to use static covariates.
    
    Returns
    -------
    formatter: DataFormatter
        Reshuffled data formatter object.
    series: Dict[str, Dict[str, TimeSeries]]
         First dictionary specified the split, second dictionary specifies the type of series (target or covariate).
    scalers: Dict[str, Scaler]
        Dictionary of scalers with key indicating the type of series (target or covariate).
    """
    # reshuffle
    formatter.reshuffle(seed)
    assert use_covs is not None, 'use_covs must be specified in the reshuffle_data call'

    # convert to series
    time_col = formatter.get_column('time')
    group_col = formatter.get_column('sid')
    target_col = formatter.get_column('target')
    static_cols = formatter.get_column('static_covs')
    static_cols = static_cols + [formatter.get_column('id')] if static_cols is not None else [formatter.get_column('id')]
    dynamic_cols = formatter.get_column('dynamic_covs')
    future_cols = formatter.get_column('future_covs')

    # build series
    series, scalers = make_series({'train': formatter.train_data,
                                    'val': formatter.val_data,
                                    'test': formatter.test_data.loc[~formatter.test_data.index.isin(formatter.test_idx_ood)],
                                    'test_ood': formatter.test_data.loc[formatter.test_data.index.isin(formatter.test_idx_ood)]},
                                    time_col,
                                    group_col,
                                    {'target': target_col,
                                    'static': static_cols,
                                    'dynamic': dynamic_cols,
                                    'future': future_cols})
    
    if not use_covs:
        # set dynamic and future covariates to None
        for split in ['train', 'val', 'test', 'test_ood']:
            for cov in ['dynamic', 'future']:
                series[split][cov] = None
    elif use_covs and cov_type == 'past':
        # use future covariates as dynamic covariates
        if series['train']['dynamic'] is None:
            for split in ['train', 'val', 'test', 'test_ood']:
                series[split]['dynamic'] = series[split]['future']
        # or attach them to dynamic covariates
        else:
            for split in ['train', 'val', 'test', 'test_ood']:
                for i in range(len(series[split]['future'])):
                    series[split]['dynamic'][i] = series[split]['dynamic'][i].concatenate(series[split]['future'][i], axis=1)
    elif use_covs and cov_type == 'dual':
        # set dynamic covariates to None, because they are not supported
        for split in ['train', 'val', 'test', 'test_ood']:
            series[split]['dynamic'] = None
    
    if use_static_covs:
        # attach static covariates to series
        for split in ['train', 'val', 'test', 'test_ood']:
            for i in range(len(series[split]['target'])):
                static_covs = series[split]['static'][i][0].pd_dataframe()
                series[split]['target'][i] = series[split]['target'][i].with_static_covariates(static_covs)
    
    return formatter, series, scalers

class ScalerCustom:
    '''
    Min-max scaler for TimeSeries that fits on all sequences simultaenously.
    Default Darts scaler fits one scaler per sequence in the list.

    Attributes
    ----------
    scaler: Scaler
        Darts scaler object.
    min_: np.ndarray
        Per feature adjustment for minimum (see Scikit-learn).
    scale_: np.ndarray
        Per feature relative scaling of the data (see Scikit-learn).
    '''
    def __init__(self):
        self.scaler = Scaler()
        self.min_ = None
        self.scale_ = None 

    def fit(self, time_series: Union[List[TimeSeries], TimeSeries]) -> None:
        
        if isinstance(time_series, list):

            # extract series as Pandas dataframe
            df = pd.concat([ts.pd_dataframe() for ts in time_series])
            value_cols = df.columns
            df.reset_index(inplace=True)
            # create new equally spaced time grid
            df['new_time'] = pd.date_range(start=df['time'].min(), periods=len(df), freq='1h')
            # fit scaler
            series = TimeSeries.from_dataframe(df, time_col='new_time', value_cols=value_cols)
            series = self.scaler.fit(series)
        else:
            series = self.scaler.fit(time_series)
        # extract min and scale
        self.min_ = self.scaler._fitted_params[0].min_
        self.scale_ = self.scaler._fitted_params[0].scale_

    def transform(self, time_series: Union[List[TimeSeries], TimeSeries]) -> Union[List[TimeSeries], TimeSeries]:
        if isinstance(time_series, list):
            # transform one by one
            series = [self.scaler.transform(ts) for ts in time_series]
        else:
            series = self.scaler.transform(time_series)
        return series
    
    def inverse_transform(self, time_series: Union[List[TimeSeries], TimeSeries]) -> Union[List[TimeSeries], TimeSeries]:
        if isinstance(time_series, list):
            # transform one by one
            series = [self.scaler.inverse_transform(ts) for ts in time_series]
        else:
            series = self.scaler.inverse_transform(time_series)
        return series
    
    def fit_transform(self, time_series: Union[List[TimeSeries], TimeSeries]) -> Union[List[TimeSeries], TimeSeries]:
        self.fit(time_series)
        series = self.transform(time_series)
        return series
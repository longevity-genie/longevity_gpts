from typing import List, Callable, Any, Tuple

import numpy as np
import torch
from torch import nn, Tensor

from .collate import default_collate

class EarlyStop:
  def __init__(self, patience: int, delta: float):
    self.patience: int = patience
    self.delta: float = delta
    self.counter: int = 0
    self.best_loss: float = np.Inf
    self.stop: bool = False

  def __call__(self, loss: float, model: nn.Module, path: str) -> None:
    if loss < self.best_loss:
      self.best_loss = loss
      self.counter = 0
      torch.save(model.state_dict(), path)
    elif loss > self.best_loss + self.delta:
      self.counter = self.counter + 1
      if self.counter >= self.patience:
        self.stop = True

class ExpLikeliLoss(nn.Module):
  def __init__(self, num_samples: int = 100):
    super(ExpLikeliLoss, self).__init__()
    self.num_samples: int = num_samples

  def forward(self, pred: Tensor, true: Tensor, logvar: Tensor) -> Tensor:
    b, l, d = pred.size(0), pred.size(1), pred.size(2)
    true = true.transpose(0,1).reshape(l, -1, self.num_samples).transpose(0, 1)
    pred = pred.transpose(0,1).reshape(l, -1, self.num_samples).transpose(0, 1)
    logvar = logvar.reshape(-1, self.num_samples)

    loss = torch.mean((-1) * torch.logsumexp((-l / 2) * logvar + (-1 / (2 * torch.exp(logvar))) * torch.sum((true - pred) ** 2, dim=1), dim=1))
    return loss

def modify_collate(num_samples: int) -> Callable[[List[Any]], Any]:
  def wrapper(batch: List[Any]) -> Any:
    batch_rep = [sample for sample in batch for _ in range(num_samples)]
    return default_collate(batch_rep)
  return wrapper

def adjust_learning_rate(model_optim: torch.optim.Optimizer, epoch: int, lr: float) -> None:
  lr = lr * (0.5 ** epoch)
  print("Learning rate halving...")
  print(f"New lr: {lr:.7f}")
  for param_group in model_optim.param_groups:
    param_group['lr'] = lr

def process_batch(
        subj_id: Tensor,
        batch_x: Tensor,
        batch_y: Tensor,
        batch_x_mark: Tensor,
        batch_y_mark: Tensor,
        len_pred: int,
        len_label: int,
        model: nn.Module,
        device: torch.device
) -> Tuple[Tensor, Tensor, Tensor]:
  subj_id = subj_id.long().to(device)
  batch_x = batch_x.float().to(device)
  batch_y = batch_y.float()
  batch_x_mark = batch_x_mark.float().to(device)
  batch_y_mark = batch_y_mark.float().to(device)

  true = batch_y[:, -len_pred:, :].to(device)

  dec_inp = torch.zeros([batch_y.shape[0], len_pred, batch_y.shape[-1]], dtype=torch.float, device=device)
  dec_inp = torch.cat([batch_y[:, :len_label, :].to(device), dec_inp], dim=1)

  pred, logvar = model(subj_id, batch_x, batch_x_mark, dec_inp, batch_y_mark)

  return pred, true, logvar
import torch.nn as nn
from modules.ffn import FFN
import torch
from typing import Optional, Tuple

class LSTM(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: Optional[int] = None,
        num_layers: int = 1,
        bidirectional: bool = True,
        activation: nn.Module = nn.LeakyReLU(),
        dropout: float = 0.0,
    ):
        super().__init__()
        self.bidirectional = bidirectional
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size//(2 if bidirectional else 1), num_layers=num_layers,
                            bidirectional=bidirectional, dropout=dropout, batch_first=True, bias=True)
        if output_size is None:
            self.ffn = activation
        else:
            self.ffn = FFN(in_features=hidden_size, out_features=output_size, activation=activation)
        self.reset_parameters()

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h, (_, c) = self.lstm(x)
        y = self.ffn(h)
        if self.bidirectional:
            c = c.permute(1, 2, 0).flatten(-2, -1)
        else:
            c = c.squeeze(0)
        return y, c

    def reset_parameters(self):
        for param in self.parameters():
            # apply orthogonal_ to weight
            if len(param.shape) > 1:
                nn.init.orthogonal_(param)
            # apply zeros_ to bias
            else:
                nn.init.zeros_(param)
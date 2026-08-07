"""
CIFN - Continuous Interference Field Network
============================================
CIFNLinear and CIFNWeightField for neural network layers.
"""

import torch
import torch.nn as nn
import math


class CIFNWeightField(nn.Module):
    """
    Continuous Interference Field Network weight generator.
    Generates weights on-the-fly from a continuous wave interference lattice.
    """
    
    def __init__(self, out_features: int, in_features: int, basis_count: int = 512):
        super().__init__()
        self.out_features = out_features
        self.in_features = in_features
        self.basis_count = basis_count
        
        # Amplitude parameters
        a_init = torch.empty(basis_count)
        nn.init.normal_(a_init, mean=0.0, std=2.0 / basis_count)
        self.a = nn.Parameter(a_init)
        
        # Fixed wave frequencies and phase offsets
        freqs = torch.linspace(1.0, 10.0, basis_count)
        signs = torch.ones(basis_count)
        signs[1::2] = -1.0
        freqs = freqs * signs
        
        self.omega_out = nn.Parameter(freqs * math.pi, requires_grad=False)
        self.omega_in = nn.Parameter(freqs * math.pi, requires_grad=False)
        
        phases = torch.linspace(0.0, 2 * math.pi, basis_count)
        self.theta_out = nn.Parameter(phases, requires_grad=False)
        self.theta_in = nn.Parameter(phases, requires_grad=False)
    
    def forward(self) -> torch.Tensor:
        device = self.a.device
        
        x = torch.linspace(0.0, 1.0, self.out_features, device=device)
        y = torch.linspace(0.0, 1.0, self.in_features, device=device)
        
        field_out = torch.sin(self.omega_out.unsqueeze(1) * x.unsqueeze(0) + self.theta_out.unsqueeze(1))
        field_in = torch.sin(self.omega_in.unsqueeze(1) * y.unsqueeze(0) + self.theta_in.unsqueeze(1))
        
        W = torch.einsum('k,ki,kj->ij', self.a, field_out, field_in)
        return W


class CIFNLinear(nn.Module):
    """
    Linear projection layer with CIFN-generated weights.
    """
    
    def __init__(self, in_features: int, out_features: int, basis_count: int = 512):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight_field = CIFNWeightField(out_features, in_features, basis_count)
        self.bias = nn.Parameter(torch.zeros(out_features))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        W = self.weight_field()
        return torch.matmul(x, W.t()) + self.bias
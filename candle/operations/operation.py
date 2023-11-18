"""Operations in a computation graph."""

import numpy as np
from abc import ABC, abstractmethod
from typing import List

from ..tensor import Tensor
from ..parameter import Parameter


class Operation(ABC):
    
    def __init__(self,
                 inputs: List[Tensor]):
        """Initializes operation.
        
        Parameters
        ----------
        inputs
            List of Tensor inputs into operation.
        
        """
        # If any of the inputs are scalars, cast to Tensor
        inputs = [Tensor(x) if isinstance(x, (int, float, complex, np.ndarray)) else x
                  for x in inputs]
        
        for x in inputs:
            if not isinstance(x, (Tensor, Parameter)):
                raise ValueError(f'Input is type {type(x)}, but all inputs must be type Tensor.')
        
        self.inputs = inputs
        self.output = None  # Tensor result of self.forward()
    
    
    def forward(self):
        """Computes the result of the operation.
        
        Returns
        -------
        output
            Tensor result of operation.
        
        """
        output = self._forward()
        
        output.operation = self
        self.output = output
        
        return output

         
    def backward(self, output_grad: np.array):
        """Computes the derivative of the loss node with respect to each Tensor in self.inputs.
        
        Parameters
        ----------
        output_grad
            Numpy array with shape self.output.shape.
        
        Returns
        -------
        input_grads
            List of Numpy arrays, one array of shape input.shape for each tensor `input` in self.inputs.
        
        """
        input_grads = self._backward(output_grad)
        
        assert len(input_grads) == len(self.inputs)
        for (input_grad, inp) in zip(input_grads, self.inputs):
            assert type(input_grad) is np.ndarray
            
            if input_grad.shape != inp.shape:
                raise RuntimeError(f'input_grad.shape = {input_grad.shape} != inp.shape = {inp.shape}:')
            
        return input_grads
            
        
    @abstractmethod
    def _forward(self):
        pass
    
    
    @abstractmethod
    def _backward(self,
                  output_grad: np.array):
        pass
    
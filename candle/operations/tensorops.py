from __future__ import annotations
import numpy as np
from typing import List, Tuple, Union

from .operation import Operation
from .. import tensor


class TensorContraction(Operation):
    """f(inputs) = tensordot(inputs[0], inputs[1], axes)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 axes: int):
        super().__init__(inputs)
        self.axes = axes
        
        
    def _forward(self):
        (a, b) = self.inputs
        return tensor.Tensor(np.tensordot(a.data, b.data, axes=self.axes))
    
    
    def _backward(self,
                  output_grad: np.array):
        (a, b) = self.inputs
        
        left_dim = len(a.data.shape) - self.axes
        right_dim = len(b.data.shape) - self.axes

        input_grad_a = np.tensordot(output_grad, b.data, axes=[range(-1, -right_dim - 1, -1)] * 2)
        input_grad_b = np.tensordot(a.data, output_grad, axes=[range(left_dim)] * 2)

        return (input_grad_a, input_grad_b)
    
    
class TensorSum(Operation):
    """f(inputs) = inputs[0].sum(axis, keepdims)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 axis: Union[int, Tuple[int, int]] = None,
                 keepdims: bool = False):
        super().__init__(inputs)
        if type(axis) is int:
            axis = (axis,)
        if axis is None:
            axis = tuple(range(len(self.inputs[0].shape)))
        
        self.axis = axis
        self.keepdims = keepdims
    
    
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.sum(axis=self.axis, keepdims=self.keepdims))
    
    
    def _backward(self,
                  output_grad: np.array):
        if not self.keepdims:
            output_grad = np.expand_dims(output_grad, axis=self.axis)
            
        input_grad = np.broadcast_to(output_grad, shape=self.inputs[0].shape)
                         
        return (input_grad,)
    
    
class TensorMax(Operation):
    """f(inputs) = inputs[0].max(axis, keepdims)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 axis: Union[int, Tuple[int, int]] = None,
                 keepdims: bool = False):
        super().__init__(inputs)
        if type(axis) is int:
            axis = (axis,)
        if axis is None:
            axis = tuple(range(len(self.inputs[0].shape)))
        
        self.axis = axis
        self.keepdims = keepdims
    
    
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.max(axis=self.axis, keepdims=self.keepdims))
    
    
    def _backward(self,
                  output_grad: np.array):
        output = self.output.data

        if not self.keepdims:
            output_grad = np.expand_dims(output_grad, axis=self.axis)
            output = np.expand_dims(output, axis=self.axis)

        mask = self.inputs[0].data == np.broadcast_to(output, self.inputs[0].shape)

        input_grad = mask * np.broadcast_to(output_grad, shape=self.inputs[0].shape)
                         
        return (input_grad,)
    
    
class TensorMin(Operation):
    """f(inputs) = inputs[0].min(axis, keepdims)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 axis: Union[int, Tuple[int, int]] = None,
                 keepdims: bool = False):
        super().__init__(inputs)
        if type(axis) is int:
            axis = (axis,)
        if axis is None:
            axis = tuple(range(len(self.inputs[0].shape)))
        
        self.axis = axis
        self.keepdims = keepdims
    
    
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.min(axis=self.axis, keepdims=self.keepdims))
    
    
    def _backward(self,
                  output_grad: np.array):
        output = self.output.data

        if not self.keepdims:
            output_grad = np.expand_dims(output_grad, axis=self.axis)
            output = np.expand_dims(output, axis=self.axis)

        mask = self.inputs[0].data == np.broadcast_to(output, self.inputs[0].shape)

        input_grad = mask * np.broadcast_to(output_grad, shape=self.inputs[0].shape)
                         
        return (input_grad,)
    
    
class TensorSlice(Operation):
    """f(inputs) = inputs[0][key]"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 key):
        super().__init__(inputs)
        if type(key) is not tuple:
            key = (key,)

        # If any elements in key are Tensor, convert to np.array
        key = tuple(k.data if isinstance(k, tensor.Tensor) else k for k in key)
            
        # Numpy slicing is quite involved and it's hard to cover every edge case
        # For now, we guarantee backprop supports slicing with ints, slices, boolean mask,
        # and a single leading 2D list, e.g. x[[[0, 1, 2], [5, 2, 3]], 2, :, 2:5:-1].
        # This covers most practical cases.
        for key_i in key[1:]:
            assert self._is_valid_slice(key_i)

        self.key = key
        self.key0_ndim = self._1d_or_2d_int_list(key[0])
        assert self._is_valid_slice(key[0]) or self.key0_ndim != -1 

    
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data[self.key])
    
    
    def _backward(self,
                  output_grad: np.array):
        input_grad = np.zeros(self.inputs[0].shape, dtype=tensor.Tensor.DEFAULT_DTYPE)

        if self.key0_ndim == -1:
            input_grad[self.key] = output_grad

        else:
            for (i, subarray) in enumerate(self.key[0]):
                input_grad[(subarray,) + self.key[1:]] += output_grad[i]

        return (input_grad,)
        

    def _is_valid_slice(self, s):
        """Slice is valid if None, int, slice, or boolean mask."""
        if s is None:
            return True
        if isinstance(s, (np.integer, int, slice)):
            return True
        if np.array(s).dtype == bool:
            return True
        return False

    
    def _1d_or_2d_int_list(self, s):
        """Returns 2 if 2d int list, 1 if 1d int list, -1 if neither."""
        s = np.array(s)
        if s.dtype == int and s.ndim in [1, 2]:
            return s.ndim
        else:
            return -1


class TensorSetSlice(Operation):
    """output = inputs[0]; output[key] = inputs[1]; f(inputs) = output"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 key):
        super().__init__(inputs)
        if type(key) is not tuple:
            key = (key,)

        # If any elements in key are Tensor, convert to np.array
        key = tuple(k.data if isinstance(k, tensor.Tensor) else k for k in key)
        
        self.key = key
            
    
    def _forward(self):
        (a, b) = [i.data for i in self.inputs]
        a = a.copy()  # Todo: make this operation in-place
        a[self.key] = b
        return tensor.Tensor(a)
    
    
    def _backward(self,
                  output_grad: np.array):
        input_grad_a = output_grad.copy()
        input_grad_a[self.key] = 0
        input_grad_b = output_grad[self.key]
        return (input_grad_a, input_grad_b)
    
    
class TensorReshape(Operation):
    """f(inputs) = inputs[0].reshape(new_shape)"""

    def __init__(self,
                 inputs: List[Tensor],
                 new_shape: Tuple[int]):
        super().__init__(inputs)
        self.new_shape = new_shape
        
        
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.reshape(self.new_shape))
    
    
    def _backward(self,
                  output_grad: np.array):
        input_grad = output_grad.reshape(self.inputs[0].shape)
        
        return (input_grad,)
    
    
class TensorSwapaxes(Operation):
    """f(inputs) = inputs[0].swapaxes(dim0, dim1)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 dim0: int,
                 dim1: int):
        super().__init__(inputs)
        self.dim0 = dim0
        self.dim1 = dim1
        
        
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.swapaxes(self.dim0, self.dim1))
    
    
    def _backward(self,
                  output_grad: np.array):
        input_grad = output_grad.swapaxes(self.dim0, self.dim1)
        
        return (input_grad,)
    
    
class BatchMatrixMultiply(Operation):
    """Multiplies two tensors of shape (A, B, C, ..., M, N) and (A, B, C, ..., N, P).

    Returns a tensor of shape (A, B, C, ..., M, P)."""
    
    def __init__(self,
                 inputs: List[Tensor]):
        super().__init__(inputs)
        
        
    def _forward(self):
        assert len(self.inputs) == 2
        (a, b) = self.inputs
        assert a.shape[:-2] == b.shape[:-2]  # Assert first N-2 dimensions match

        return tensor.Tensor(a.data @ b.data)
    
    
    def _backward(self,
                  output_grad: np.array):
        (a, b) = self.inputs
        input_grad_a = output_grad @ b.data.swapaxes(-1, -2)
        input_grad_b = a.data.swapaxes(-1, -2) @ output_grad
        
        return (input_grad_a, input_grad_b)
    
    
class TensorTranspose(Operation):
    """f(inputs) = inputs[0].T"""
    
    def __init__(self,
                 inputs: List[Tensor]):
        super().__init__(inputs)
        
        
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.T)
    
    
    def _backward(self,
                  output_grad: np.array):
        return (output_grad.T,)
    
    
class TensorMaskedFill(Operation):
    
    def __init__(self,
                 inputs: List[Tensor],
                 mask: Tensor,
                 fill_value: float):
        """Returns Tensor with masked values replaced with fill_value.
        
        Parameters
        ----------
        inputs
            Single Tensor.
        mask
            Tensor of 1s and 0s, must be broadcastable with inputs[0].
            1 to fill with fill_value, 0 to leave as-is.
        fill_value
            Value to fill.
            
        """
        super().__init__(inputs)
        if not np.all(np.isclose(mask.data, 0) | np.isclose(mask.data, 1)):
            raise ValueError('mask must be a Tensor with only 0s and 1s.')
        self.broadcasted_mask = np.broadcast_to(mask.data, self.inputs[0].shape)
        self.fill_value = fill_value

        
    def _forward(self):
        assert len(self.inputs) == 1
        
        return tensor.Tensor((1 - self.broadcasted_mask) * self.inputs[0].data + self.broadcasted_mask * self.fill_value)
    
    
    def _backward(self,
                  output_grad: np.array):
        input_grad = output_grad * (1 - self.broadcasted_mask)
        
        return (input_grad,)
    
    
class TensorConcatenation(Operation):
    """f(inputs) = np.concatenate(*inputs[0], axis=axis)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 axis: int = 0):
        super().__init__(inputs)
        self.axis = axis
    
    
    def _forward(self):
        return tensor.Tensor(np.concatenate([tensor.data for tensor in self.inputs], axis=self.axis))
    
    
    def _backward(self,
                  output_grad: np.array):
        input_lengths_along_axis = [i.shape[self.axis] for i in self.inputs]
        indices_or_sections = np.cumsum(input_lengths_along_axis)[:-1]

        input_grads = tuple(np.split(output_grad, indices_or_sections, axis=self.axis))

        return input_grads
    
    
class TensorClone(Operation):
    """f(inputs) = inputs[0].copy()"""
    
    def __init__(self,
                 inputs: List[Tensor]):
        super().__init__(inputs)
        
        
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.copy())
    
    
    def _backward(self,
                  output_grad: np.array):
        return (output_grad,)
    
    
class TensorRepeatInterleave(Operation):
    """f(inputs) = np.repeat(inputs[0], repeats, axis)"""

    def __init__(self,
                 inputs: List[Tensor],
                 repeats: int,
                 axis: int):
        super().__init__(inputs)
        assert type(repeats) is int
        assert axis is None or type(axis) is int
        self.repeats = repeats
        
        if axis is not None:
            dim = len(self.inputs[0].shape)
            axis = (axis + dim) % dim
        self.axis = axis
        
        
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(self.inputs[0].data.repeat(self.repeats, self.axis))
    
    
    def _backward(self,
                  output_grad: np.array):
        orig_shape = self.inputs[0].shape
        
        if self.axis is None:
            input_grad = output_grad.reshape(orig_shape + (self.repeats,)).sum(axis=-1)
        else:
            shape = (orig_shape[:self.axis]
                     + (orig_shape[self.axis], self.repeats)
                     + orig_shape[self.axis + 1:])

            input_grad = output_grad.reshape(shape).sum(axis=self.axis + 1)

        return (input_grad,)
    
    
class TensorFlip(Operation):
    """f(inputs) = np.flip(inputs[0].T"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 axis: int = None):
        super().__init__(inputs)
        self.axis = axis
        
        
    def _forward(self):
        assert len(self.inputs) == 1
        return tensor.Tensor(np.flip(self.inputs[0].data, axis=self.axis))
    
    
    def _backward(self,
                  output_grad: np.array):
        return (np.flip(output_grad, axis=self.axis),)


class TopKOperation(Operation):
    """(weights, indices) = topk(inputs[0], k, axis)"""
    
    def __init__(self,
                 inputs: List[Tensor],
                 k: int,
                 axis: int = -1):
        super().__init__(inputs)
        assert k >= 1
        self.k = k
        self.axis = axis
        self._indices = None  # Populated during forward()

    
    def _forward(self):
        assert len(self.inputs) == 1
        x = self.inputs[0].data
        x = x.swapaxes(self.axis, -1)
        
        argsort = np.argsort(-x, axis=-1)
        indices = argsort.take(range(self.k), axis=-1)
        
        onehot_bool = np.eye(x.shape[-1]).astype(bool)
        
        weights = []
        for i in range(self.k):
            idx = indices.take(i, axis=-1)
            bool_mask = onehot_bool[idx]
            top_i = x[bool_mask].reshape(idx.shape)
            weights.append(np.expand_dims(top_i, axis=-1))
        
        weights = np.concatenate(weights, axis=-1).swapaxes(-1, self.axis)
        
        self._indices = tensor.Tensor(indices.swapaxes(-1, self.axis)).astype(int)
        
        return tensor.Tensor(weights)
        
            
    def _backward(self,
                  output_grad: np.array):
        input_grad = np.zeros_like(self.inputs[0].data)
        input_grad = np.moveaxis(input_grad, self.axis, -1)
        output_grad = np.moveaxis(output_grad, self.axis, 0)
        indices = np.moveaxis(self._indices.data, self.axis, 0)
        
        onehot_bool = np.eye(input_grad.shape[-1]).astype(bool)
        for i in range(self.k):
            bool_mask = onehot_bool[indices[i]]
            input_grad[bool_mask] = output_grad[i].flatten()
        
        input_grad = np.moveaxis(input_grad, -1, self.axis)
        
        return (input_grad,)

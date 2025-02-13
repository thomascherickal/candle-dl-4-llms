import numpy as np
import unittest

from candle.tensor import Tensor, Parameter, randn
from candle.operations import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Exponentiation,
    TensorSum,
    TensorMax,
    TensorMin,
    TensorContraction,
    TensorSlice,
    TensorSetSlice,
    TensorReshape,
    TensorSwapaxes,
    TensorTranspose,
    TensorConcatenation,
    TensorMaskedFill,
    TensorFlip,
    TopKOperation,
    TensorRepeatInterleave,
    BatchMatrixMultiply,
    Conv2dOperation,
    MaxPool2dOperation,
    AvgPool2dOperation,
    ReLUActivation,
    GeLUActivation,
    SiLUActivation,
)
from .utils import numerical_grad_check


class TestOperations(unittest.TestCase):
    
    def test_add_sub_mult_div(self):
        numerical_grad_check(operation_class=Addition,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11)),
                                          Parameter(randn(2, 3, 5, 7, 11))])

        numerical_grad_check(operation_class=Addition,
                             test_inputs=[Parameter(5.0),
                                          Parameter(3.0)])
        
        numerical_grad_check(operation_class=Subtraction,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11)),
                                          Parameter(randn(2, 3, 5, 7, 11))])

        numerical_grad_check(operation_class=Subtraction,
                             test_inputs=[Parameter(5.0),
                                          Parameter(3.0)])

        numerical_grad_check(operation_class=Multiplication,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11)),
                                          Parameter(randn(2, 3, 5, 7, 11))])

        numerical_grad_check(operation_class=Multiplication,
                             test_inputs=[Parameter(5.0),
                                          Parameter(3.0)])

        numerical_grad_check(operation_class=Division,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11)),
                                          Parameter(10 + randn(2, 3, 5, 7, 11))])

        numerical_grad_check(operation_class=Division,
                             test_inputs=[
                                 Parameter(5.0),
                                 Parameter(3.0),
                             ])
        
    def test_broadcasted_add_sub_mult_div(self):
        numerical_grad_check(operation_class=Addition,
                             test_inputs=[
                                 Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                 Parameter(randn(3, 1, 1, 7, 1)),
                             ])

        numerical_grad_check(operation_class=Addition,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(3.0)])

        numerical_grad_check(operation_class=Subtraction,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(randn(3, 1, 1, 7, 1))])

        numerical_grad_check(operation_class=Subtraction,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(3.0)])

        numerical_grad_check(operation_class=Multiplication,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(randn(3, 1, 1, 7, 1))])

        numerical_grad_check(operation_class=Multiplication,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(3.0)])

        numerical_grad_check(operation_class=Division,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(10 + randn(3, 1, 1, 7, 1))])

        numerical_grad_check(operation_class=Division,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(3.0)])

        
    def test_activations(self):
        numerical_grad_check(operation_class=ReLUActivation,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))])
        
        numerical_grad_check(operation_class=GeLUActivation,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))])

        numerical_grad_check(operation_class=SiLUActivation,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))])
        
        
    def test_power(self):
        numerical_grad_check(operation_class=Power,
                             test_inputs=[Parameter(100 + randn(2, 3, 5, 7, 11))],
                             kwargs={'power': 1.234},
                             atol=1e-3)

        numerical_grad_check(operation_class=Power,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'power': 3},
                             atol=1e-2)
        
        numerical_grad_check(operation_class=Exponentiation,
                             test_inputs=[Parameter(randn(3, 4, 5, 7))],
                             kwargs={'base': 2.5},
                             atol=1e-3)
        
        
    def test_tensor_contraction(self):
        numerical_grad_check(operation_class=TensorContraction,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11)),
                                          Parameter(randn(5, 7, 11, 17))],
                             kwargs = {'axes': 3})

        numerical_grad_check(operation_class=TensorContraction,
                             test_inputs=[Parameter(randn(1, 2, 3, 4, 5)),
                                          Parameter(randn(1, 2, 3, 4, 5))],
                             kwargs = {'axes': 5})
        
        
    def test_tensor_sum(self):
        numerical_grad_check(operation_class=TensorSum,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11)),])

        numerical_grad_check(operation_class=TensorSum,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': 1})

        numerical_grad_check(operation_class=TensorSum,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': (2, 3)})

        numerical_grad_check(operation_class=TensorSum,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'keepdims': True})

        numerical_grad_check(operation_class=TensorSum,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': 1,
                                     'keepdims': True})

        numerical_grad_check(operation_class=TensorSum,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': (2, 3),
                                     'keepdims': True})
        
        
    def test_tensor_max_min(self):
        numerical_grad_check(operation_class=TensorMax,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': (2, 4), 'keepdims': True})

        numerical_grad_check(operation_class=TensorMax,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': (2, 4), 'keepdims': False})

        numerical_grad_check(operation_class=TensorMax,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': None, 'keepdims': True})

        numerical_grad_check(operation_class=TensorMax,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': None, 'keepdims': False})

        numerical_grad_check(operation_class=TensorMin,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': (2, 4), 'keepdims': True})

        numerical_grad_check(operation_class=TensorMin,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': (2, 4), 'keepdims': False})

        numerical_grad_check(operation_class=TensorMin,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': None, 'keepdims': True})

        numerical_grad_check(operation_class=TensorMin,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11, 13))],
                             kwargs={'axis': None, 'keepdims': False})

        
    def test_tensor_slice(self):
        numerical_grad_check(operation_class=TensorSlice,
                                     test_inputs=[Parameter(randn(7, 11, 13, 17, 1, 1))],
                                     kwargs={'key': ([0, 1, 2, 3], 0, slice(None))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 11, 13, 17, 1, 1))],
                             kwargs={'key': ([[0, 1, 2, 3]], 0, slice(None))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': (slice(None, 3, None), 1, 2, slice(None, None, None))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': [0, 1, 2, 5]})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': [[0, 1, 2, 5]]})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': [[0, 1, 2, 5], [6, 2, 3, 4]]})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': ([[0, 1, 2, 3]], slice(None, 3, None), 1, 2, slice(None, None, None))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': [[0, 1, 2, 5], [6, 2, 3, 4]]})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': ([[0, 1, 2, 5], [6, 2, 3, 4]], slice(2, 3, 1), slice(None))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': (None, slice(None))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': (None, None, slice(2, 4, 1), None, slice(None))})
        
        # Boolean slicing
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(3, 2, 5))],
                             kwargs={'key': ([[True, False], [True, True], [False, True]], slice(1, 3, 1))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(3, 2, 5))],
                             kwargs={'key': (np.array([[True, False], [True, True], [False, True]]), slice(1, 3, 1))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(3, 2, 5))],
                             kwargs={'key': (np.array([True, False, False]), slice(1, 3, 1))})
        
        numerical_grad_check(operation_class=TensorSlice,
                             test_inputs=[Parameter(randn(3, 11, 17, 1, 1))],
                             kwargs={'key': ([True, False, True], 1, slice(None))})


    def test_tensor_set_slice(self):
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(7, 11, 13, 1, 1)),
                                          Parameter(randn(7, 11, 13, 1, 1))],
                             kwargs={'key': (slice(None))})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(7, 11, 13, 17, 1, 1)),
                                          Parameter(randn(1, 4, 13, 17, 1, 1))],
                             kwargs={'key': ([[0, 1, 2, 3]], 0, slice(None))})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(randn(3, 5, 1, 1, 1))],
                             kwargs={'key': (slice(None, 3, None), 1, 2, slice(None, None, None))})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(randn(4, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': [0, 1, 2, 5]})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(randn(1, 4, 2, 3, 5, 1, 1, 1))],
                             kwargs={'key': [[0, 1, 2, 5]]})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                          Parameter(randn(1, 4, 2, 1, 1, 1))],
                             kwargs={'key': ([[0, 1, 2, 3]], slice(None, 3, None), 1, 2, slice(None, None, None))})

        
        # Boolean slicing
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(3, 2, 5)),
                                          Parameter(randn(4, 2))],
                             kwargs={'key': ([[True, False], [True, True], [False, True]], slice(1, 3, 1))})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(3, 2, 5)),
                                          Parameter(randn(4, 2))],
                             kwargs={'key': (np.array([[True, False], [True, True], [False, True]]), slice(1, 3, 1))})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(3, 2, 5)),
                                          Parameter(randn(1, 1, 5))],
                             kwargs={'key': (np.array([True, False, False]), slice(1, 3, 1))})
        
        numerical_grad_check(operation_class=TensorSetSlice,
                             test_inputs=[Parameter(randn(3, 11, 17, 1, 1)),
                                          Parameter(randn(2, 17, 1, 1))],
                             kwargs={'key': ([True, False, True], 1, slice(None))})
        
        try:        
            # This test case should raise assertion because of duplicate 2's in the key
            numerical_grad_check(operation_class=TensorSetSlice,
                                 test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1)),
                                              Parameter(randn(2, 4, 2, 3, 5, 1, 1, 1))],
                                 kwargs={'key': [[0, 1, 2, 5], [6, 2, 3, 4]]})
        
            assert False  # This should not get here
        except:
            assert True

        try:        
            # This test case should raise assertion because of duplicate 2's in the key
            numerical_grad_check(operation_class=TensorSetSlice,
                                 test_inputs=[Parameter(randn(7, 5, 3, 5, 1, 1, 1)),
                                              Parameter(randn(2, 4, 2, 3, 5, 1, 1, 1))],
                                 kwargs={'key': ([[0, 1, 2, 5], [6, 2, 3, 4]], slice(2, 4, 1), slice(None))})
            assert False  # This should not get here
        except:
            assert True


    def test_slice_grad(self):
        x = Parameter(randn(2, 3, 5))
        y = x ** 2
        y.retain_grad()
        z = Parameter(randn(2, 4))
        y[:, 0, 1:] = z
        (y ** 2).sum().backward()
        
        assert np.all((z.grad != 0) == np.array([[True, True, True, True], 
                                                 [True, True, True, True]]))
        
        assert np.all((x.grad != 0) == np.array([[[ True, False, False, False, False],
                                                  [ True,  True,  True,  True,  True],
                                                  [ True,  True,  True,  True,  True]],
                                        
                                                 [[ True, False, False, False, False],
                                                  [ True,  True,  True,  True,  True],
                                                  [ True,  True,  True,  True,  True]]]))
        
        assert np.all((y.grad != 0) == np.array([[[ True,  True,  True,  True,  True],
                                                  [ True,  True,  True,  True,  True],
                                                  [ True,  True,  True,  True,  True]],
                                        
                                                 [[ True,  True,  True,  True,  True],
                                                  [ True,  True,  True,  True,  True],
                                                  [ True,  True,  True,  True,  True]]]))
    
    def test_overlapping_slice(self):
        x = Parameter([0, 1, 2, 3, 4, 5])
        y = x ** 2
        a = Parameter([1, 2])
        b = Parameter([1, 2, 3, 4])
        c = Parameter([2, 3, 4])
        
        y[2:4] = a
        y[1:5] = b
        y[3:6] = c
        
        y.sum().backward()
        
        assert np.all(a.grad == np.array([0, 0]))
        assert np.all(b.grad == np.array([1, 1, 0, 0]))
        assert np.all(c.grad == np.array([1, 1, 1]))
        

    def test_boolean_slice_grad(self):
        x = Parameter(randn(2, 3))
        y = x ** 2
        y.retain_grad()
        z = Parameter([1, 2, 3])
        
        mask = Tensor([[True, True, False], [False, True, False]]).astype(bool)
        y[mask] = z
        y.sum().backward()
        assert np.all(y[mask].data == np.array([1, 2, 3]))
        
        assert np.all((x.grad == 0) == np.array([[True, True, False], [False, True, False]]))
        assert np.all(y.grad == np.array([[1, 1, 1], [1, 1, 1]]))
        assert np.all(z.grad == np.array([1, 1, 1]))

    
    def test_tensor_reshape(self):
        numerical_grad_check(operation_class=TensorReshape,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11))],
                             kwargs={'new_shape': (-1,)})

        numerical_grad_check(operation_class=TensorReshape,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11))],
                             kwargs={'new_shape': (12, -1,)})

        numerical_grad_check(operation_class=TensorReshape,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11))],
                             kwargs={'new_shape': (3, 4, -1, 7)})
        
        
    def test_tensor_transpose(self):
        numerical_grad_check(operation_class=TensorSwapaxes,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))],
                             kwargs={'dim0': 2, 'dim1': 5})
        
        
        numerical_grad_check(operation_class=TensorTranspose,
                             test_inputs=[Parameter(randn(7, 2, 3, 5, 1, 1, 1))])
        
        
    def test_tensor_masked_fill(self):
        mask = Parameter((np.random.random(size=(1, 5, 7, 1)) > 0.5).astype(float))

        numerical_grad_check(operation_class=TensorMaskedFill,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11))],
                             kwargs={'mask': mask, 'fill_value': 123})
        
        
    def test_batch_matrix_multiply(self):
        numerical_grad_check(operation_class=BatchMatrixMultiply,
                             test_inputs=[Parameter(randn(3, 4, 5, 7, 11)),
                                          Parameter(randn(3, 4, 5, 11, 13))])
        
    
    def test_conv(self):
        numerical_grad_check(operation_class=Conv2dOperation,
                             test_inputs=[Parameter(randn(5, 3, 13, 17)),
                                          Parameter(randn(3, 2, 4, 5))],
                             kwargs={'stride': (2, 3),
                                     'padding': (3, 4)})
        
    def test_pool(self):
        numerical_grad_check(operation_class=MaxPool2dOperation,
                             test_inputs=[Parameter(randn(5, 3, 13, 17))],
                             kwargs={'kernel_size': (3, 4),
                                     'padding': (1, 2)})

        numerical_grad_check(operation_class=MaxPool2dOperation,
                             test_inputs=[Parameter(randn(5, 3, 13, 17))],
                             kwargs={'kernel_size': (3, 4),
                                     'padding': (1, 1)})

        numerical_grad_check(operation_class=AvgPool2dOperation,
                             test_inputs=[Parameter(randn(5, 3, 13, 17))],
                             kwargs={'kernel_size': (3, 4),
                                     'padding': (1, 2)})

        numerical_grad_check(operation_class=AvgPool2dOperation,
                             test_inputs=[Parameter(randn(5, 3, 13, 17))],
                             kwargs={'kernel_size': (3, 4),
                                     'padding': (1, 1)})
        
        
    def test_concat(self):
        numerical_grad_check(operation_class=TensorConcatenation,
                             test_inputs=[Parameter(randn(10, 12, 24)),
                                          Parameter(randn(10, 15, 24)),
                                          Parameter(randn(10, 13, 24))],
                             kwargs={'axis': -2})
        
        numerical_grad_check(operation_class=TensorConcatenation,
                             test_inputs=[Parameter(randn(10, 12, 24)),
                                          Parameter(randn(10, 12, 24)),
                                          Parameter(randn(10, 12, 24))])
        

    def test_repeat_interleave(self):
        numerical_grad_check(operation_class=TensorRepeatInterleave,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'repeats': 3, 'axis': -1})

        numerical_grad_check(operation_class=TensorRepeatInterleave,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'repeats': 3, 'axis': -2})

        numerical_grad_check(operation_class=TensorRepeatInterleave,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'repeats': 3, 'axis': 2})

        numerical_grad_check(operation_class=TensorRepeatInterleave,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'repeats': 3, 'axis': 4})

        numerical_grad_check(operation_class=TensorRepeatInterleave,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'repeats': 3, 'axis': 0})

        numerical_grad_check(operation_class=TensorRepeatInterleave,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'repeats': 3, 'axis': None})


    def test_flip(self):
        numerical_grad_check(operation_class=TensorFlip,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': None})

        numerical_grad_check(operation_class=TensorFlip,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': 1})

        numerical_grad_check(operation_class=TensorFlip,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': -1})


        numerical_grad_check(operation_class=TensorFlip,
                             test_inputs=[Parameter(randn(2, 3, 5, 7, 11))],
                             kwargs={'axis': (-1, 2)})

    def test_topk(self):
        for _ in range(10):
            for axis in range(5):
                for k in range(1, 3):
                    p = Parameter(1e3 * np.random.normal(size=(2, 3, 4, 5, 4)))
                    numerical_grad_check(operation_class=TopKOperation,
                                         test_inputs=[p],
                                         kwargs={'k': k, 'axis': axis},
                                         atol=0.5)
                    
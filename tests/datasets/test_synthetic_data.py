# Copyright 2021 MosaicML. All Rights Reserved.

from typing import Optional

import pytest

from composer.datasets import SyntheticDataset
from composer.datasets.synthetic import SyntheticDataLabelType, SyntheticDataType


@pytest.mark.parametrize('data_type', [
    SyntheticDataType.GAUSSIAN,
    SyntheticDataLabelType.CLASSIFICATION_INT,
])
@pytest.mark.parametrize('label_type', [
    SyntheticDataLabelType.CLASSIFICATION_ONE_HOT,
    SyntheticDataLabelType.CLASSIFICATION_INT,
    SyntheticDataLabelType.RANDOM_INT,
])
def test_synthetic_data_creation(data_type: SyntheticDataType, label_type: SyntheticDataLabelType):
    if data_type == SyntheticDataType.SEPARABLE and label_type != SyntheticDataLabelType.CLASSIFICATION_INT:
        # skip because not supported
        return

    dataset_size = 1000
    data_shape = (3, 32, 32)
    num_samples_to_create = 10
    num_classes = 10
    label_shape = (1, 10, 12)
    dataset = SyntheticDataset(total_dataset_size=dataset_size,
                               data_shape=data_shape,
                               num_unique_samples_to_create=num_samples_to_create,
                               data_type=data_type,
                               label_type=label_type,
                               num_classes=num_classes,
                               label_shape=label_shape)

    assert len(dataset) == dataset_size

    # verify datapoints are correct
    x, y = dataset[0]
    assert x.size() == data_shape
    if label_type == SyntheticDataLabelType.CLASSIFICATION_INT:
        assert isinstance(y.item(), int)
    elif label_type == SyntheticDataLabelType.CLASSIFICATION_ONE_HOT:
        assert y.size() == (num_classes,)
        assert min(y) == 0
        assert max(y) == 1
    elif label_type == SyntheticDataLabelType.RANDOM_INT:
        assert y.size() == label_shape

    # check that points were allocated in memory after the first call to __getitem__
    assert dataset.input_data is not None
    assert dataset.input_target is not None
    # check that the correct number of points were allocated in memory
    assert dataset.input_data.size()[0] == num_samples_to_create
    assert dataset.input_target.size()[0] == num_samples_to_create

    # verify that you can getch points outside the num_samples_to_create range
    # (still within the total dataset size range)
    x, y = dataset[num_samples_to_create + 1]
    assert x is not None
    assert y is not None


@pytest.mark.parametrize('label_type', [
    SyntheticDataLabelType.CLASSIFICATION_ONE_HOT,
    SyntheticDataLabelType.CLASSIFICATION_INT,
])
@pytest.mark.parametrize('num_classes', [None, 0])
def test_synthetic_classification_param_validation(label_type: SyntheticDataLabelType, num_classes: Optional[int]):
    with pytest.raises(ValueError):
        SyntheticDataset(total_dataset_size=10, data_shape=(2, 2), label_type=label_type, num_classes=num_classes)

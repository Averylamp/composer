# Copyright 2021 MosaicML. All Rights Reserved.

from unittest.mock import MagicMock

import pytest
from torch.cuda import device_count

from composer.callbacks import MemoryMonitorHparams
from composer.datasets.synthetic import SyntheticDatasetHparams
from composer.trainer import TrainerHparams
from composer.trainer.devices.device_gpu import DeviceGPU


def _do_trainer_fit(mosaic_trainer_hparams: TrainerHparams, testing_with_gpu: bool = False):
    memory_monitor_hparams = MemoryMonitorHparams()
    mosaic_trainer_hparams.callbacks.append(memory_monitor_hparams)

    mosaic_trainer_hparams.ddp.fork_rank_0 = False
    mosaic_trainer_hparams.max_epochs = 1

    mosaic_trainer_hparams.total_batch_size = 50

    trainer = mosaic_trainer_hparams.initialize_object()

    # Default model uses CPU
    if testing_with_gpu:
        trainer.device = DeviceGPU(True, 1)

    log_destination = MagicMock()
    log_destination.will_log.return_value = True
    trainer.logger.backends = [log_destination]
    trainer.fit()

    assert isinstance(mosaic_trainer_hparams.train_dataset, SyntheticDatasetHparams)
    num_train_samples = mosaic_trainer_hparams.train_dataset.total_dataset_size
    num_train_steps = num_train_samples // mosaic_trainer_hparams.total_batch_size

    expected_calls = num_train_steps * mosaic_trainer_hparams.max_epochs

    return log_destination, expected_calls


@pytest.mark.timeout(60)
def test_memory_monitor_cpu(mosaic_trainer_hparams: TrainerHparams):
    log_destination, _ = _do_trainer_fit(mosaic_trainer_hparams, testing_with_gpu=False)

    memory_monitor_called = False
    for log_call in log_destination.log_metric.mock_calls:
        metrics = log_call[1][3]
        if "memory/alloc_requests" in metrics:
            if metrics["memory/alloc_requests"] > 0:
                memory_monitor_called = True
                break
    assert not memory_monitor_called


@pytest.mark.timeout(60)
def test_memory_monitor_gpu(mosaic_trainer_hparams: TrainerHparams):
    n_cuda_devices = device_count()
    if n_cuda_devices > 0:
        log_destination, expected_calls = _do_trainer_fit(mosaic_trainer_hparams, testing_with_gpu=True)

        num_memory_monitor_calls = 0
        for log_call in log_destination.log_metric.mock_calls:
            metrics = log_call[1][3]
            if "memory/alloc_requests" in metrics:
                if metrics["memory/alloc_requests"] > 0:
                    num_memory_monitor_calls += 1
        assert num_memory_monitor_calls == expected_calls

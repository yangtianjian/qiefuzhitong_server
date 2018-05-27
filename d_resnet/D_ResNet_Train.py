#!/usr/bin/env python
# -*- coding: utf-8 -*-
import chainer
import numpy as np
import os
from D_ResNet import D_ResNet
from dataset import get_skin_data
import chainer.functions as F

def trend_predict(data):
    model = chainer.links.Classifier(D_ResNet())
    optimizer = chainer.optimizers.MomentumSGD(lr=0.01, momentum=0.9)
    train_set, test_set = get_skin_data()
    train_iter = chainer.iterators.SerialIterator(train_set, 40,shuffle=True)
    test_iter = chainer.iterators.SerialIterator(test_set, 40, repeat=False, shuffle=True)
    stop_trigger = (10000, 'epoch')
    optimizer.setup(model)
    updater = chainer.training.updater.StandardUpdater(train_iter, optimizer)
    trainer = chainer.training.Trainer(updater, stop_trigger)
    trainer.extend(chainer.training.extensions.Evaluator(test_iter, model))
    trainer.extend(chainer.training.extensions.LogReport())
    trainer.extend(chainer.training.extensions.snapshot())
    trainer.extend(chainer.training.extensions.PrintReport(['epoch', 'main/loss', 'validation/main/loss', 'main/accuracy', 'validation/main/accuracy', 'elapsed_time']))
    trainer.extend(chainer.training.extensions.ProgressBar())
    #chainer.serializers.load_npz('model.npz', model)
    return F.softmax(model.predictor(data))


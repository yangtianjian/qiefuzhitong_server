#!/usr/bin/env python
# -*- coding: utf-8 -*-
import chainer
import chainer.functions as F
from chainer import initializers
import chainer.links as L
import time


class BottleNeckA(chainer.Chain):
    def __init__(self, in_size, ch, out_size, stride=1):
        super(BottleNeckA, self).__init__()
        initialW = initializers.HeNormal()
        with self.init_scope():

            self.conv1 = L.Convolution2D(
                in_size, ch, 3, 2, 0, initialW=initialW, nobias=True)
            self.bn1 = L.BatchNormalization(ch)
            self.conv2 = L.Convolution2D(
                ch, ch, 3, 1, 0, initialW=initialW, nobias=True)
            self.bn2 = L.BatchNormalization(ch)
            self.conv3 = L.Convolution2D(
                ch, out_size, 3, 1, 0, initialW=initialW, nobias=True)
            self.bn3 = L.BatchNormalization(out_size)

            self.conv4 = L.Convolution2D(
                in_size, out_size, 11, 2, 0, initialW=initialW, nobias=True)
            self.bn4 = L.BatchNormalization(out_size)

    def __call__(self, x):
        h1 = F.relu(self.bn1(self.conv1(x)))
        h1 = F.relu(self.bn2(self.conv2(h1)))
        h1 = self.bn3(self.conv3(h1))

        h2 = self.bn4(self.conv4(x))
        return F.relu(h1 + h2)

class BottleNeckB(chainer.Chain):

    def __init__(self, in_size, ch):
        # Out size equal to in size
        super(BottleNeckB, self).__init__()
        initialW = initializers.HeNormal()
        with self.init_scope():
            self.conv1 = L.Convolution2D(
                in_size, ch, 3, 1, 1, initialW=initialW, nobias=True)
            self.bn1 = L.BatchNormalization(ch)
            self.conv2 = L.Convolution2D(
                ch, ch, 3, 1, 1, initialW=initialW, nobias=True)
            self.bn2 = L.BatchNormalization(ch)
            self.conv3 = L.Convolution2D(
                ch, in_size, 3, 1, 1, initialW=initialW, nobias=True)
            self.bn3 = L.BatchNormalization(in_size)


    def __call__(self, x):
        h = F.relu(self.bn1(self.conv1(x)))
        h = F.relu(self.bn2(self.conv2(h)))
        h = self.bn3(self.conv3(h))
        return F.relu(h + x)


class Block(chainer.Chain):

    def __init__(self, layer, in_size, ch, out_size, stride=1):
        super(Block, self).__init__()
        self.add_link('a', BottleNeckA(in_size, ch, out_size, stride))
        for i in range(1, layer):
            self.add_link('b{}'.format(i), BottleNeckB(out_size, ch))
        self.layer = layer

    def __call__(self, x):
        h = self.a(x)
        for i in range(1, self.layer):
            h = self['b{}'.format(i)](h)
        return h


class ResNet(chainer.Chain):
    def __init__(self):
        super(ResNet, self).__init__()
        with self.init_scope():
            self.conv1 = L.Convolution2D(
                3, 64, 3, 2, 1, initialW=initializers.HeNormal(), nobias=True)
            self.bn1 = L.BatchNormalization(64)
            self.res2 = Block(3, 64, 64, 128, 1)
            self.res3 = Block(4, 128, 64, 32)
            self.fc = L.Linear(1568, 3)

    def __call__(self, x):
        h = self.bn1(self.conv1(x)) 
        h = F.max_pooling_2d(F.relu(h), 3, stride=1, pad=1)
        h = self.res2(h)
        h = self.res3(h)

        h = F.average_pooling_2d(h, 3, stride=1)
        h = self.fc(h)
        return h
import torch.nn as nn
import torch.optim as optim
from densenet import densenet121


def make_model():

    model = densenet121(pretrained=True)

    # make all params untrainable
    for p in model.parameters():
        p.requires_grad = False

    # reset the last fc layer
    model.classifier = nn.Linear(1024, 256)
    # model_size: penultimate_layer_output_dim,
    # 201: 1920, 169: 1664, 121: 1024

    # make some other params trainable
    trainable_params = [
        'features.norm5.weight',
        'features.norm5.bias',
        'features.denseblock4.denselayer16.conv.2.weight',
        'features.denseblock4.denselayer15.conv.2.weight'
    ]
    for n, p in model.named_parameters():
        if n in trainable_params:
            p.requires_grad = True

    # create different parameter groups
    classifier_weights = [model.classifier.weight]
    classifier_biases = [model.classifier.bias]
    features_weights = [
        p for n, p in model.named_parameters()
        if n in trainable_params and 'conv.2' in n
    ]
    features_bn_weights = [
        p for n, p in model.named_parameters()
        if n in trainable_params and 'norm5.weight' in n
    ]
    features_bn_biases = [
        p for n, p in model.named_parameters()
        if n in trainable_params and 'bias' in n
    ]

    # set different learning rates
    # but they are not actually used
    classifier_lr = 1e-1
    features_lr = 1e-1

    # you need to tune only weight decay and momentum here
    optimizer = optim.SGD([
        {'params': classifier_weights, 'lr': classifier_lr, 'weight_decay': 1e-2},
        {'params': classifier_biases, 'lr': classifier_lr},

        {'params': features_weights, 'lr': features_lr, 'weight_decay': 1e-2},
        {'params': features_bn_weights, 'lr': features_lr},
        {'params': features_bn_biases, 'lr': features_lr}
    ], momentum=0.9, nesterov=True)

    # loss function
    criterion = nn.CrossEntropyLoss().cuda()
    # move the model to gpu
    model = model.cuda()
    return model, criterion, optimizer
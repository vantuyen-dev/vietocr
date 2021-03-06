import torch
from torch import nn
from torchvision.models import resnet50
from torchvision.models.resnet import Bottleneck
from einops import rearrange
from torch.hub import load_state_dict_from_url

resnet50_url = 'https://download.pytorch.org/models/resnet50-19c8e357.pth'

class Resnet50(nn.Module):
    def __init__(self, hidden=256):
        super().__init__()
        self.backbone = resnet50(pretrained=False)
        self.backbone.inplanes = 64

        layers = [3, 4, 6, 3]
        block = Bottleneck

        self.conv1 = nn.Conv2d(3, self.backbone.inplanes, kernel_size=7, stride=(2, 2), padding=3,
                                               bias=False)

        self.backbone.layer1 = self.backbone._make_layer(block, 64, layers[0])
        self.backbone.layer2 = self.backbone._make_layer(block, 128, layers[1], stride=2)
        self.backbone.layer3 = self.backbone._make_layer(block, 256, layers[2], stride=2)
        self.backbone.layer4 = self.backbone._make_layer(block, 512, layers[3], stride=(2,1))

        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=(1, 1), padding=1)
        self.conv = nn.Conv2d(2048, hidden, 1)
        
        state_dict = load_state_dict_from_url(resnet50_url,
                                              progress=True)
        self.backbone.load_state_dict(state_dict)
        
    def forward(self, inputs):
        x = self.backbone.conv1(inputs)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.maxpool(x)

        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)

        conv = self.conv(x)
        conv = rearrange(conv, 'b d h w -> b d (w h)')
        conv = conv.permute(-1, 0, 1)

        return conv


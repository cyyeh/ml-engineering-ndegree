import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
import os
from google.cloud import storage

from PIL import Image
from PIL import ImageFile

from collections import OrderedDict  # pylint: disable=g-importing-member


"""Bottleneck ResNet v2 with GroupNorm and Weight Standardization."""
class StdConv2d(nn.Conv2d):
    def forward(self, x):
        w = self.weight
        v, m = torch.var_mean(w, dim=[1, 2, 3], keepdim=True, unbiased=False)
        w = (w - m) / torch.sqrt(v + 1e-10)
        return F.conv2d(x, w, self.bias, self.stride, self.padding,
                        self.dilation, self.groups)


def conv3x3(cin, cout, stride=1, groups=1, bias=False):
    return StdConv2d(cin, cout, kernel_size=3, stride=stride,
                     padding=1, bias=bias, groups=groups)


def conv1x1(cin, cout, stride=1, bias=False):
    return StdConv2d(cin, cout, kernel_size=1, stride=stride,
                     padding=0, bias=bias)


def tf2th(conv_weights):
    """Possibly convert HWIO to OIHW."""
    if conv_weights.ndim == 4:
        conv_weights = conv_weights.transpose([3, 2, 0, 1])
    return torch.from_numpy(conv_weights)


class PreActBottleneck(nn.Module):
    """Pre-activation (v2) bottleneck block.

    Follows the implementation of "Identity Mappings in Deep Residual Networks":
    https://github.com/KaimingHe/resnet-1k-layers/blob/master/resnet-pre-act.lua

    Except it puts the stride on 3x3 conv when available.
    """

    def __init__(self, cin, cout=None, cmid=None, stride=1):
        super().__init__()
        cout = cout or cin
        cmid = cmid or cout//4

        self.gn1 = nn.GroupNorm(32, cin)
        self.conv1 = conv1x1(cin, cmid)
        self.gn2 = nn.GroupNorm(32, cmid)
        self.conv2 = conv3x3(cmid, cmid, stride)  # Original code has it on conv1!!
        self.gn3 = nn.GroupNorm(32, cmid)
        self.conv3 = conv1x1(cmid, cout)
        self.relu = nn.ReLU(inplace=True)

        if (stride != 1 or cin != cout):
            # Projection also with pre-activation according to paper.
            self.downsample = conv1x1(cin, cout, stride)

    def forward(self, x):
        out = self.relu(self.gn1(x))
        
        # Residual branch
        residual = x
        if hasattr(self, 'downsample'):
            residual = self.downsample(out)

        # Unit's branch
        out = self.conv1(out)
        out = self.conv2(self.relu(self.gn2(out)))
        out = self.conv3(self.relu(self.gn3(out)))

        return out + residual

    def load_from(self, weights, prefix=''):
        convname = 'standardized_conv2d'
        with torch.no_grad():
            self.conv1.weight.copy_(tf2th(weights[f'{prefix}a/{convname}/kernel']))
            self.conv2.weight.copy_(tf2th(weights[f'{prefix}b/{convname}/kernel']))
            self.conv3.weight.copy_(tf2th(weights[f'{prefix}c/{convname}/kernel']))
            self.gn1.weight.copy_(tf2th(weights[f'{prefix}a/group_norm/gamma']))
            self.gn2.weight.copy_(tf2th(weights[f'{prefix}b/group_norm/gamma']))
            self.gn3.weight.copy_(tf2th(weights[f'{prefix}c/group_norm/gamma']))
            self.gn1.bias.copy_(tf2th(weights[f'{prefix}a/group_norm/beta']))
            self.gn2.bias.copy_(tf2th(weights[f'{prefix}b/group_norm/beta']))
            self.gn3.bias.copy_(tf2th(weights[f'{prefix}c/group_norm/beta']))
        if hasattr(self, 'downsample'):
            w = weights[f'{prefix}a/proj/{convname}/kernel']
            self.downsample.weight.copy_(tf2th(w))


class ResNetV2(nn.Module):
    """Implementation of Pre-activation (v2) ResNet mode."""

    def __init__(self, block_units, width_factor, head_size=21843, zero_head=False):
        super().__init__()
        wf = width_factor  # shortcut 'cause we'll use it a lot.

        # The following will be unreadable if we split lines.
        # pylint: disable=line-too-long
        self.root = nn.Sequential(OrderedDict([
            ('conv', StdConv2d(3, 64*wf, kernel_size=7, stride=2, padding=3, bias=False)),
            ('pad', nn.ConstantPad2d(1, 0)),
            ('pool', nn.MaxPool2d(kernel_size=3, stride=2, padding=0)),
            # The following is subtly not the same!
            # ('pool', nn.MaxPool2d(kernel_size=3, stride=2, padding=1)),
        ]))

        self.body = nn.Sequential(OrderedDict([
            ('block1', nn.Sequential(OrderedDict(
                [('unit01', PreActBottleneck(cin=64*wf, cout=256*wf, cmid=64*wf))] +
                [(f'unit{i:02d}', PreActBottleneck(cin=256*wf, cout=256*wf, cmid=64*wf)) for i in range(2, block_units[0] + 1)],
            ))),
            ('block2', nn.Sequential(OrderedDict(
                [('unit01', PreActBottleneck(cin=256*wf, cout=512*wf, cmid=128*wf, stride=2))] +
                [(f'unit{i:02d}', PreActBottleneck(cin=512*wf, cout=512*wf, cmid=128*wf)) for i in range(2, block_units[1] + 1)],
            ))),
            ('block3', nn.Sequential(OrderedDict(
                [('unit01', PreActBottleneck(cin=512*wf, cout=1024*wf, cmid=256*wf, stride=2))] +
                [(f'unit{i:02d}', PreActBottleneck(cin=1024*wf, cout=1024*wf, cmid=256*wf)) for i in range(2, block_units[2] + 1)],
            ))),
            ('block4', nn.Sequential(OrderedDict(
                [('unit01', PreActBottleneck(cin=1024*wf, cout=2048*wf, cmid=512*wf, stride=2))] +
                [(f'unit{i:02d}', PreActBottleneck(cin=2048*wf, cout=2048*wf, cmid=512*wf)) for i in range(2, block_units[3] + 1)],
            ))),
        ]))
        # pylint: enable=line-too-long

        self.zero_head = zero_head
        self.head = nn.Sequential(OrderedDict([
            ('gn', nn.GroupNorm(32, 2048*wf)),
            ('relu', nn.ReLU(inplace=True)),
            ('avg', nn.AdaptiveAvgPool2d(output_size=1)),
            ('conv', nn.Conv2d(2048*wf, head_size, kernel_size=1, bias=True)),
        ]))

    def forward(self, x):
        x = self.head(self.body(self.root(x)))
        assert x.shape[-2:] == (1, 1)  # We should have no spatial shape left.
        return x[...,0,0]

    def load_from(self, weights, prefix='resnet/'):
        with torch.no_grad():
            self.root.conv.weight.copy_(tf2th(weights[f'{prefix}root_block/standardized_conv2d/kernel']))  # pylint: disable=line-too-long
            self.head.gn.weight.copy_(tf2th(weights[f'{prefix}group_norm/gamma']))
            self.head.gn.bias.copy_(tf2th(weights[f'{prefix}group_norm/beta']))
            if self.zero_head:
                nn.init.zeros_(self.head.conv.weight)
                nn.init.zeros_(self.head.conv.bias)
            else:
                self.head.conv.weight.copy_(tf2th(weights[f'{prefix}head/conv2d/kernel']))  # pylint: disable=line-too-long
                self.head.conv.bias.copy_(tf2th(weights[f'{prefix}head/conv2d/bias']))

        for bname, block in self.body.named_children():
            for uname, unit in block.named_children():
                unit.load_from(weights, prefix=f'{prefix}{bname}/{uname}/')
                

class DogBreedPrediction(object):
    def __init__(self, model_file):
        super(DogBreedPrediction, self).__init__()
        # VGG-16 pretrained model
        self._dog_detector = models.vgg16(pretrained=True)
        # BiT fine-tuned model
        self._dog_breed_classifier = ResNetV2([3, 4, 23, 3], width_factor=1, head_size=133, zero_head=True)
        self._dog_breed_classifier.load_state_dict(
            torch.load(model_file, map_location=torch.device('cpu')))
        # https://pytorch.org/hub/pytorch_vision_vgg/
        # both models use the same preprocess step
        self._preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])
        self._class_names = ['Affenpinscher', 'Afghan hound', 'Airedale terrier', 'Akita', 'Alaskan malamute', 'American eskimo dog',
        'American foxhound', 'American staffordshire terrier', 'American water spaniel', 'Anatolian shepherd dog', 'Australian cattle dog',
        'Australian shepherd', 'Australian terrier', 'Basenji', 'Basset hound', 'Beagle', 'Bearded collie', 'Beauceron', 'Bedlington terrier',
        'Belgian malinois', 'Belgian sheepdog', 'Belgian tervuren', 'Bernese mountain dog', 'Bichon frise', 'Black and tan coonhound',
        'Black russian terrier', 'Bloodhound', 'Bluetick coonhound', 'Border collie', 'Border terrier', 'Borzoi', 'Boston terrier',
        'Bouvier des flandres', 'Boxer', 'Boykin spaniel', 'Briard', 'Brittany', 'Brussels griffon', 'Bull terrier', 'Bulldog', 'Bullmastiff',
        'Cairn terrier', 'Canaan dog', 'Cane corso', 'Cardigan welsh corgi', 'Cavalier king charles spaniel', 'Chesapeake bay retriever', 'Chihuahua',
        'Chinese crested', 'Chinese shar-pei', 'Chow chow', 'Clumber spaniel', 'Cocker spaniel', 'Collie', 'Curly-coated retriever', 'Dachshund',
        'Dalmatian', 'Dandie dinmont terrier', 'Doberman pinscher', 'Dogue de bordeaux', 'English cocker spaniel', 'English setter', 'English springer spaniel',
        'English toy spaniel', 'Entlebucher mountain dog', 'Field spaniel', 'Finnish spitz', 'Flat-coated retriever', 'French bulldog', 
        'German pinscher', 'German shepherd dog', 'German shorthaired pointer', 'German wirehaired pointer', 'Giant schnauzer', 'Glen of imaal terrier',
        'Golden retriever', 'Gordon setter', 'Great dane', 'Great pyrenees', 'Greater swiss mountain dog', 'Greyhound', 'Havanese', 'Ibizan hound',
        'Icelandic sheepdog', 'Irish red and white setter', 'Irish setter', 'Irish terrier', 'Irish water spaniel', 'Irish wolfhound', 'Italian greyhound',
        'Japanese chin', 'Keeshond', 'Kerry blue terrier', 'Komondor', 'Kuvasz', 'Labrador retriever', 'Lakeland terrier', 'Leonberger',
        'Lhasa apso', 'Lowchen', 'Maltese', 'Manchester terrier', 'Mastiff', 'Miniature schnauzer', 'Neapolitan mastiff', 'Newfoundland',
        'Norfolk terrier', 'Norwegian buhund', 'Norwegian elkhound', 'Norwegian lundehund', 'Norwich terrier', 'Nova scotia duck tolling retriever',
        'Old english sheepdog', 'Otterhound', 'Papillon', 'Parson russell terrier', 'Pekingese', 'Pembroke welsh corgi', 'Petit basset griffon vendeen',
        'Pharaoh hound', 'Plott', 'Pointer', 'Pomeranian', 'Poodle', 'Portuguese water dog', 'Saint bernard', 'Silky terrier', 'Smooth fox terrier',
        'Tibetan mastiff', 'Welsh springer spaniel', 'Wirehaired pointing griffon', 'Xoloitzcuintli', 'Yorkshire terrier']

        
    def _detect_dog(self, input_batch):
        with torch.no_grad():
            output = self._dog_detector(input_batch)
            
        output_idx = output.data.numpy().argmax()
        return 151 <= output_idx  <= 268
    
    
    def _predit_top3_dog_breeds(self, input_batch):
        def get_class_name(classes):
            return map(lambda x: self._class_names[x], classes)

        with torch.no_grad():
            output = self._dog_breed_classifier(input_batch)

        # the following code is to get top-3 dog breeds with respective probability
        softmax = nn.Softmax(dim=1) # to get probability distribution over all classes
        softmax_output = softmax(output.data)
        top3_pred_values, top3_pred_indices = torch.topk(softmax_output, 3)
        top3_pred_prob =  np.squeeze(top3_pred_values).numpy()
        top3_pred_classes = np.squeeze(top3_pred_indices).numpy()

        return list(zip(get_class_name(top3_pred_classes), top3_pred_prob))
    
    
    def predict(self, img_path):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
            
        input_img = Image.open(img_path)
        input_tensor = self._preprocess(input_img)
        input_batch = input_tensor.unsqueeze(0) # (224, 224, 3) -> (1, 224, 224, 3)
        
        if self._detect_dog(input_batch):
            return {
                'dog_detected:': True,
                'message': self._predit_top3_dog_breeds(input_batch),
            }
        else:
            return {
                'dog_detected': False,
                'message': 'No dog is detected, please try another image again!',
            }

# keep model as global variable so we don't have to reload
# it in case of warm invocations
model = None

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket"""
    storage_client = storage.Client()
    bucket =  storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    blob.download_to_filename(destination_file_name)
    
    print(f'Blob {source_blob_name} is downloaded to {destination_file_name}.')
    
# cloud function entry point
def handler(request):
    global model
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'dog-breed-classifier')
    SOURCE_BLOB_NAME = os.getenv('SOURCE_BLOB_NAME', 'model_transfer.pt')
    DESTINATION_FILE_NAME = f'/tmp/{SOURCE_BLOB_NAME}'
    
    if model is None:
        download_blob(BUCKET_NAME, SOURCE_BLOB_NAME, DESTINATION_FILE_NAME)
        model = DogBreedPrediction(DESTINATION_FILE_NAME)
        
    # testing
    download_blob(BUCKET_NAME, 'testing/Brittany_02625.jpg', 'tmp/Brittany_02625.jpg')
    print(model.predict('tmp/Brittany_02625.jpg'))
    print()
    download_blob(BUCKET_NAME, 'testing/sky.jpeg', 'tmp/sky.jpeg')
    print(model.predict('tmp/sky.jpeg'))
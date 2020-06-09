import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
from PIL import ImageFile

CLASS_NAMES = [
    'Affenpinscher', 'Afghan hound', 'Airedale terrier', 'Akita', 'Alaskan malamute', 'American eskimo dog',
    'American foxhound', 'American staffordshire terrier', 'American water spaniel', 'Anatolian shepherd dog',
    'Australian cattle dog', 'Australian shepherd', 'Australian terrier', 'Basenji', 'Basset hound', 'Beagle',
    'Bearded collie', 'Beauceron', 'Bedlington terrier', 'Belgian malinois', 'Belgian sheepdog', 'Belgian tervuren',
    'Bernese mountain dog', 'Bichon frise', 'Black and tan coonhound', 'Black russian terrier', 'Bloodhound',
    'Bluetick coonhound', 'Border collie', 'Border terrier', 'Borzoi', 'Boston terrier', 'Bouvier des flandres',
    'Boxer', 'Boykin spaniel', 'Briard', 'Brittany', 'Brussels griffon', 'Bull terrier', 'Bulldog', 'Bullmastiff',
    'Cairn terrier', 'Canaan dog', 'Cane corso', 'Cardigan welsh corgi', 'Cavalier king charles spaniel',
    'Chesapeake bay retriever', 'Chihuahua', 'Chinese crested', 'Chinese shar-pei', 'Chow chow', 'Clumber spaniel',
    'Cocker spaniel', 'Collie', 'Curly-coated retriever', 'Dachshund', 'Dalmatian', 'Dandie dinmont terrier',
    'Doberman pinscher', 'Dogue de bordeaux', 'English cocker spaniel', 'English setter', 'English springer spaniel',
    'English toy spaniel', 'Entlebucher mountain dog', 'Field spaniel', 'Finnish spitz', 'Flat-coated retriever',
    'French bulldog', 'German pinscher', 'German shepherd dog', 'German shorthaired pointer',
    'German wirehaired pointer', 'Giant schnauzer', 'Glen of imaal terrier', 'Golden retriever', 'Gordon setter',
    'Great dane', 'Great pyrenees', 'Greater swiss mountain dog', 'Greyhound', 'Havanese', 'Ibizan hound',
    'Icelandic sheepdog', 'Irish red and white setter', 'Irish setter', 'Irish terrier', 'Irish water spaniel',
    'Irish wolfhound', 'Italian greyhound', 'Japanese chin', 'Keeshond', 'Kerry blue terrier', 'Komondor', 'Kuvasz',
    'Labrador retriever', 'Lakeland terrier', 'Leonberger', 'Lhasa apso', 'Lowchen', 'Maltese', 'Manchester terrier',
    'Mastiff', 'Miniature schnauzer', 'Neapolitan mastiff', 'Newfoundland', 'Norfolk terrier', 'Norwegian buhund',
    'Norwegian elkhound', 'Norwegian lundehund', 'Norwich terrier', 'Nova scotia duck tolling retriever',
    'Old english sheepdog', 'Otterhound', 'Papillon', 'Parson russell terrier', 'Pekingese', 'Pembroke welsh corgi',
    'Petit basset griffon vendeen', 'Pharaoh hound', 'Plott', 'Pointer', 'Pomeranian', 'Poodle', 'Portuguese water dog',
    'Saint bernard', 'Silky terrier', 'Smooth fox terrier', 'Tibetan mastiff', 'Welsh springer spaniel',
    'Wirehaired pointing griffon', 'Xoloitzcuintli', 'Yorkshire terrier']


class DogBreedPrediction(object):
    def __init__(self, model_file):
        super(DogBreedPrediction, self).__init__()
        # MobileNet v2 pretrained model
        self._dog_detector = models.mobilenet_v2(pretrained=True)
        # MobileNet v2 fine-tuned model
        self._dog_breed_classifier = torch.load(model_file)
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
        self._class_names = CLASS_NAMES

    def _detect_dog(self, input_batch):
        self._dog_detector.eval()

        with torch.no_grad():
            output = self._dog_detector(input_batch)

        output_idx = output.data.numpy().argmax()
        return 151 <= output_idx <= 268

    def _predit_top3_dog_breeds(self, input_batch):
        def get_class_name(classes):
            return map(lambda x: self._class_names[x], classes)

        self._dog_breed_classifier.eval()

        with torch.no_grad():
            output = self._dog_breed_classifier(input_batch)

        # the following code is to get top-3 dog breeds with respective probability
        # to get probability distribution over all classes
        softmax = nn.Softmax(dim=1)
        softmax_output = softmax(output.data)
        top3_pred_values, top3_pred_indices = torch.topk(softmax_output, 3)
        top3_pred_prob = np.squeeze(top3_pred_values).numpy()
        top3_pred_classes = np.squeeze(top3_pred_indices).numpy()

        top3_results = [
            {'breed': pair[0], 'prob': str(pair[1])}
            for pair in zip(get_class_name(top3_pred_classes), top3_pred_prob)
        ]

        return top3_results

    def predict(self, img_path):
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        with Image.open(img_path) as input_img:
            input_tensor = self._preprocess(input_img)
            # (224, 224, 3) -> (1, 224, 224, 3)
            input_batch = input_tensor.unsqueeze(0)

            if self._detect_dog(input_batch):
                return {
                    'dog_detected': True,
                    'message': self._predit_top3_dog_breeds(input_batch),
                }
            else:
                return {
                    'dog_detected': False,
                    'message': 'No dog is detected, please try another image again!',
                }

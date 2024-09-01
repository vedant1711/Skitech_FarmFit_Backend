from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import torch
import io
from PIL import Image
from torchvision import transforms
import torch.nn as nn


def ConvBlock(in_channels, out_channels, pool=False):
    layers = [nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
             nn.BatchNorm2d(out_channels),
             nn.ReLU(inplace=True)]
    if pool:
        layers.append(nn.MaxPool2d(4))
    return nn.Sequential(*layers)


# Model Architecture
class ResNet9(nn.Module):
    def __init__(self, in_channels, num_diseases):
        super().__init__()

        self.conv1 = ConvBlock(in_channels, 64)
        self.conv2 = ConvBlock(64, 128, pool=True)  # out_dim : 128 x 64 x 64
        self.res1 = nn.Sequential(ConvBlock(128, 128), ConvBlock(128, 128))

        self.conv3 = ConvBlock(128, 256, pool=True)  # out_dim : 256 x 16 x 16
        self.conv4 = ConvBlock(256, 512, pool=True)  # out_dim : 512 x 4 x 44
        self.res2 = nn.Sequential(ConvBlock(512, 512), ConvBlock(512, 512))

        self.classifier = nn.Sequential(nn.MaxPool2d(4),
                                        nn.Flatten(),
                                        nn.Linear(512, num_diseases))

    def forward(self, xb):  # xb is the loaded batch
        out = self.conv1(xb)
        out = self.conv2(out)
        out = self.res1(out) + out
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.res2(out) + out
        out = self.classifier(out)
        return out



# Predefined disease classes
disease_classes = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust',
    'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
    'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy',
    'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

main_dic = {
    "Apple___Apple_scab": {
        "disease_name": "Apple Scab",
        "causes": {
            "1": " Apple scab overwinters primarily in fallen leaves and in the soil. Disease development is favored by wet, cool weather that generally occurs in spring and early summer"
            ,
            "2": "Fungal spores are carried by wind, rain or splashing water from the ground to flowers, leaves or fruit. During damp or rainy periods, newly opening apple leaves are extremely susceptible to infection. The longer the leaves remain wet, the more severe the infection will be. Apple scab spreads rapidly between 55-75 degrees Fahrenheit.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        }
    },
    "Apple___Black_rot": {
        "disease_name": "Apple Black Rot",
        "causes": {
            "1": "Black rot is caused by the fungus Botryosphaeria obtusa. The fungus overwinters in infected fruit and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        }
    },
    "Apple___Cedar_apple_rust": {
        "disease_name": "Apple Cedar Apple Rust",
        "causes": {
            "1": "Cedar apple rust is caused by the fungus Gymnosporangium juniperi-virginianae. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {

            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Apple___healthy": {
        "disease_name": "Apple Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Blueberry___healthy": {
        "disease_name": "Blueberry Healthy",
        "causes": {

            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "disease_name": "Cherry Powdery Mildew",
        "causes": {
            "1": "Powdery mildew is caused by the fungus Podosphaera leucotricha. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Cherry_(including_sour)___healthy": {
        "disease_name": "Cherry Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "disease_name": "Corn Gray Leaf Spot",
        "causes": {
            "1": "Gray leaf spot is caused by the fungus Cercospora zeae-maydis. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Corn_(maize)___Common_rust_": {
        "disease_name": "Corn Common Rust",
        "causes": {
            "1": "Common rust is caused by the fungus Puccinia sorghi. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "disease_name": "Corn Northern Leaf Blight",
        "causes": {
            "1": "Northern leaf blight is caused by the fungus Exserohilum turcicum. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Corn_(maize)___healthy": {
        "disease_name": "Corn Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Grape___Black_rot": {
        "disease_name": "Grape Black Rot",
        "causes": {
            "1": "Black rot is caused by the fungus Guignardia bidwellii. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {

            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },

    "Grape___Esca_(Black_Measles)": {
        "disease_name": "Grape Esca",
        "causes": {
            "1": "Esca is caused by the fungus Phaeoacremonium aleophilum. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "disease_name": "Grape Leaf Blight",
        "causes": {
            "1": "Leaf blight is caused by the fungus Isariopsis leaf spot. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Grape___healthy": {
        "disease_name": "Grape Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Orange___Haunglongbing_(Citrus_greening)": {

        "disease_name": "Orange Greening",
        "causes": {
            "1": "Citrus greening is caused by the bacterium Candidatus Liberibacter asiaticus. The bacterium overwinters in infected leaves and in the soil. The bacterium is spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
            "2": "The bacterium infects blossoms, leaves, and fruit. The bacterium enters the plant through wounds, such as those caused by insects or hail. The bacterium can also enter through the stomata (pores) on the underside of the leaves. The bacterium grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Peach___Bacterial_spot": {
        "disease_name": "Peach Bacterial Spot",
        "causes": {
            "1": "Bacterial spot is caused by the bacterium Xanthomonas campestris pv. pruni. The bacterium overwinters in infected leaves and in the soil. The bacterium is spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
            "2": "The bacterium infects blossoms, leaves, and fruit. The bacterium enters the plant through wounds, such as those caused by insects or hail. The bacterium can also enter through the stomata (pores) on the underside of the leaves. The bacterium grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Peach___healthy": {
        "disease_name": "Peach Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },

        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Pepper,_bell___Bacterial_spot": {
        "disease_name": "Pepper Bacterial Spot",
        "causes": {
            "1": "Bacterial spot is caused by the bacterium Xanthomonas campestris pv. vesicatoria. The bacterium overwinters in infected leaves and in the soil. The bacterium is spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
            "2": "The bacterium infects blossoms, leaves, and fruit. The bacterium enters the plant through wounds, such as those caused by insects or hail. The bacterium can also enter through the stomata (pores) on the underside of the leaves. The bacterium grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Pepper,_bell___healthy": {
        "disease_name": "Pepper Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Potato___Early_blight": {
        "disease_name": "Potato Early Blight",
        "causes": {
            "1": "Early blight is caused by the fungus Alternaria solani. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Potato___Late_blight": {
        "disease_name": "Potato Late Blight",
        "causes": {
            "1": "Late blight is caused by the fungus Phytophthora infestans. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Potato___healthy": {
        "disease_name": "Potato Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Raspberry___healthy": {

        "disease_name": "Raspberry Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Soybean___healthy": {
        "disease_name": "Soybean Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Squash___Powdery_mildew": {
        "disease_name": "Squash Powdery Mildew",
        "causes": {
            "1": "Powdery mildew is caused by the fungus Podosphaera xanthii. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Strawberry___Leaf_scorch": {
        "disease_name": "Strawberry Leaf Scorch",
        "causes": {
            "1": "Leaf scorch is caused by the fungus Colletotrichum acutatum. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Strawberry___healthy": {
        "disease_name": "Strawberry Healthy",
        "causes": {
            "1": "Heathy",
            "2": "",
        },
        "prevent": {
            "1": "Heathy",
            "2": "",
            "3": "",
        },
    },
    "Tomato___Bacterial_spot": {
        "disease_name": "Tomato Bacterial Spot",
        "causes": {
            "1": "Bacterial spot is caused by the bacterium Xanthomonas campestris pv. vesicatoria. The bacterium overwinters in infected leaves and in the soil. The bacterium is spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
            "2": "The bacterium infects blossoms, leaves, and fruit. The bacterium enters the plant through wounds, such as those caused by insects or hail. The bacterium can also enter through the stomata (pores) on the underside of the leaves. The bacterium grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The bacterium can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Early_blight": {
        "disease_name": "Tomato Early Blight",
        "causes": {
            "1": "Early blight is caused by the fungus Alternaria solani. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Late_blight": {

        "disease_name": "Tomato Late Blight",
        "causes": {
            "1": "Late blight is caused by the fungus Phytophthora infestans. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Leaf_Mold": {
        "disease_name": "Tomato Leaf Mold",
        "causes": {
            "1": "Leaf mold is caused by the fungus Sclerotinia sclerotiorum. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },

    "Tomato___Septoria_leaf_spot": {
        "disease_name": "Tomato Septoria Leaf Spot",
        "causes": {
            "1": "Septoria leaf spot is caused by the fungus Septoria lycopersici. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "disease_name": "Tomato Spider Mites Two-spotted Spider Mite",
        "causes": {
        },

        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Target_Spot": {
        "disease_name": "Tomato Target Spot",
        "causes": {
            "1": "Target spot is caused by the fungus Cercospora lycopersici. The fungus overwinters in infected leaves and in the soil. The fungus is spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
            "2": "The fungus infects blossoms, leaves, and fruit. The fungus enters the plant through wounds, such as those caused by insects or hail. The fungus can also enter through the stomata (pores) on the underside of the leaves. The fungus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The fungus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "disease_name": "Tomato Yellow Leaf Curl Virus",
        "causes": {
            "1": "Tomato yellow leaf curl virus is caused by the virus Begomovirus. The virus overwinters in infected leaves and in the soil. The virus is spread by splashing water, rain, insects, birds, and wind. The virus can survive in the soil for several years.",
            "2": "The virus infects blossoms, leaves, and fruit. The virus enters the plant through wounds, such as those caused by insects or hail. The virus can also enter through the stomata (pores) on the underside of the leaves. The virus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The virus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___Tomato_mosaic_virus": {
        "disease_name": "Tomato Mosaic Virus",
        "causes": {
            "1": "Tomato mosaic virus is caused by the virus Tobamovirus. The virus overwinters in infected leaves and in the soil. The virus is spread by splashing water, rain, insects, birds, and wind. The virus can survive in the soil for several years.",
            "2": "The virus infects blossoms, leaves, and fruit. The virus enters the plant through wounds, such as those caused by insects or hail. The virus can also enter through the stomata (pores) on the underside of the leaves. The virus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The virus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },
    "Tomato___healthy": {
        "disease_name": "Tomato Healthy",
        "causes": {
            "1": "Tomato mosaic virus is caused by the virus Tobamovirus. The virus overwinters in infected leaves and in the soil. The virus is spread by splashing water, rain, insects, birds, and wind. The virus can survive in the soil for several years.",
            "2": "The virus infects blossoms, leaves, and fruit. The virus enters the plant through wounds, such as those caused by insects or hail. The virus can also enter through the stomata (pores) on the underside of the leaves. The virus grows on the plant and produces spores that are spread by splashing water, rain, insects, birds, and wind. The virus can survive in the soil for several years.",
        },
        "prevent": {
            "1": "Choose resistant varieties when possible",
            "2": "Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring",
            "3": "Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.",
        },
    },

}

# Initialize the model
disease_model = ResNet9(3, len(disease_classes))
model_path = f"{settings.BASE_DIR}/app/utils/models/plant-disease-model.pth"
state_dict = torch.load(model_path, map_location=torch.device('cpu'))
disease_model.load_state_dict(state_dict)
disease_model.eval()


# Utility function to make predictions
def predict_image(img, model=disease_model):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    yb = model(img_u)
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds]
    return prediction


# Disease Prediction API View
class DiseasePredictionView(APIView):
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        img_bytes = request.FILES['image'].read()
        try:
            # Predict the disease
            prediction = predict_image(img_bytes)

            # Fetch the disease information from main_dic
            if prediction in main_dic:
                disease_info = main_dic[prediction]
                response_data = {
                    "disease_name": disease_info["disease_name"],
                    "causes": disease_info["causes"],
                    "prevent": disease_info["prevent"],
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Disease information not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


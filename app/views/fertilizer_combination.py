from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.models import Fertilizer, CropNutrientRequirement
import itertools


class FertilizerCombinationAPIView(APIView):
    def post(self, request):
        crop_name = request.data.get('crop_name')
        farm_area = request.data.get('farm_area')
        soil_n = request.data.get('n',0)
        soil_p = request.data.get('p',0)
        soil_k = request.data.get('k',0)

        crop_requirement = get_object_or_404(CropNutrientRequirement, crop_name=crop_name)

        net_n = max(crop_requirement.nitrogen_needed - soil_n, 0)
        net_p = max(crop_requirement.phosphorus_needed - soil_p, 0)
        net_k = max(crop_requirement.potassium_needed - soil_k, 0)
        remaining_requirements = [net_n, net_p, net_k]

        if net_n == 0 and net_p == 0 and net_k == 0:
            return Response({"message": "No additional fertilizer required."})

        fertilizers = Fertilizer.objects.all()
        fertilizer_dict = {fert.name: [fert.nitrogen_content, fert.phosphorus_content, fert.potassium_content] for fert in fertilizers}

        # Categorize fertilizers based on N, P, K content
        categorized_fertilizers = categorize_fertilizers(fertilizer_dict)

        # Generate valid fertilizer combinations
        valid_combinations = generate_combinations(categorized_fertilizers, remaining_requirements)

        # Prepare the response
        response_data = []
        for combination in valid_combinations:
            combination_details = {}
            for fert_name, amount in combination.items():
                combination_details[fert_name] = round(amount * farm_area, 3)
            response_data.append(combination_details)

        return Response(response_data[:5])


def categorize_fertilizers(fertilizers):
    npk_fertilizers = {}
    np_fertilizers = {}
    nk_fertilizers = {}
    pk_fertilizers = {}
    n_fertilizers = {}
    p_fertilizers = {}
    k_fertilizers = {}

    for fert_name, content in fertilizers.items():
        n, p, k = content
        if n > 0 and p > 0 and k > 0:
            npk_fertilizers[fert_name] = content
        elif n > 0 and p > 0:
            np_fertilizers[fert_name] = content
        elif n > 0 and k > 0:
            nk_fertilizers[fert_name] = content
        elif p > 0 and k > 0:
            pk_fertilizers[fert_name] = content
        elif n > 0:
            n_fertilizers[fert_name] = content
        elif p > 0:
            p_fertilizers[fert_name] = content
        elif k > 0:
            k_fertilizers[fert_name] = content

    return npk_fertilizers, np_fertilizers, nk_fertilizers, pk_fertilizers, n_fertilizers, p_fertilizers, k_fertilizers


def generate_combinations(fertilizer_groups, remaining_requirements):
    possible_combinations = []

    for r in range(1, len(fertilizer_groups) + 1):
        for combination in itertools.combinations(fertilizer_groups, r):
            combined_fert = {}
            combined_remaining = remaining_requirements[:]

            for fert_group in combination:
                for fert_name, fert_content in fert_group.items():
                    amount_needed = calculate_fertilizer_amount(combined_remaining, fert_content)
                    combined_remaining = update_remaining_requirements(combined_remaining, fert_content, amount_needed)

                    if fert_name in combined_fert:
                        combined_fert[fert_name] += amount_needed
                    else:
                        combined_fert[fert_name] = amount_needed

            if all(req <= 0 for req in combined_remaining):
                possible_combinations.append(combined_fert)

    return possible_combinations


def calculate_fertilizer_amount(remaining, content):
    n_content, p_content, k_content = content
    n_fert = remaining[0] / (n_content / 100) if n_content > 0 else float('inf')
    p_fert = remaining[1] / (p_content / 100) if p_content > 0 else float('inf')
    k_fert = remaining[2] / (k_content / 100) if k_content > 0 else float('inf')
    return min(n_fert, p_fert, k_fert)


def update_remaining_requirements(remaining, content, amount):
    return [
        remaining[0] - amount * (content[0] / 100),
        remaining[1] - amount * (content[1] / 100),
        remaining[2] - amount * (content[2] / 100)
    ]

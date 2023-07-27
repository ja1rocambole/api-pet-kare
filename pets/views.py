from django.shortcuts import render
from rest_framework.views import APIView, Request, Response, status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


from groups.models import Group
from traits.models import Trait
from .models import Pet
from .serializers import PetSerializer


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 2


# Create your views here.
class PetView(APIView, CustomPageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet_data = serializer.validated_data

        group_name = pet_data["group"]["scientific_name"]
        group_obj = Group.objects.filter(scientific_name__iexact=group_name).first()

        if not group_obj:
            group_obj = Group.objects.create(scientific_name=group_name)

        traits = pet_data.get("traits", [])

        trait_objects = []
        for trait in traits:
            trait_name = trait.get("name")
            trait_obj = Trait.objects.filter(name__iexact=trait_name).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(name=trait_name)

            trait_objects.append(trait_obj)

        pet = Pet.objects.create(
            name=pet_data["name"],
            age=pet_data["age"],
            weight=pet_data["weight"],
            sex=pet_data["sex"],
            group=group_obj,
        )

        for trait in trait_objects:
            pet.traits.add(trait)

        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request: Request):
        trait_parm = request.query_params.get("trait", None)

        if trait_parm:
            trait = Trait.objects.filter(name__iexact=trait_parm).first()

            pets = Pet.objects.filter(traits=trait)
        else:
            pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request, view=self)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id):
        try:
            pet = Pet.objects.get(id=pet_id)
        except:
            return Response({"detail": "Not found."})

        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        serializer = PetSerializer(data=request.data, partial=True)

        pet = get_object_or_404(Pet, id=pet_id)

        serializer.is_valid(raise_exception=True)

        pet_data = serializer.validated_data

        if "group" in pet_data:
            group_name = pet_data["group"]["scientific_name"]
            group_obj = Group.objects.filter(scientific_name__iexact=group_name).first()

            if not group_obj:
                group_obj = Group.objects.create(scientific_name=group_name)

            pet.group = group_obj

        if "traits" in pet_data:
            traits = pet_data["traits"]
            pet.traits.clear()

            trait_objects = []
            for trait in traits:
                trait_name = trait.get("name")
                trait_obj = Trait.objects.filter(name__iexact=trait_name).first()

                if not trait_obj:
                    trait_obj = Trait.objects.create(name=trait_name)

                trait_objects.append(trait_obj)

            print(trait_obj)
            for trait in trait_objects:
                pet.traits.add(trait)

        if "name" in pet_data:
            pet.name = pet_data["name"]
        if "age" in pet_data:
            pet.age = pet_data["age"]
        if "weight" in pet_data:
            pet.weight = pet_data["weight"]
        if "sex" in pet_data:
            pet.sex = pet_data["sex"]

        pet_serializer = PetSerializer(pet, partial=True)

        pet.save()

        return Response(pet_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)

        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

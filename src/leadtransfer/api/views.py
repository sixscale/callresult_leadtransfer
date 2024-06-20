import json
import logging
from datetime import datetime

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import CRMContactSerializer
from ..service.amocrm import send_lead_to_amocrm
from ..service import amocrm_moloko
from ..service.validation import ContactCreationData, LeadCreationData

logger = logging.getLogger(__name__)


class LeadCreationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"request_data: {json.dumps(request.data)}\n"
                    f"request_time: {datetime.now()}\n")
        deal_id = request.data.get("leads[status][0][id]", [""])[0]
        amocrm_moloko.handle_deal(deal_id)
        return Response(status=status.HTTP_200_OK)


class LeadTransferAPIView(CreateAPIView):
    serializer_class = CRMContactSerializer

    def post(self, request, *args, **kwargs):
        validated_contact = ContactCreationData.model_validate(request.data)
        validated_deal = LeadCreationData.model_validate(request.data)
        logger.info(f"request_data: {request.data}\n"
                    f"request_time: {datetime.now()}\n"
                    f"validated_contact: {validated_contact}\n"
                    f"validated_deal: {validated_deal}\n")
        send_lead_to_amocrm(
            validated_contact,
            validated_deal
        )
        return Response(status=status.HTTP_200_OK)

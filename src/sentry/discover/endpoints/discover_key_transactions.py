from __future__ import absolute_import

from django.db import transaction
from rest_framework.response import Response

from sentry.api.bases import KeyTransactionBase
from sentry.api.bases.organization import OrganizationPermission
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.discover.models import KeyTransaction
from sentry.discover.endpoints.serializers import KeyTransactionSerializer
from sentry.snuba.discover import query


class IsKeyTransactionEndpoint(KeyTransactionBase):
    permission_classes = (OrganizationPermission,)

    def get(self, request, organization):
        """ Get the Key Transactions for a user """
        if not self.has_feature(request, organization):
            return self.response(status=404)

        project = self.get_project(request, organization)

        transaction = request.GET.get("transaction")

        try:
            KeyTransaction.objects.get(
                organization=organization,
                owner=request.user,
                project=project,
                transaction=transaction,
            )
            return Response({"isKey": True}, status=200)
        except KeyTransaction.DoesNotExist:
            return Response({"isKey": False}, status=200)


class KeyTransactionEndpoint(KeyTransactionBase):
    permission_classes = (OrganizationPermission,)

    def post(self, request, organization):
        """ Create a Key Transaction """
        if not self.has_feature(request, organization):
            return Response(status=404)

        project = self.get_project(request, organization)

        base_filter = {"organization": organization, "project": project, "owner": request.user}

        with transaction.atomic():
            serializer = KeyTransactionSerializer(data=request.data, context=base_filter)
            if serializer.is_valid():
                data = serializer.validated_data
                base_filter["transaction"] = data["transaction"]

                KeyTransaction.objects.create(**base_filter)
                return Response(status=201)
            return Response(serializer.errors, status=400)

    def get(self, request, organization):
        """ Get the Key Transactions for a user """
        if not self.has_feature(request, organization):
            return self.response(status=404)

        params = self.get_filter_params(request, organization)
        fields = request.GET.getlist("field")[:]
        orderby = self.get_orderby(request)

        queryset = KeyTransaction.objects.filter(organization=organization, owner=request.user)

        if not queryset.exists():
            raise ResourceDoesNotExist

        results = query(
            fields,
            request.GET.get("query"),
            params,
            orderby=orderby,
            referrer="discover.key_transactions",
            # The snuba query for transactions is of the form
            # (transaction="1" AND project=1) OR (transaction="2" and project=2) ...
            # which the schema intentionally doesn't support so we cannot do an AND in OR
            # so here the "and" operator is being instead to do an AND in OR query
            conditions=[
                [
                    # First layer is Ands
                    [
                        # Second layer is Ors
                        [
                            "and",
                            [
                                [
                                    "equals",
                                    # Without the outer ' here, the transaction will be treated as another column
                                    # instead of a string. This isn't an injection risk since snuba is smart enough to
                                    # handle escaping for us.
                                    ["transaction", u"'{}'".format(transaction.transaction)],
                                ],
                                ["equals", ["project_id", transaction.project.id]],
                            ],
                        ],
                        "=",
                        1,
                    ]
                    for transaction in queryset
                ]
            ],
        )

        return Response(
            self.handle_results_with_meta(request, organization, params["project_id"], results),
            status=200,
        )

    def delete(self, request, organization):
        """ Remove a Key transaction for a user """
        if not self.has_feature(request, organization):
            return self.response(status=404)

        project = self.get_project(request, organization)
        transaction = request.data["transaction"]

        try:
            model = KeyTransaction.objects.get(
                transaction=transaction, organization=organization, project=project
            )
        except KeyTransaction.DoesNotExist:
            raise ResourceDoesNotExist

        model.delete()

        return Response(status=204)

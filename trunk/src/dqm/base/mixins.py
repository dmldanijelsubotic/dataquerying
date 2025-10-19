class ViewSetAddUser:
    def perform_create(self, serializer):
        """
        Set the user to the current user when creating an object
        """
        serializer.save(user=self.request.user)


class AddIncludeQueryParam:
    def get_serializer(self, *args, **kwargs):
        # Extract the ?include=... query parameter
        include_param = self.request.query_params.get("include")

        if include_param:
            # Split it into a list of field names
            include = [field.strip() for field in include_param.split(",")]
            kwargs["include"] = include

        return super().get_serializer(*args, **kwargs)

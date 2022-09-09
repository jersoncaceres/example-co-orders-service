class JsonModelMixin(object):
    def to_json(self, remove_null=False):
        result = {}

        if not remove_null:
            for field in self.json_fields:
                result[field] = getattr(self, field)
        else:
            for field in self.json_fields:
                value = getattr(self, field)
                if value is not None:
                    result[field] = getattr(self, field)
        return result

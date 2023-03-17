from drf_writable_nested.mixins import NestedUpdateMixin


class ModifiedWritableNestedUpdateMixin(NestedUpdateMixin):
    """
    Modified NestedUpdateMixin for preventing deletion of relation if no PK is provided.
    Here, default update method of NestedUpdateMixin is overwritten for removing deleting feature.

    'self.delete_reverse_relations_if_need(instance, reverse_relations)' commented
    for prevention in update method
    """

    def update(self, instance, validated_data):
        relations, reverse_relations = self._extract_relations(validated_data)

        # Create or update direct relations (foreign key, one-to-one)
        self.update_or_create_direct_relations(
            validated_data,
            relations,
        )

        # Update instance
        instance = super(NestedUpdateMixin, self).update(
            instance,
            validated_data,
        )
        self.update_or_create_reverse_relations(instance, reverse_relations)
        # self.delete_reverse_relations_if_need(instance, reverse_relations)
        instance.refresh_from_db()
        return instance

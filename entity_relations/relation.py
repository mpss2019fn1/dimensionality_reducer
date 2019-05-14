class Relation:

    def __init__(self, name, relative_occurrence):
        self.name = name
        self.relative_occurrence = relative_occurrence
        self._relation_values = {}

    def add_relation_value(self, relation_value_name, relation_value_occurrence):
        self._relation_values[relation_value_name] = relation_value_occurrence

    def get_relation_value_occurrence(self, relation_value_name):
        return self._relation_values[relation_value_name]

    def __iter__(self):
        yield from self._relation_values

    def __repr__(self):
        self.__str__()

    def __str__(self):
        relation_values_repr = "\n\t".join(
            f"{name}: {self._relation_values[name]}%" for name in self._relation_values)
        return f"{self.name}: {self.relative_occurrence}%\n{relation_values_repr}"

    def as_html(self):
        relation_values_repr = "".join(
            f"\t» {name}: <i>{self._relation_values[name]}%</i><br>" for name in self._relation_values)
        return f"<b>{self.name}: {self.relative_occurrence}%</b><br>{relation_values_repr}"

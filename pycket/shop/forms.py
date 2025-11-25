from math import ceil, floor

from django import forms


class SeatSelectionForm(forms.Form):
    def __init__(self, seating_grid, stage_width, *args, **kwargs):
        super(SeatSelectionForm, self).__init__(*args, **kwargs)
        self.seating_grid = seating_grid
        self.rows = self.generate_seat_fields(seating_grid)
        self.stage_width = stage_width
        if len(seating_grid) == 0:
            self._seating_row_padding = 0
        else:
            if len(seating_grid[0]) > stage_width:
                self._seating_row_padding_left = 0
                self._seating_row_padding_right = 0
                stage_row_padding = (len(seating_grid[0]) - stage_width) / 2
                self._stage_row_padding_left = floor(stage_row_padding)
                self._stage_row_padding_right = ceil(stage_row_padding)
            else:
                seating_row_padding = (stage_width - len(seating_grid[0])) / 2
                self._seating_row_padding_left = ceil(seating_row_padding)
                self._seating_row_padding_right = floor(seating_row_padding)
                self._stage_row_padding_left = 0
                self._stage_row_padding_right = 0

    def generate_seat_fields(self, seating_grid):
        rows = []
        for row_index, row in enumerate(seating_grid):
            field_names_row = []
            for seat_index, seat in enumerate(row):
                field_name = f"seat_{row_index}_{seat_index}"
                if seat is False:
                    self.fields[field_name] = forms.BooleanField(
                        required=False,
                        widget=forms.CheckboxInput(attrs={"class": "seat-checkbox"}),
                    )
                    field_names_row.append(field_name)
                elif seat is True:
                    self.fields[field_name] = forms.BooleanField(
                        required=False,
                        widget=forms.CheckboxInput(
                            attrs={
                                "class": "seat-checkbox",
                                "disabled": True,
                                "checked": True,
                            }
                        ),
                    )
                    field_names_row.append(field_name)
                else:
                    field_names_row.append(None)
            rows.append(field_names_row)

        return rows

    def clean(self):
        cleaned_data = super().clean()
        seats = []
        for row_index, row in enumerate(self.rows):
            for seat_index, field_name in enumerate(row):
                if field_name is not None and cleaned_data.get(field_name):
                    if self.seating_grid[row_index][seat_index] is None:
                        raise forms.ValidationError("Invalid seat selection")
                    seats.append((row_index, seat_index))
        cleaned_data["seats"] = seats
        try:
            cleaned_data["num_seats"] = int(self.data.get("num_seats"))
        except:
            raise ValueError("invalid number of seats")
        try:
            cleaned_data["note"] = self.data.get("note")
        except:
            cleaned_data["note"] = ""
        return cleaned_data

    def rows_for_display(self):
        for i, r in list(enumerate(self.rows))[::-1]:
            yield i + 1, r

    def seating_row_padding_left(self):
        return range(self._seating_row_padding_left)

    def seating_row_padding_right(self):
        return range(self._seating_row_padding_right)

    def stage_row_padding_left(self):
        return range(self._stage_row_padding_left)

    def stage_row_padding_right(self):
        return range(self._stage_row_padding_right)

# Copyright (C) 2009-2022, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland, and CMP3 contributors
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

"""Module that defines traits-based classes for Connectome Mapper 3 BIDS App Interface TraitsUI View."""

from traits.api import Property
from traitsui.api import TabularAdapter


class MultiSelectAdapter(TabularAdapter):
    """This adapter is used by left and right tables for selection of subject to be processed."""

    # Titles and column names for each column of a table.
    # In this example, each table has only one column.
    columns = [("", "myvalue")]

    # Set a default integer width for the column
    width = int(100)  # This ensures width is explicitly set as an integer

    # Property to format the display text in the 'myvalue' column
    myvalue_text = Property()

    def _get_myvalue_text(self):
        """Getter for Property 'myvalue_text', used to format the display text."""
        return f"sub-{self.item}"

    def get_width(self, object, trait, row):
        """Ensure the width returned is always an integer."""
        return int(super().get_width(object, trait, row))  # Cast the width to int


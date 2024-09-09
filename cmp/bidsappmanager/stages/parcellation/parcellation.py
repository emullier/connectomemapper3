# Copyright (C) 2009-2022, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland, and CMP3 contributors
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

"""Definition of parcellation config and stage UI classes."""

# General imports
import os
import subprocess

from traits.api import *
from traitsui.api import *

# Own imports
from cmp.stages.parcellation.parcellation import ParcellationConfig, ParcellationStage


class ParcellationConfigUI(ParcellationConfig):
    """Class that extends the :class:`ParcellationConfig` with graphical components.

    Attributes
    ----------
    custom_parcellation_view : traits.ui.View
        VGroup that displays the different parts of a custom BIDS parcellation file

    traits_view : traits.ui.View
        TraitsUI view that displays the attributes of this class, e.g.
        the parameters for the stage

    See also
    ---------
    cmp.stages.parcellation.parcellation.ParcellationConfig
    """
    cortex_option = Enum("Desikan [D]", "Destrieux [X]", "DKT40 [T]", "Brainnetome [B]", 
                         "Brodmann [R]", "Campbell [C]", "Kleist [K]", "Lausanne [L]",
                         "HCPMM [H]", "Schaefer [S]", "Smith [M]", "VonEconomo [V]",
                         "Yeo 7 and 17 networks [Y]", "Flechsig [F]")
    basal_ganglia_option = Enum("Aseg [F]", "First [R]")
    thalamus_option = Enum("Aseg [F]", "First [R]", "Thalamic nuclei [I]", "MIAL [M]")
    amygdala_option = Enum("Aseg [F]", "Amygdala nuclei [I]", "First [R]")
    hippocampus_option = Enum("Aseg [F]", "First [R]", "Hippocampal subfields [I]", "Head body and tail [H]")
    hypothalamus_option = Enum("Aseg [F]",  "Hypothalamic nuclei [I]")
    cerebellum_option = Enum("Aseg [F]")
    brainstem_option = Enum("Aseg [F]",  "Brainstem regions [I]")
    gyral_wm_option = Enum("Subcortical WM parcellation using FreeSurfer [F]")
    

    #custom_parcellation_group = VGroup(
    #    cortex_option = Enum("Desikan", "Destrieux"),
    #    basal_ganglia_option = Enum("aseg", "first"),
    #    label="Custom parcellation"
    #

    traits_view = View(
            Item("cortex_option", label="Cortex"),
            Item("basal_ganglia_option", label="Basal Ganglia"),
            Item("thalamus_option", label="Thalamus"),
            Item("amygdala_option", label="Amygdala"),
            Item("hippocampus_option", label="Hippocampus"),
            Item("hypothalamus_option", label="Hypothalamus"),
            Item("cerebellum_option", label="Cerebellum"),
            Item("brainstem_option", label="Brainstem"),
            Item("gyral_wm_option", label="Gyral white matter")
    )


class ParcellationStageUI(ParcellationStage):
    """Class that extends the :class:`ParcellationStage` with graphical components.

    Attributes
    ----------
    inspect_output_button : traits.ui.Button
        Button that displays the selected output in an appropriate viewer
        (present only in the window for quality inspection)

    inspect_outputs_view : traits.ui.View
        TraitsUI view that displays the quality inspection window of this stage

    config_view : traits.ui.View
        TraitsUI view that displays the configuration window of this stage

    See also
    ---------
    cmp.stages.parcellation.parcellation.ParcellationStage
    """

    inspect_output_button = Button("View")

    inspect_outputs_view = View(
        Group(
            Item("name", editor=TitleEditor(), show_label=False),
            Group(
                Item("inspect_outputs_enum", show_label=False),
                Item(
                    "inspect_output_button",
                    enabled_when='inspect_outputs_enum!="Outputs not available"',
                    show_label=False,
                ),
                label="View outputs",
                show_border=True,
            ),
        ),
        scrollable=True,
        resizable=True,
        kind="livemodal",
        title="Inspect stage outputs",
        buttons=["OK", "Cancel"],
    )

    config_view = View(
        Group(
            Item("name", editor=TitleEditor(), show_label=False),
            Group(
                Item("config", style="custom", show_label=False),
                label="Configuration",
                show_border=True,
            ),
        ),
        scrollable=True,
        resizable=True,
        height=350,
        width=600,
        kind="livemodal",
        title="Edit stage configuration",
        buttons=["OK", "Cancel"],
    )

    def __init__(self, pipeline_mode, subject, session, bids_dir, output_dir):
        """Constructor of the ParcellationStageUI class.

        Parameters
        -----------
        pipeline_mode : string
            Pipeline mode that can be "Diffusion" or "fMRI"

        bids_dir : path
            BIDS root directory

        output_dir : path
            Output directory

        See also
        ---------
        cmp.stages.parcellation.parcellation.ParcellationStage.__init_
        cmp.cmpbidsappmanager.stages.parcellation.parcellation.ParcellationStageUI
        """
        ParcellationStage.__init__(self, pipeline_mode, subject, session, bids_dir, output_dir)
        self.config = ParcellationConfigUI()

    def _inspect_output_button_fired(self, info):
        """Display the selected output when ``inspect_output_button`` is clicked.

        Parameters
        ----------
        info : traits.ui.Button
            Button object
        """
        subprocess.Popen(self.inspect_outputs_dict[self.inspect_outputs_enum])

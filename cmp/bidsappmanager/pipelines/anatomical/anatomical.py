# Copyright (C) 2009-2022, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland, and CMP3 contributors
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

"""Anatomical pipeline UI Class definition."""

import os
import glob
import shutil

from traits.api import *
from traitsui.api import *
from traitsui.qt.extra.qt_view import QtView
from pyface.ui.qt.image_resource import ImageResource

# Own import
from cmtklib.bids.io import __cmp_directory__, __nipype_directory__, __freesurfer_directory__
from cmp.bidsappmanager.stages.parcellation.parcellation import ParcellationStageUI
from cmp.pipelines.anatomical.anatomical import (
    AnatomicalPipeline,
)
from cmtklib.util import return_button_style_sheet


class AnatomicalPipelineUI(AnatomicalPipeline):
    """Class that extends the :class:`~cmp.pipelines.anatomical.anatomical.AnatomicalPipeline` with graphical components.

    Attributes
    ----------
    segmentation : traits.ui.Button
        Button to open the window for configuration or quality inspection
        of the segmentation stage depending on the ``view_mode``

    parcellation : traits.ui.Button
        Button to open the window for configuration or quality inspection
        of the segmentation stage depending on the ``view_mode``

    view_mode : ['config_view', 'inspect_outputs_view']
        Variable used to control the display of either (1) the configuration
        or (2) the quality inspection of stage of the pipeline

    pipeline_group : traitsUI panel
        Panel defining the layout of the buttons of the stages with corresponding images

    traits_view : QtView
        QtView that includes the ``pipeline_group`` panel

    See also
    ---------
    cmp.pipelines.anatomical.anatomical.AnatomicalPipeline
    """

    segmentation = Button()

    parcellation = Button()

    view_mode = Enum("config_view", ["config_view", "inspect_outputs_view"])

    pipeline_group = VGroup(
        # Item('parcellation',editor=CustomEditor(image=ImageResource('parcellation'))),show_labels=False),
        HGroup(
            spring,
            UItem(
                "parcellation",
                style="custom",
                width=222,
                height=129,
                resizable=False,
                style_sheet=return_button_style_sheet(
                    ImageResource("parcellation").absolute_path
                ),
            ),
            spring,
            show_labels=False,
            label="",
        ),
        spring,
        springy=True,
    )

    traits_view = QtView(Include("pipeline_group"))

    def __init__(self, project_info):
        """Constructor of the AnatomicalPipelineUI class.

        Parameters
        -----------
        project_info : cmp.project.ProjectInfo
            CMP_Project_Info object that stores general information
            such as the BIDS root and output directories (see
            :class_`cmp.project.CMP_Project_Info` for more details)

        See also
        ---------
        cmp.pipelines.anatomical.AnatomicalPipeline.__init__
        """
        AnatomicalPipeline.__init__(self, project_info)

        if len(project_info.subject_sessions) > 0:
            subject_id = "_".join((self.subject, self.global_conf.subject_session))
            subject_session = self.global_conf.subject_session
        else:
            subject_id = self.subject
            subject_session = ""

        self.stages = {
            "Parcellation": ParcellationStageUI(
                pipeline_mode="Diffusion",
                subject=self.subject,
                session=subject_session,
                bids_dir=project_info.base_directory,
                output_dir=project_info.output_directory,
            ),
        }

        for stage in list(self.stages.keys()):
            if project_info.subject_session != "":
                self.stages[stage].stage_dir = os.path.join(
                    self.base_directory,
                    "derivatives",
                    __nipype_directory__,
                    self.subject,
                    project_info.subject_session,
                    self.pipeline_name,
                    self.stages[stage].name,
                )
            else:
                self.stages[stage].stage_dir = os.path.join(
                    self.base_directory,
                    "derivatives",
                    __nipype_directory__,
                    self.subject,
                    self.pipeline_name,
                    self.stages[stage].name,
                )



    def _parcellation_fired(self, info):
        """Method that displays the window for the parcellation stage.

        The window changed accordingly to the value of ``view_mode`` to be
        in configuration or quality inspection mode.

        Parameters
        -----------
        info : traits.ui.Button
            The parcellation button object
        """
        self.stages["Parcellation"].configure_traits(view=self.view_mode)

    def check_input(self, layout):
        """Method that checks if inputs of the anatomical pipeline are available in the datasets.

        Parameters
        -----------
        layout : bids.BIDSLayout
            BIDSLayout object used to query

        Returns
        -------
        valid_inputs : bool
            True in all inputs of the anatomical pipeline are available
        """
        print("**** Check Inputs  ****")
        t1_available = False
        valid_inputs = False

        types = layout.get_modalities()

        subjid = self.subject.split("-")[1]

        if self.global_conf.subject_session != "":
            sessid = self.global_conf.subject_session.split("-")[1]

        files = layout.get(
            subject=subjid,
            session=None if (self.global_conf.subject_session == "") else sessid,
            suffix="T1w",
            extension="nii.gz",
        )
        if len(files) > 0:
            T1_file = files[0].filename
            print(T1_file)
        else:
            error(
                message="T1w image not found for subject %s, session %s."
                % (subjid, self.global_conf.subject_session),
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )
            return False

        for typ in types:
            if typ == "T1w" and os.path.isfile(T1_file):
                print("T1_file found: %s" % T1_file)
                t1_available = True

        if t1_available:
            # Copy diffusion data to derivatives / cmp  / subject / dwi
            if self.global_conf.subject_session == "":
                out_T1_file = os.path.join(
                    self.derivatives_directory, __cmp_directory__,
                    self.subject, "anat",
                    self.subject + "_T1w.nii.gz",
                )
            else:
                out_T1_file = os.path.join(
                    self.derivatives_directory, __cmp_directory__,
                    self.subject, self.global_conf.subject_session, "anat",
                    f'{self.subject}_{self.global_conf.subject_session}_T1w.nii.gz',
                )

            if not os.path.isfile(out_T1_file):
                shutil.copy(src=T1_file, dst=out_T1_file)

            msg = "Inputs check finished successfully. \nAnatomical data (T1w) available."
            print(f'\tINFO: {msg}')
            valid_inputs = True
        else:
            msg = (
                "  * No anatomical data (T1w) available in folder "
                + os.path.join(self.base_directory, self.subject, 'anat')
                + "!\n"
            )
            print(f'\tERROR: Missing required inputs: {msg}')
            error(
                message=f"Missing required inputs:\n{msg} Please see documentation for more details.",
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )

        if self.stages["Parcellation"].config.parcellation_scheme == "Chimera":
            msg = ""

        return msg

    def check_output(self):
        """Method that checks if outputs of the anatomical pipeline are available.

        Returns
        --------
        valid_output : bool
            True is all outputs are found

        error_message : string
            Message in case there is an error
        """
        t1_available = False
        brain_available = False
        brainmask_available = False
        wm_available = False
        roivs_available = False
        valid_output = False

        subject = self.subject

        if self.global_conf.subject_session == "":
            anat_deriv_subject_directory = os.path.join(
                self.base_directory, "derivatives", __cmp_directory__, self.subject, "anat"
            )
        else:
            if self.global_conf.subject_session not in subject:
                anat_deriv_subject_directory = os.path.join(
                    self.base_directory, "derivatives", __cmp_directory__,
                    subject, self.global_conf.subject_session, "anat",
                )
                subject = "_".join((subject, self.global_conf.subject_session))
            else:
                anat_deriv_subject_directory = os.path.join(
                    self.base_directory, "derivatives", __cmp_directory__,
                    subject.split("_")[0], self.global_conf.subject_session, "anat",
                )

        T1_file = os.path.join(
            anat_deriv_subject_directory, subject + "_T1w_head.nii.gz"
        )
        brain_file = os.path.join(
            anat_deriv_subject_directory, subject + "_T1w_brain.nii.gz"
        )
        brainmask_file = os.path.join(
            anat_deriv_subject_directory, subject + "_T1w_brainmask.nii.gz"
        )
        wm_mask_file = os.path.join(
            anat_deriv_subject_directory, subject + "_T1w_class-WM.nii.gz"
        )
        roiv_files = glob.glob(
            anat_deriv_subject_directory + "/" + subject + "_T1w_parc_scale*.nii.gz"
        )

        error_message = ""

        if os.path.isfile(T1_file):
            t1_available = True
        else:
            error_message = (
                "Missing anatomical output file %s . Please re-run the anatomical pipeline"
                % T1_file
            )
            print(error_message)
            error(
                message=error_message,
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )

        if os.path.isfile(brain_file):
            brain_available = True
        else:
            error_message = (
                "Missing anatomical output file %s . Please re-run the anatomical pipeline"
                % brain_file
            )
            print(error_message)
            error(
                message=error_message,
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )

        if os.path.isfile(brainmask_file):
            brainmask_available = True
        else:
            error_message = (
                "Missing anatomical output file %s . Please re-run the anatomical pipeline"
                % brainmask_file
            )
            print(error_message)
            error(
                message=error_message,
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )

        if os.path.isfile(wm_mask_file):
            wm_available = True
        else:
            error_message = (
                "Missing anatomical output file %s . Please re-run the anatomical pipeline"
                % wm_mask_file
            )
            print(error_message)
            error(
                message=error_message,
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )

        cnt1 = 0
        cnt2 = 0
        for roiv_file in roiv_files:
            cnt1 = cnt1 + 1
            if os.path.isfile(roiv_file):
                cnt2 = cnt2 + 1
        if cnt1 == cnt2:
            roivs_available = True
        else:
            error_message = (
                "Missing %g/%g anatomical parcellation output files. Please re-run the anatomical pipeline"
                % (cnt1 - cnt2, cnt1)
            )
            print(error_message)
            error(
                message=error_message,
                title="Error",
                buttons=["OK", "Cancel"],
                parent=None,
            )

        if (
            t1_available is True
            and brain_available is True
            and brainmask_available is True
            and wm_available is True
            and roivs_available is True
        ):
            print("valid deriv/anat output")
            valid_output = True

        return valid_output, error_message

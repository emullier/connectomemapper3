

import os
import numpy as np
from nipype.interfaces import fsl

in_path = '/home/localadmin/DATA/ds-sample/derivatives/nipype-1.8.6/sub-01/ses-01/fMRI_pipeline/preprocessing_stage/converter/fMRI_despike.nii.gz'
out_path = '/home/localadmin/DATA/ds-sample/derivatives/nipype-1.8.6/sub-01/ses-01/fMRI_pipeline/preprocessing_stage/motion_correction/fMRI_despike.nii.gz'

mcflt = fsl.MCFLIRT()
mcflt.inputs.in_file = in_path
mcflt.inputs.out_file = out_path
mcflt.inputs.save_mats = True
mcflt.inputs.mean_vol = True
mcflt.inputs.save_plots = True

res = mcflt.run()  

print(res)
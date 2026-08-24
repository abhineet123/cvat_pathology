import torch

from cellpose import models as cellpose_models

from cell_seg_params import CellposeParams
from cell_seg_utils import linux_path
from cell_seg_wsi import CellSegWSIBase


class CellposeWSI(CellSegWSIBase):
    def __init__(self, params: CellposeParams, file_mode):
        CellSegWSIBase.__init__(
            self,
            name=f"cellpose-{params.type}",
            file_mode=file_mode,
            params=params,
        )
        self.params: CellposeParams = params
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        m_type_to_pt = dict(
            sam="cpsam",
            sam2="cpsam_v2",
            dino="cpdino-vitb",
            dino2="cpdino",
        )
        pt = m_type_to_pt[params.type]

        m_subtype_to_threshold = dict(
            p20=2.0,
            p10=1.0,
            p5=0.5,
            p1=0.1,
            p0=0,
            n0=0,
            n1=-0.1,
            n2=-0.2,
            n5=-0.5,
            n10=-1.0,
            n20=-2.0,
            n50=-5.0,
        )
        if self.params.subtype:
            self.name = f"{self.name}-{params.subtype}"
            self.params.cellprob_threshold = m_subtype_to_threshold[self.params.subtype]
            print(f"setting cellprob_threshold to {self.params.cellprob_threshold}")

        self.diameter = self.params.cell_size / self.params.pixel_size
        self.predictor = cellpose_models.CellposeModel(
            device=self.device,
            pretrained_model=pt,
        )

    def detect(self, wsi_roi, roi_offset):
        image_h, image_w = wsi_roi.shape[:2]
        # image_np_t = image_np.transpose((2, 0, 1))

        # image_transformed = cellpose_transforms.convert_image(image_np_t, do_3D=False)
        # image_transformed = image_np

        # print(f"running cellpose inference on WSI of size {image_w} x {image_h}...")

        out = self.predictor.eval(
            wsi_roi,
            niter=1000,
            # diameter=self.diameter,
            diameter=None,
            normalize={"tile_norm_blocksize": self.params.tile_norm_blocksize},
            do_3D=False,
            augment=False,
            flow_threshold=self.params.flow_threshold,
            cellprob_threshold=self.params.cellprob_threshold,
            stitch_threshold=0.0,
            min_size=-1,
            batch_size=self.params.batch_size,
            bsize=self.params.tile_size,
            resample=True,
            channel_axis=None,
            z_axis=None,
            flow3D_smooth=0,
        )
        instance_mask = out[0]
        # flows = out[1]
        # cellprob = flows[-1]

        cells = self.instance_mask_to_cells(instance_mask, roi_offset)

        if self.params.show:
            self.show(cells, wsi_roi)

        return cells

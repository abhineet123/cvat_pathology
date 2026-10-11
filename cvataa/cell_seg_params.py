class CellSegParams:
    def __init__(self):
        self.show = 0
        self.cols = [
            "#000000",
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#f1a66d",
            "#ff00ff",
            "#00ffff",
            "#ffff00",
        ]


class StarDistParams(CellSegParams):
    def __init__(self):
        CellSegParams.__init__(self)


class CellVITParams(CellSegParams):
    """
    :ivar model_type:
        sam


    :ivar classifier:
        consep
        lizard
        midog
        nucls_main
        nucls_super
        ocelot
        panoptils
    """

    def __init__(self):
        CellSegParams.__init__(self)

        self.model_type = "sam"
        self.classifier = ""
        self.binary = 0
        self.mp = 0
        self.patch_size = 1024
        self.batch_size = 1
        self.geojson = 1
        self.compression = 1
        self.graph = 0
        self.gpu = 0
        self.resolution = 0.25
        self.chunk_size = 0


class CellposeParams(CellSegParams):
    def __init__(self):
        CellSegParams.__init__(self)

        self.type = "sam"
        self.subtype = ""

        self.pixel_size = 0.2632
        self.cell_size = 200

        self.flow_threshold = 0
        self.cellprob_threshold = -1
        self.tile_norm_blocksize = 0

        self.tile_size = 256
        self.batch_size = 64


class EnsembleParams:
    """
    :ivar dups: check for duplicates in each component model's annotations
        dups=1: remove any duplicates found
        dups=2: raise an error if any duplicates are found
    :ivar load: load annotations from cache
        load=1: load final annotations from ensemble cache
        load=2: load component model annotations from their respective caches and run ensemble on these
    """

    def __init__(self):
        self.sfx = ""
        self.nms_thresh = 0.3
        self.multi = 1
        self.enable_mask = 1
        self.dups = 1
        self.load = 0
        self.meta = EnsembleParams.Metadata()

    class Metadata:
        def __init__(self):
            self.fo = 0
            self.cvat = 0
            self.shape = 0
            self.reset = 1
            self.fo_root = ".fiftyone"

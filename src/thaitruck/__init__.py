"""ThaiTruck — spicy data blending, Thai food truck style."""

from thaitruck.fried_rice import fried_rice
from thaitruck.orange_chicken import orange_chicken
from thaitruck.larb import larb
from thaitruck.pad_thai import pad_thai
from thaitruck.sticky_rice import sticky_rice
from thaitruck.satay import satay
from thaitruck.tom_kha import tom_kha
from thaitruck.massaman import massaman
from thaitruck.nam_pla import nam_pla
from thaitruck.pipeline import TruckPipeline
from thaitruck.exceptions import (
    ThaiTruckError,
    DateColumnNotFound,
    InvalidHeatLevel,
    SkewTypeError,
    ValidationError,
)
from thaitruck import accessor  # noqa: F401  registers the `.truck` DataFrame accessor

__version__ = "0.2.2"

__all__ = [
    "fried_rice",
    "orange_chicken",
    "larb",
    "pad_thai",
    "sticky_rice",
    "satay",
    "tom_kha",
    "massaman",
    "nam_pla",
    "TruckPipeline",
    "ThaiTruckError",
    "DateColumnNotFound",
    "InvalidHeatLevel",
    "SkewTypeError",
    "ValidationError",
]

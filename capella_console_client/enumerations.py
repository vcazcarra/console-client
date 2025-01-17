from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


class ProductType(str, BaseEnum):
    SLC = "SLC"
    GEO = "GEO"
    SICD = "SICD"
    GEC = "GEC"
    SIDD = "SIDD"
    CPHD = "CPHD"


class AssetType(str, BaseEnum):
    HH = "HH"
    VV = "VV"
    preview = "preview"
    raster = "raster"
    metadata = "metadata"
    thumbnail = "thumbnail"
    log = "log"
    profile = "profile"
    stats = "stats"
    stats_plots = "stats_plots"


class ProductClass(str, BaseEnum):
    standard = "standard"
    extended = "extended"
    custom = "custom"


class OrbitState(str, BaseEnum):
    ascending = "ascending"
    descending = "descending"


class ObservationDirection(str, BaseEnum):
    left = "left"
    right = "right"


class OrbitalPlane(str, BaseEnum):
    fortyfive = 45
    fiftythree = 53
    ninetyseven = 97


class InstrumentMode(str, BaseEnum):
    stripmap = "stripmap"
    spotlight = "spotlight"
    sliding_spotlight = "sliding_spotlight"

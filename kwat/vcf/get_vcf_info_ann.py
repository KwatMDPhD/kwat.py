from ._get_vcf_info import _get_vcf_info
from .ANN_KEYS import ANN_KEYS


def _get_vcf_info_ann(io, ke, n_an=None):

    an = _get_vcf_info(io, "ANN")

    if an is not None:

        ie = ANN_KEYS.index(ke)

        return [ans.split(sep="|")[ie] for ans in an.split(sep=",")[:n_an]]

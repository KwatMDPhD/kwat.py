def make_variant_dict_consistent(
    vd, an_=("effect", "impact", "gene_name"), fo_=("GT",)
):

    vd["ANN"] = {0: {an: vd.get(an) for an in an_}}

    vd["sample"] = {0: {fo: vd.get(fo) for fo in fo_}}

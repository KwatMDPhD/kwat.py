def get_vcf_genotype(re, al, gt):

    return [
        [re, *al.split(sep=",")][int(ie)] for ie in gt.replace("/", "|").split(sep="|")
    ]
